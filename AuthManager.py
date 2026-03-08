import json
import subprocess
import sys
from datetime import datetime

AUTH_FILE = "auth.json"

# ============================================
# DETECTION STREAMLIT
# ============================================

try:
    import streamlit as st
    streamlit_mode = True
except:
    streamlit_mode = False

# ============================================
# AUTH JSON
# ============================================

def load_auth():
    with open(AUTH_FILE, "r") as f:
        return json.load(f)

def save_auth(data):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============================================
# PROGRAMME PRINCIPAL
# ============================================

def main():
    auth_data = load_auth()
    
    if streamlit_mode:
        streamlit_interface(auth_data)
    else:
        console_interface(auth_data)

# ============================================
# VERSION STREAMLIT (compacte)
# ============================================

def streamlit_interface(auth_data):
    """Interface Streamlit compacte"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Portail d'applications",
        page_icon="🔐",
        layout="wide"
    )
    
    # CSS personnalisé pour réduire les tailles
    st.markdown("""
        <style>
        /* Réduire la taille des titres */
        .main .block-container h1 {
            font-size: 1.8rem !important;
            padding-top: 0.5rem !important;
        }
        .main .block-container h2 {
            font-size: 1.3rem !important;
        }
        .main .block-container h3 {
            font-size: 1.1rem !important;
        }
        /* Réduire l'espacement */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        /* Métriques plus petites */
        div[data-testid="metric-container"] {
            padding: 0.5rem !important;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.8rem !important;
        }
        div[data-testid="metric-container"] div {
            font-size: 1.2rem !important;
        }
        /* Boutons plus compacts */
        .stButton button {
            padding: 0.2rem 0.5rem !important;
            font-size: 0.9rem !important;
        }
        /* Réduire les marges */
        .stMarkdown {
            margin-bottom: 0.3rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Titre compact
    st.title("🔐 Portail")
    
    # Initialisation de l'état
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_key = None
        st.session_state.user_data = None
    
    # Écran de connexion
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            cle = st.text_input("Clé", type="password", key="login_input", label_visibility="collapsed")
            
            if cle:
                if cle in auth_data:
                    st.session_state.authenticated = True
                    st.session_state.user_key = cle
                    st.session_state.user_data = auth_data[cle]
                    st.rerun()
                else:
                    st.error("❌")
        return
    
    # Utilisateur connecté
    user = st.session_state.user_data
    
    # Sidebar compacte
    with st.sidebar:
        st.markdown(f"**{user['nom']}**")
        st.metric("💰", f"{user['solde']}")
        
        if st.button("🚪 Déconnexion", key="logout_btn", help="Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.user_key = None
            st.session_state.user_data = None
            st.rerun()
    
    # Applications en grille compacte
    apps = user["apps"]
    
    # 3 colonnes pour les apps
    cols = st.columns(4)
    
    for i, app in enumerate(apps):
        with cols[i % 3]:
            with st.container():
                # Nom et coût sur la même ligne
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{app['nom']}**")
                with col2:
                    st.markdown(f"coût `{app['cout_par_utilisation']}`")
                
                # Paramètres
                params_key = f"p_{i}_{st.session_state.user_key}"
                user_params = st.text_input(
                    "📝",
                    key=params_key,
                    placeholder=app['params_fixes'],
                    label_visibility="collapsed"
                )
                
                full_params = app["params_fixes"]
                if user_params:
                    full_params += " " + user_params
                
                # Bouton de lancement
                btn_key = f"r_{i}_{st.session_state.user_key}"
                if st.button("▶️", key=btn_key, use_container_width=True):
                    run_application(app, full_params, st.session_state.user_key, auth_data)
                
                st.markdown("---")  # Séparateur léger

def run_application(app, full_params, user_key, auth_data):
    """Exécute une application"""
    
    cout = app["cout_par_utilisation"]
    user = auth_data[user_key]
    
    if user["solde"] < cout:
        st.error("❌ Solde")
        return
    
    # Facturation
    user["solde"] -= cout
    user["last_use"] = datetime.now().isoformat()
    auth_data[user_key] = user
    save_auth(auth_data)
    
    # Mise à jour de l'état
    st.session_state.user_data = user
    
    # Message compact
    st.toast(f"✅ {cout} crédits")
    
    # Exécution
    try:
        cmd = [
            sys.executable,
            app["fichier"],
            "--key",
            user_key,
            "--params",
            full_params
        ]
        
        with st.spinner("..."):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        # Résultats dans un expander
        with st.expander("📊 Résultat", expanded=False):
            if result.stdout:
                st.code(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            if result.stderr:
                st.error(result.stderr[:200])
                
    except Exception as e:
        st.error(f"❌ {str(e)[:50]}")

# ============================================
# VERSION CONSOLE (inchangée)
# ============================================

def console_interface(auth_data):
    """Interface console existante"""
    while True:
        print("\n🔐 PORTAIL\n")
        cle = input("Clé (ou 'quit'): ").strip()
        
        if cle.lower() == 'quit':
            break
            
        if cle not in auth_data:
            print("❌")
            continue
        
        user = auth_data[cle]
        
        while True:
            print("\n" + "="*30)
            print(f"{user['nom']} - 💰 {user['solde']}")
            print("="*30)
            
            apps = user["apps"]
            
            print("\nApps:")
            for i, app in enumerate(apps, 1):
                print(f"{i}. {app['nom']} ({app['cout_par_utilisation']})")
            print("0. Exit")
            
            choix = input("\nChoix: ").strip()
            
            if choix == "0":
                break
            
            try:
                idx = int(choix) - 1
                if idx < 0 or idx >= len(apps):
                    print("❌")
                    continue
            except:
                print("❌")
                continue
            
            app = apps[idx]
            
            params = input("Params (Entrée pour aucun): ").strip()
            
            full_params = app["params_fixes"]
            if params:
                full_params += " " + params
            
            if user["solde"] < app["cout_par_utilisation"]:
                print("❌ Solde")
                continue
            
            # Facturation
            user["solde"] -= app["cout_par_utilisation"]
            user["last_use"] = datetime.now().isoformat()
            auth_data[cle] = user
            save_auth(auth_data)
            
            print(f"✅ {app['cout_par_utilisation']} crédits")
            
            import os
            if not os.path.exists(app["fichier"]):
                print("❌ Fichier")
                continue
            
            cmd = [
                sys.executable,
                app["fichier"],
                "--key",
                cle,
                "--params",
                full_params
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                print(result.stdout[:200])
            if result.stderr:
                print("⚠️", result.stderr[:100])

# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()
