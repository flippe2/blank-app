import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from symbolsdict import ind_global, ind_emergent, ind_commod, ind_macro, ind_sector

# -------------------------
# Configuration de la page Streamlit
# -------------------------
st.set_page_config(
    page_title="Comparaison d'indices",
    page_icon="📈",
    layout="wide"
)

# -------------------------
# Paramètres
# -------------------------
folder = "data/"
PERIOD = "6mo"

categories = {
    "ind_global": ind_global,
    "ind_emergent": ind_emergent,
    "ind_commod": ind_commod,
    "ind_macro": ind_macro,
    "ind_sector": ind_sector
}

# Jours fériés (à ajuster selon votre pays/marché)
holidays = [ 
    dt.datetime(2025, 11, 27).date(),
    dt.datetime(2025, 12, 25).date(),
    dt.datetime(2026, 1, 1).date(),
    dt.datetime(2026, 1, 19).date(),
    dt.datetime(2026, 2, 16).date(),
    dt.datetime(2026, 4, 3).date(),
    dt.datetime(2026, 6, 19).date(),
    dt.datetime(2026, 7, 3).date(),
    dt.datetime(2026, 9, 7).date(),
    dt.datetime(2026, 11, 26).date(),
    dt.datetime(2026, 12, 25).date(),
    dt.datetime(2027, 1, 1).date(),
]

# -------------------------
# Fonctions utilitaires
# -------------------------
def get_last_business_day():
    """Retourne la dernière date de bourse (hier ou avant si week-end/jour férié)"""
    today = dt.datetime.now().date()
    last_bday = today - dt.timedelta(days=1)
    
    # Reculer jusqu'à trouver un jour ouvré
    while last_bday.weekday() >= 5 or last_bday in holidays:  # 5=samedi, 6=dimanche
        last_bday -= dt.timedelta(days=1)
    
    return last_bday

def needs_update(filepath, symbol):
    """
    Vérifie si le fichier a besoin d'être mis à jour
    Retourne (bool, raison)
    """
    # Si le fichier n'existe pas
    if not os.path.exists(filepath):
        return True, "fichier manquant"
    
    try:
        # Lire la dernière date du fichier existant
        df_existing = pd.read_csv(
            filepath,
            header=[0, 1],
            index_col=0,
            parse_dates=True
        )
        
        if len(df_existing) == 0:
            return True, "fichier vide"
        
        last_date_in_file = df_existing.index[-1].date()
        last_bday = get_last_business_day()
        
        # Si la dernière date du fichier est antérieure à la dernière séance
        if last_date_in_file < last_bday:
            return True, f"données obsolètes (dernier: {last_date_in_file}, dernière séance: {last_bday})"
        
        # Sinon, on est à jour
        return False, "à jour"
        
    except Exception as e:
        return True, f"erreur de lecture: {str(e)[:50]}"


# -------------------------
# Fonctions utilitaires (sans os)
# -------------------------
def get_last_business_day():
    """Retourne la dernière date de bourse"""
    today = dt.datetime.now().date()
    last_bday = today - dt.timedelta(days=1)
    
    while last_bday.weekday() >= 5 or last_bday in holidays:
        last_bday -= dt.timedelta(days=1)
    
    return last_bday

def read_csv_safe(filepath):
    """
    Tente de lire un CSV, retourne None si échec
    Pas de os.path.exists, on essaye directement
    """
    try:
        df = pd.read_csv(
            filepath,
            header=[0, 1],
            index_col=0,
            parse_dates=True
        )
        return df
    except:
        return None

# -------------------------
# Téléchargement intelligent (sans os)
# -------------------------
@st.cache_data(ttl=3600)
def load_data():
    """
    Charge les données avec try/except uniquement
    """
    data = {}
    
    total_assets = sum(len(assets) for assets in categories.values())
    progress_bar = st.progress(0, text="Vérification des données...")
    status_text = st.empty()
    
    asset_count = 0
    last_bday = get_last_business_day()
    
    for cat, assets in categories.items():
        cat_df = pd.DataFrame()
        
        for asset in assets:
            symbol = asset["symbol"]
            filepath = folder + symbol + ".csv"
            
            asset_count += 1
            progress_bar.progress(asset_count / total_assets)
            status_text.text(f"📊 Traitement de {symbol}...")
            
            # Étape 1 : Essayer de lire le fichier existant
            df = read_csv_safe(filepath)
            need_download = False
            
            if df is not None and len(df) > 0:
                # Fichier existe, vérifier la date
                last_date = df.index[-1].date()
                if last_date < last_bday:
                    need_download = True
                    status_text.text(f"📥 Mise à jour de {symbol} (dernier: {last_date})...")
            else:
                # Fichier inexistant ou illisible
                need_download = True
                status_text.text(f"📥 Téléchargement de {symbol}...")
            
            # Étape 2 : Télécharger si nécessaire
            if need_download:
                try:
                    df = yf.download(
                        symbol,
                        period=PERIOD,
                        auto_adjust=True,
                        progress=False
                    )
                    
                    if len(df) > 0:
                        # Sauvegarde (le dossier data/ doit exister)
                        try:
                            df.to_csv(filepath, index=True, date_format='%Y-%m-%d')
                        except:
                            # Si le dossier n'existe pas, on ignore la sauvegarde
                            pass
                except Exception as e:
                    st.warning(f"⚠️ Échec téléchargement {symbol}: {str(e)[:50]}")
                    continue
            
            # Étape 3 : Normalisation si on a des données
            if df is not None and len(df) > 0:
                try:
                    series = df["Close"]
                    norm = 100 * series / series.iloc[-1]
                    cat_df[symbol] = norm
                except:
                    pass
        
        if not cat_df.empty:
            data[cat] = cat_df
    
    progress_bar.empty()
    status_text.empty()
    
    # Catégorie summary
    summary_df = pd.DataFrame()
    for cat in data:
        mean_curve = data[cat].mean(axis=1)
        summary_df[cat] = mean_curve
    data["summary"] = summary_df
    
    return data
    
    # Nettoyage des indicateurs de progression
    progress_bar.empty()
    status_text.empty()
    
    # Catégorie summary (moyennes)
    summary_df = pd.DataFrame()
    for cat in data:
        mean_curve = data[cat].mean(axis=1)
        summary_df[cat] = mean_curve
    data["summary"] = summary_df
    
    # Résumé des mises à jour
    st.success(f"Données chargées - {len(data)-1} catégories disponibles")
    
    return data
    
    # Catégorie summary (moyennes)
    summary_df = pd.DataFrame()
    for cat in data:
        mean_curve = data[cat].mean(axis=1)
        summary_df[cat] = mean_curve
    data["summary"] = summary_df
    
    return data

# -------------------------
# Chargement effectif
# -------------------------
with st.spinner("Chargement des données..."):
    data = load_data()

# -------------------------
# Interface Streamlit
# -------------------------
st.title("Comparaison d'indices")
st.markdown("---")

# Organisation en colonnes pour les sélecteurs
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Catégorie principale")
    cat_names = ["off"] + [c for c in data.keys() if c != "summary"] + ["summary"]
    # On met "summary" à la fin pour que l'index 6 soit "summary" (comme dans l'original)
    cat1 = st.selectbox(
        "Choisissez la catégorie 1",
        cat_names,
        index=cat_names.index("summary") if "summary" in cat_names else 0,
        key="cat1"
    )

with col2:
    st.subheader("📉 Catégorie secondaire")
    cat2 = st.selectbox(
        "Choisissez la catégorie 2",
        cat_names,
        index=0,  # "off" par défaut
        key="cat2"
    )

# Options d'affichage
with st.expander("⚙️ Options d'affichage", expanded=False):
    show_grid = st.checkbox("Afficher la grille", value=True)
    show_hline = st.checkbox("Afficher la ligne à 100", value=True)
    legend_position = st.selectbox(
        "Position de la légende",
        ["top-right", "top-left", "bottom-right", "bottom-left", "none"],
        index=0
    )

# -------------------------
# Création du graphique Plotly
# -------------------------
fig = go.Figure()

# Couleurs pour les deux catégories (pour garder une distinction)
colors1 = px.colors.qualitative.Plotly
colors2 = px.colors.qualitative.Set2

# Tracé de la catégorie 1
if cat1 != "off" and cat1 in data:
    df1 = data[cat1]
    for i, col in enumerate(df1.columns):
        fig.add_trace(go.Scatter(
            x=df1.index,
            y=df1[col],
            mode='lines',
            name=col,
            line=dict(width=2, color=colors1[i % len(colors1)]),
            legendgroup="cat1",
            legendgrouptitle_text=f"📊 {cat1}",
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Valeur: %{y:.1f}<extra></extra>'
        ))

# Tracé de la catégorie 2
if cat2 != "off" and cat2 in data:
    df2 = data[cat2]
    for i, col in enumerate(df2.columns):
        fig.add_trace(go.Scatter(
            x=df2.index,
            y=df2[col],
            mode='lines',
            name=col,
            line=dict(dash='dash', width=2, color=colors2[i % len(colors2)]),
            legendgroup="cat2",
            legendgrouptitle_text=f"📉 {cat2}",
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Valeur: %{y:.1f}<extra></extra>'
        ))

# Ajout de la ligne horizontale à 100
if show_hline:
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        name="base 100"
    )

# Configuration du layout
fig.update_layout(
    title={
        'text': f"Évolution comparée - Base 100 (aujourd'hui)",
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Date",
    yaxis_title="Valeur normalisée (aujourd'hui = 100)",
    hovermode='x unified',
    height=700,
    template="plotly_white",
    showlegend=True,
    legend=dict(
        groupclick="toggleitem",
        orientation="v",
        yanchor="top",
        y=0.99,
        xanchor="left" if "left" in legend_position else "right",
        x=0.01 if "left" in legend_position else 0.99
    ),
    margin=dict(l=50, r=50, t=100, b=50)
)

# Configuration des axes Y (pour mettre à droite comme dans l'original)
fig.update_yaxes(
    tickformat=".0f",
    gridcolor="lightgray" if show_grid else None,
    zeroline=False,
    showline=True,
    linewidth=1,
    linecolor='black',
    mirror=True,
    side="right"  # Met les labels Y à droite
)

# Configuration des axes X
fig.update_xaxes(
    gridcolor="lightgray" if show_grid else None,
    showline=True,
    linewidth=1,
    linecolor='black',
    rangeslider_visible=False  # On utilise le zoom natif plutôt qu'un slider
)

# Ajout des boutons de zoom/réinitialisation
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            x=0.5,
            y=1.15,
            xanchor="center",
            buttons=list([
                dict(
                    label="🔄 Réinitialiser",
                    method="relayout",
                    args=[{"xaxis.range": None, "yaxis.range": None}]
                ),
                dict(
                    label="🔍 Zoom avant",
                    method="relayout",
                    args=[{"xaxis.range": [df1.index[int(len(df1)*0.25)], df1.index[int(len(df1)*0.75)]] 
                           if cat1 != "off" and not df1.empty else None}]
                )
            ])
        )
    ]
)

# -------------------------
# Affichage dans Streamlit
# -------------------------
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Statistiques et informations
# -------------------------
with st.expander("📊 Voir les statistiques", expanded=False):
    col1, col2 = st.columns(2)
    
    if cat1 != "off" and cat1 in data:
        with col1:
            st.subheader(f"📈 {cat1}")
            st.dataframe(
                data[cat1].tail(10).round(1),
                height=300,
                use_container_width=True
            )
    
    if cat2 != "off" and cat2 in data:
        with col2:
            st.subheader(f"📉 {cat2}")
            st.dataframe(
                data[cat2].tail(10).round(1),
                height=300,
                use_container_width=True
            )

# Footer avec les contrôles de zoom
st.markdown("---")
st.markdown("""
**🖱️ Instructions pour zoomer/pan :**
- **Zoom** : utilisez la molette ou sélectionnez une zone avec le clic gauche
- **Pan** : maintenez le clic droit et déplacez
- **Réinitialiser** : double-clic ou bouton "Réinitialiser" ci-dessus
- **Légende** : cliquez sur un élément pour isoler, double-cliquez pour afficher seulement celui-là
""")
