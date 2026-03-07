import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from symbolsdict import ind_global, ind_emergent, ind_commod, ind_macro, ind_sector
import mpl_interactions  # Nouvel import

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

# Options de zoom
st.sidebar.header("🔄 Contrôles du graphique")
zoom_active = st.sidebar.checkbox("Activer le zoom/pan", value=True)

# -------------------------
# Tracé du graphique avec zoom interactif
# -------------------------

fig, ax = plt.subplots(figsize=(12, 7))

def plot_categories(cat1, cat2):
    ax.clear()
    current_lines = []
    current_symbols = []

    if cat1 != "off":
        df1 = data[cat1]
        for col in df1.columns:
            line, = ax.plot(df1.index, df1[col], linewidth=2, picker=True)  # picker pour sélection
            current_lines.append(line)
            current_symbols.append(col)

    if cat2 != "off":
        df2 = data[cat2]
        for col in df2.columns:
            line, = ax.plot(df2.index, df2[col], linestyle="--", picker=True)
            current_lines.append(line)
            current_symbols.append(col)

    ax.axhline(100, color='gray', linestyle=':', alpha=0.5)
    ax.set_ylabel("normalized value (today=100)")
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.grid(True, alpha=0.3)

    # Affichage des labels
    y = 0.95
    for line, sym in zip(current_lines, current_symbols):
        color = line.get_color()
        ax.text(1.01, y, sym, transform=ax.transAxes, color=color, fontsize=9, va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        y -= 0.03
    
    # Active le zoom interactif
    if zoom_active:
        ax.set_title("✅ Zoom/Pan activé - Utilisez les boutons ci-dessous")
    else:
        ax.set_title("Cliquez sur 'Activer le zoom' dans la barre latérale")

# Boutons de contrôle du graphique
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Zoom avant"):
        st.session_state.zoom_level = st.session_state.get('zoom_level', 1) * 1.2
with col2:
    if st.button("🔎 Zoom arrière"):
        st.session_state.zoom_level = st.session_state.get('zoom_level', 1) / 1.2
with col3:
    if st.button("↔️ Réinitialiser"):
        st.session_state.zoom_level = 1
        st.session_state.pan_x = 0
with col4:
    if st.button("📊 Vue complète"):
        st.session_state.zoom_level = 1
        st.session_state.pan_x = 0

# Application du zoom
plot_categories(cat1, cat2)

if zoom_active:
    # Utilise la fonctionnalité native de matplotlib
    plt.rcParams['keymap.zoom'] = ['o']  # Personnalisation des touches
    plt.rcParams['keymap.pan'] = ['p']
    
    # Ajoute une légende interactive
    ax.legend().set_draggable(True)

st.pyplot(fig)

# Instructions
if zoom_active:
    st.info("""
    **🖱️ Instructions pour zoom/pan :**
    - Cliquez sur l'icône loupe 🔍 dans la fenêtre matplotlib
    - Ou utilisez les boutons ci-dessus
    - Maintenez clic droit pour déplacer (pan)
    - Molette pour zoomer
    """)
