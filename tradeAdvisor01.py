import json
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date
import pytz
import yfinance as yf

AUTH_FILE = "auth.json"

# ==========================================================
# CONFIGURATION
# ==========================================================

BUY_OR_SELL = False         # True = cherche BUY, False = cherche SELL
WARMUP       = 20           # barres minimum avant de scorer
REFRESH_SEC  = 60           # intervalle de rafraîchissement (secondes)

NY = pytz.timezone("America/New_York")
MARKET_OPEN  = (9, 30)      # heure NY
MARKET_CLOSE = (16, 0)

# ==========================================================
# AUTH / CREDITS
# ==========================================================

def load_auth():
    with open(AUTH_FILE, "r") as f:
        return json.load(f)

def save_auth(data):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f, indent=2)

def consume_credit(cost=1):
    """Déduit cost crédits du compte courant. Retourne False si solde insuffisant."""
    cle = st.session_state.get("user_key")
    if not cle:
        return False
    auth_data = load_auth()
    user = auth_data.get(cle, {})
    if user.get("solde", 0) < cost:
        return False
    user["solde"] -= cost
    user["last_use"] = datetime.now().isoformat()
    auth_data[cle] = user
    save_auth(auth_data)
    st.session_state.user_data = user
    return True

# ==========================================================
# LECTURE PARAMETRES (session_state ou sys.argv)
# ==========================================================

def get_params():
    """Retourne (symbol, buy_or_sell) depuis app_params ou valeurs par défaut."""
    symbol     = "TSLA"
    buy_or_sell = BUY_OR_SELL

    raw = st.session_state.get("app_params", "") or ""
    for token in raw.split():
        if "=" in token:
            k, v = token.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            if k == "symbol":
                symbol = v.upper()
            elif k == "side":
                buy_or_sell = v.upper() == "BUY"

    return symbol, buy_or_sell

# ==========================================================
# STATUT DU MARCHÉ
# ==========================================================

holidays = [ datetime(2025, 11, 27).date(),
             datetime(2025, 12, 25).date(),
             datetime(2026, 1, 1).date(),
             datetime(2026, 1, 19).date(),
             datetime(2026, 2, 16).date(),
             datetime(2026, 4, 3).date(),
             datetime(2026, 6, 19).date(),
             datetime(2026, 7, 3).date(),
             datetime(2026, 9, 7).date(),
             datetime(2026, 1, 19).date(),
             datetime(2026, 11, 26).date(),
             datetime(2026, 12, 25).date(),
             datetime(2027, 1, 1).date(),
           ]

def market_status():
    """Retourne ('open'|'before'|'after'|'weekend'|'holiday', heure NY)."""
    now_ny = datetime.now(NY)
    wd = now_ny.weekday()  # 0=lundi … 6=dimanche

    if wd >= 5:
        return "weekend", now_ny

    if now_ny.date() in holidays :
        return "holiday"

    h, m = now_ny.hour, now_ny.minute
    total = h * 60 + m
    open_min  = MARKET_OPEN[0]  * 60 + MARKET_OPEN[1]
    close_min = MARKET_CLOSE[0] * 60 + MARKET_CLOSE[1]

    if total < open_min:
        return "before", now_ny
    elif total >= close_min:
        return "after", now_ny
    else:
        return "open", now_ny

# ==========================================================
# TÉLÉCHARGEMENT DONNÉES 1 min (2 jours)
# ==========================================================

def fetch_data(symbol):
    df = yf.download(symbol, period="2d", interval="1m", progress=False, auto_adjust=True)
    if df.empty:
        return None
    # Aplatir colonnes multi-index si nécessaire
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(NY)
    # Garder uniquement heures de marché
    df = df.between_time(
        f"{MARKET_OPEN[0]:02d}:{MARKET_OPEN[1]:02d}",
        f"{MARKET_CLOSE[0]:02d}:{MARKET_CLOSE[1]:02d}"
    )
    return df

# ==========================================================
# SCORE BUY / SELL (adapté de etfAdvisor02)
# ==========================================================

def compute_score(df_slice, buy_or_sell):
    """Calcule le score sur les données minute passées."""
    # Resample en 1h pour les indicateurs
    df_hour = df_slice.resample("1h").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last"
    }).dropna()

    if len(df_hour) < 4:
        return 0

    current   = df_hour["Close"].iloc[-1]
    low_hour  = df_hour["Low"].min()
    high_hour = df_hour["High"].max()
    rng       = high_hour - low_hour

    score = 0

    # --- Position dans range (30 pts) ---
    if rng > 0:
        position = (current - low_hour) / rng
        score += (1 - position) * 30 if buy_or_sell else position * 30

    # --- SMA20 horaire (25 pts) ---
    if len(df_hour) >= 20:
        sma20    = df_hour["Close"].rolling(20).mean().iloc[-1]
        pct_sma  = ((current / sma20) - 1) * 100
        if buy_or_sell:
            if pct_sma <= -2:   score += 25
            elif pct_sma <= -1: score += 20
            elif pct_sma <= 0:  score += 15
            else:               score += 5
        else:
            if pct_sma >= 2:    score += 25
            elif pct_sma >= 1:  score += 20
            elif pct_sma >= 0:  score += 15
            else:               score += 5
    else:
        score += 10

    # --- Momentum 3h (20 pts) ---
    if len(df_hour) >= 4:
        price_3h = df_hour["Close"].iloc[-4]
        momentum = ((current / price_3h) - 1) * 100
        if buy_or_sell:
            if momentum <= -1:    score += 20
            elif momentum <= -0.5: score += 15
            elif momentum <= 0:   score += 10
        else:
            if momentum >= 1:     score += 20
            elif momentum >= 0.5: score += 15
            elif momentum >= 0:   score += 10
    else:
        score += 10

    return int(score)

# ==========================================================
# CONSTRUCTION DE L'AXE X "MINUTES DEPUIS OUVERTURE"
# ==========================================================

def build_x_axis(df):
    """
    Retourne une Series d'entiers : minutes écoulées depuis l'ouverture
    du jour courant (séance J). La séance J-1 est décalée négativement.
    """
    if df is None or df.empty:
        return pd.Series(dtype=int)

    today = df.index[-1].date()
    x = pd.Series(index=df.index, dtype=float)

    for ts in df.index:
        day  = ts.date()
        mins = ts.hour * 60 + ts.minute - (MARKET_OPEN[0] * 60 + MARKET_OPEN[1])
        if day == today:
            x[ts] = mins
        else:
            # séance précédente : offset négatif
            session_len = (MARKET_CLOSE[0] * 60 + MARKET_CLOSE[1]) - (MARKET_OPEN[0] * 60 + MARKET_OPEN[1])
            x[ts] = mins - session_len

    return x

# ==========================================================
# BACKTEST SUR LES DONNÉES TÉLÉCHARGÉES
# ==========================================================

def run_backtest(df, buy_or_sell, alert_score):
    """Retourne liste de (timestamp, price, score) pour chaque signal."""
    signals = []
    last_signal_day = None

    for i in range(WARMUP, len(df)):
        df_slice = df.iloc[:i]
        score    = compute_score(df_slice, buy_or_sell)

        if score >= alert_score:
            ts  = df.index[i]
            day = ts.date()
            if last_signal_day == day:
                continue          # 1 signal par jour max
            last_signal_day = day
            signals.append((ts, df["Close"].iloc[i], score))

    return signals

# ==========================================================
# GRAPHIQUE
# ==========================================================

def plot_chart(df, signals, x_axis, symbol, buy_or_sell):
    fig, ax = plt.subplots(figsize=(14, 5))

    # Tracer les deux séances avec l'axe X en "minutes depuis ouverture"
    # Séparateur entre les deux séances
    today = df.index[-1].date()
    mask_today = pd.Series([ts.date() == today for ts in df.index], index=df.index)
    mask_prev  = ~mask_today

    x_vals = x_axis.values
    closes  = df["Close"].values

    if mask_prev.any():
        ax.plot(x_axis[mask_prev], df["Close"][mask_prev],
                color="#aaaaaa", linewidth=1, label="J-1")
    if mask_today.any():
        ax.plot(x_axis[mask_today], df["Close"][mask_today],
                color="#1f77b4", linewidth=1.5, label="Aujourd'hui")

    # Signaux
    for ts, price, score in signals:
        x_pos = x_axis.get(ts, None)
        if x_pos is None:
            continue
        if buy_or_sell:
            ax.scatter(x_pos, price, marker="^", color="green", s=120, zorder=5,
                       label=f"BUY (score {score})")
        else:
            ax.scatter(x_pos, price, marker="v", color="red", s=120, zorder=5,
                       label=f"SELL (score {score})")

    ax.set_title(f"{symbol} — {'BUY' if buy_or_sell else 'SELL'} advisor")
    ax.set_xlabel("Minutes depuis ouverture (NY)")
    ax.set_ylabel("Prix ($)")
    ax.grid(True, alpha=0.3)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)

    # Légende sans doublons
    handles, labels = ax.get_legend_handles_labels()
    seen = {}
    for h, l in zip(handles, labels):
        if l not in seen:
            seen[l] = h
    ax.legend(seen.values(), seen.keys())

    plt.tight_layout()
    return fig

# ==========================================================
# MAIN STREAMLIT
# ==========================================================

def main():
    st.set_page_config(page_title="ETF Advisor", page_icon="📈", layout="wide")

    # --- Bouton retour ---
    if st.button("← Retour au menu"):
        st.session_state.page = "menu"
        st.switch_page("AuthManager.py")

    symbol, buy_or_sell = get_params()
    alert_score = 55 if not buy_or_sell else 40

    st.title(f"📈 ETF Advisor — {symbol}")
    st.caption(f"Mode : {'🟢 BUY' if buy_or_sell else '🔴 SELL'} | Score seuil : {alert_score} | Refresh : {REFRESH_SEC}s")

    # Placeholder pour mise à jour en place
    status_ph = st.empty()
    chart_ph  = st.empty()
    info_ph   = st.empty()

    # --- Vérification statut marché ---
    status, now_ny = market_status()

    status_messages = {
        "weekend": f"📅 Week-end — marché fermé ({now_ny.strftime('%A %d/%m %H:%M')} NY)",
        "holiday": f"🏖️ Jour férié — marché fermé ({now_ny.strftime('%d/%m %H:%M')} NY)",
        "before":  f"⏳ Avant ouverture — marché ouvre à 09:30 NY ({now_ny.strftime('%H:%M')} NY)",
        "after":   f"🔒 Marché fermé — clôture à 16:00 NY ({now_ny.strftime('%H:%M')} NY)",
    }

    if status != "open":
        status_ph.warning(status_messages[status])
        # On télécharge quand même pour afficher le dernier état connu
        with st.spinner("Chargement des dernières données..."):
            df = fetch_data(symbol)
        if df is not None and not df.empty:
            last_ts = df.index[-1].strftime("%Y-%m-%d %H:%M NY")
            info_ph.info(f"🕐 Dernière donnée reçue : {last_ts}")
            x_axis  = build_x_axis(df)
            signals = run_backtest(df, buy_or_sell, alert_score)
            fig = plot_chart(df, signals, x_axis, symbol, buy_or_sell)
            chart_ph.pyplot(fig)
            plt.close(fig)
        else:
            info_ph.warning("Aucune donnée disponible.")

        # Pause longue hors marché puis rerun
        time.sleep(REFRESH_SEC * 5)
        st.rerun()
        return

    # --- Marché ouvert : boucle live ---
    status_ph.success(f"✅ Marché ouvert ({now_ny.strftime('%H:%M')} NY)")

    with st.spinner("Téléchargement données yfinance..."):
        df = fetch_data(symbol)

    if df is None or df.empty:
        # Peut arriver en début de séance ou jour férié non détecté
        info_ph.warning("Aucune donnée — possible jour férié ou problème réseau.")
        time.sleep(REFRESH_SEC)
        st.rerun()
        return

    last_ts = df.index[-1].strftime("%Y-%m-%d %H:%M NY")
    info_ph.info(f"🕐 Dernière donnée reçue : {last_ts}")

    x_axis  = build_x_axis(df)
    signals = run_backtest(df, buy_or_sell, alert_score)

    # --- Consommation de crédits pour chaque signal ---
    # On mémorise les signaux déjà facturés dans la session
    if "billed_signals" not in st.session_state:
        st.session_state.billed_signals = set()

    for ts, price, score in signals:
        sig_key = str(ts)
        if sig_key not in st.session_state.billed_signals:
            ok = consume_credit(cost=1)
            if ok:
                st.session_state.billed_signals.add(sig_key)
                side = "BUY" if buy_or_sell else "SELL"
                st.toast(f"💳 1 crédit consommé — signal {side} @ {price:.2f} (score {score})")
            else:
                st.error("❌ Solde insuffisant pour facturer ce signal.")

    # --- Affichage solde ---
    solde = st.session_state.get("user_data", {}).get("solde", "?")
    st.sidebar.metric("💰 Solde", f"{solde} crédits")
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.switch_page("AuthManager.py")

    # --- Graphique ---
    fig = plot_chart(df, signals, x_axis, symbol, buy_or_sell)
    chart_ph.pyplot(fig)
    plt.close(fig)

    # --- Signaux détectés ---
    if signals:
        rows = [{"Heure": ts.strftime("%H:%M"), "Prix": f"{p:.2f}", "Score": s,
                 "Signal": "▲ BUY" if buy_or_sell else "▼ SELL"}
                for ts, p, s in signals]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("Aucun signal détecté pour l'instant.")

    # --- Attendre et relancer ---
    time.sleep(REFRESH_SEC)
    st.rerun()


if __name__ == "__main__":
    main()
