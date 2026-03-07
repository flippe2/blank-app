
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from symbolsdict import ind_global, ind_emergent, ind_commod, ind_macro, ind_sector

# -------------------------
# Paramètres
# -------------------------

PERIOD = "6mo"
do_download = False
do_save = True
folder = "data/"

categories = {
    "ind_global": ind_global,
    "ind_emergent": ind_emergent,
    "ind_commod": ind_commod,
    "ind_macro": ind_macro,
    "ind_sector": ind_sector
}

# -------------------------
# Téléchargement/Chargement des données
# -------------------------

data = {}

for cat, assets in categories.items():
    cat_df = pd.DataFrame()
    for asset in assets:
        symbol = asset["symbol"]
        try:
            if do_download:
                df = yf.download(symbol, period=PERIOD, auto_adjust=True, progress=False)
                if do_save:
                    df.to_csv(folder + symbol + ".csv", index=True, date_format='%Y-%m-%d')
            else:
                df = pd.read_csv(folder + symbol + ".csv", header=[0, 1], index_col=0, parse_dates=True)

            if len(df) == 0:
                continue

            series = df["Close"]
            norm = 100 * series / series.iloc[-1]
            cat_df[symbol] = norm

        except Exception as e:
            st.warning(f"Erreur pour {symbol}: {e}")
            continue

    if not cat_df.empty:
        data[cat] = cat_df

# -------------------------
# Calcul de la catégorie "summary"
# -------------------------

summary_df = pd.DataFrame()
for cat in data:
    mean_curve = data[cat].mean(axis=1)
    summary_df[cat] = mean_curve
data["summary"] = summary_df

# -------------------------
# Interface Streamlit
# -------------------------

st.title("Comparaison de catégories d'actifs")

# Sélection des catégories via des dropdowns
cat_names = ["off"] + list(data.keys())
cat1 = st.selectbox("Catégorie 1", cat_names, index=6)  # "summary" par défaut
cat2 = st.selectbox("Catégorie 2", cat_names, index=0)  # "off" par défaut

# -------------------------
# Tracé du graphique
# -------------------------

fig, ax = plt.subplots(figsize=(12, 7))

def plot_categories(cat1, cat2):
    ax.clear()
    current_lines = []
    current_symbols = []

    if cat1 != "off":
        df1 = data[cat1]
        for col in df1.columns:
            line, = ax.plot(df1.index, df1[col], linewidth=2)
            current_lines.append(line)
            current_symbols.append(col)

    if cat2 != "off":
        df2 = data[cat2]
        for col in df2.columns:
            line, = ax.plot(df2.index, df2[col], linestyle="--")
            current_lines.append(line)
            current_symbols.append(col)

    ax.axhline(100)
    ax.set_ylabel("normalized value (today=100)")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.grid(True)

    # Affichage des labels
    y = 0.95
    for line, sym in zip(current_lines, current_symbols):
        color = line.get_color()
        ax.text(1.01, y, sym, transform=ax.transAxes, color=color, fontsize=9, va='center')
        y -= 0.03

plot_categories(cat1, cat2)
st.pyplot(fig)
