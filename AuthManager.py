import streamlit as st
import subprocess  # pour lancer un autre script
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def main(params=""):
    """Dashboard financier"""
    
    st.title("📊 Dashboard Financier")
    
    # Sidebar
    st.sidebar.header("Paramètres")
    period = "6mo"
    if "period=" in params:
        period = params.split("period=")[1].split()[0]
    days = {"1mo":30,"3mo":90,"6mo":180,"1y":365}.get(period, 180)
    st.sidebar.info(f"Période: {period}")
    st.sidebar.info(f"Jours: {days}")
    
    # Bouton pour lancer l'application test.py
    if st.button("🚀 Lancer l'application test"):
        # Méthode 1 : lancer un autre Streamlit en arrière-plan
        subprocess.Popen(["streamlit", "run", "test.py"])
        
        # Méthode 2 : utiliser st.experimental_rerun avec un flag session_state
##        st.session_state['switch_to_test'] = True
##        st.experimental_rerun()
    
    # Vérifier le flag pour switcher
    if st.session_state.get('switch_to_test', False):
        st.info("🔄 Redirection vers test.py...")
        # Ici on pourrait importer test.py comme module et lancer sa fonction main
        import test
        test.main()
        return  # stoppe le reste du dashboard actuel
    
    # --- Simulation de données ---
    np.random.seed(42)
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    returns = np.random.randn(days) * 0.02
    trend = 0.001
    prices = 100 * (1 + returns + trend).cumprod()
    
    df = pd.DataFrame({
        'Date': dates,
        'Prix': prices,
        'Volume': np.random.randint(1000, 10000, days)
    })
    df['MA20'] = df['Prix'].rolling(20).mean()
    df['MA50'] = df['Prix'].rolling(50).mean()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Graphique", "📊 Indicateurs", "📋 Données"])
    
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Prix'], mode='lines', name='Prix', line=dict(color='blue', width=2)))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], mode='lines', name='MM20', line=dict(color='orange', width=1, dash='dash')))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='MM50', line=dict(color='red', width=1, dash='dash')))
        fig.update_layout(title=f'Évolution du prix - {period}', xaxis_title='Date', yaxis_title='Prix (€)', height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            returns = (df['Prix'].iloc[-1] / df['Prix'].iloc[0] - 1) * 100
            st.metric("Rendement", f"{returns:.1f}%", delta=f"{returns:.1f}%")
            volatility = df['Prix'].pct_change().std() * np.sqrt(252) * 100
            st.metric("Volatilité", f"{volatility:.1f}%")
        with col2:
            st.metric("Plus haut", f"{df['Prix'].max():.2f} €")
            st.metric("Plus bas", f"{df['Prix'].min():.2f} €")
    
    with tab3:
        st.dataframe(df.tail(20).style.format({
            'Prix': '{:.2f} €',
            'Volume': '{:,.0f}',
            'MA20': '{:.2f} €',
            'MA50': '{:.2f} €'
        }), use_container_width=True)

if __name__ == "__main__":
    main()
