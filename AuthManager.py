import json
import streamlit as st
from datetime import datetime

AUTH_FILE = "auth.json"

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
# INITIALISATION SESSION
# ============================================

def init_session_state():
    """Initialise les variables de session"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_key = None
        st.session_state.user_data = None
        st.session_state.page = "login"
        st.session_state.current_app = None
        st.session_state.app_params = None

# ============================================
# CSS PERSONNALISÉ
# ============================================

def apply_custom_css():
    st.markdown("""
        <style>
        div[data-testid="column"] {
            padding: 0 15px !important;
        }
        .stTextInput input {
            font-size: 1rem !important;
            padding: 0.6rem !important;
            border-radius: 8px !important;
        }
        .stButton button {
            font-size: 1rem !important;
            padding: 0.5rem !important;
            border-radius: 8px !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .element-container {
            margin-bottom: 1rem !important;
        }
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 1rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div[data-testid="metric-container"] label {
            color: rgba(255,255,255,0.9) !important;
            font-size: 0.9rem !important;
        }
        div[data-testid="metric-container"] div {
            color: white !important;
            font-size: 1.5rem !important;
            font-weight: bold !important;
        }
        hr {
            margin: 1rem 0 !important;
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================
# PAGE DE CONNEXION
# ============================================

def page_login():
    """Page de connexion"""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1 style='font-size: 3rem; margin-bottom: 1rem;'>🔐</h1>
                <h2 style='color: #667eea; margin-bottom: 2rem;'>Portail d'accès</h2>
            </div>
        """, unsafe_allow_html=True)

        auth_data = load_auth()
        cle = st.text_input("Clé d'accès", type="password", key="login_input", placeholder="Entrez votre clé...")

        if cle:
            if cle in auth_data:
                st.session_state.authenticated = True
                st.session_state.user_key = cle
                st.session_state.user_data = auth_data[cle]
                st.session_state.page = "menu"
                st.rerun()
            else:
                st.error("❌ Clé invalide")

# ============================================
# PAGE MENU DES APPLICATIONS
# ============================================

def page_menu():
    """Page du menu des applications"""

    auth_data = load_auth()
    user = st.session_state.user_data

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>👤</div>
                <h3 style='margin-bottom: 1rem;'>{user['nom']}</h3>
            </div>
        """, unsafe_allow_html=True)

        st.metric("💰 Solde disponible", f"{user['solde']} crédits")

        st.markdown("---")

        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_key = None
            st.session_state.user_data = None
            st.session_state.page = "login"
            st.rerun()

    # Contenu principal
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h1 style='color: #333;'>📋 Applications disponibles</h1>
            <p style='color: #666;'>Sélectionnez une application pour commencer</p>
        </div>
    """, unsafe_allow_html=True)

    apps = user["apps"]

    for i in range(0, len(apps), 2):
        cols = st.columns(2)

        for j in range(2):
            if i + j < len(apps):
                app = apps[i + j]

                with cols[j]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {app['nom']}")
                        with col2:
                            st.markdown(f"""
                                <div style='
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    padding: 0.5rem;
                                    border-radius: 20px;
                                    text-align: center;
                                    font-weight: bold;
                                '>
                                    {app['cout_par_utilisation']} 💰
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style='
                                background: #f5f5f5;
                                padding: 0.5rem;
                                border-radius: 8px;
                                margin: 0.5rem 0;
                                font-family: monospace;
                            '>
                                {app['params_fixes']}
                            </div>
                        """, unsafe_allow_html=True)

                        params_key = f"params_{i+j}_{st.session_state.user_key}"
                        user_params = st.text_input(
                            "Paramètres additionnels",
                            key=params_key,
                            placeholder="ex: period=3mo, format=pdf...",
                            label_visibility="collapsed"
                        )

                        btn_key = f"run_{i+j}_{st.session_state.user_key}"
                        if st.button(f"🚀 Lancer", key=btn_key, use_container_width=True):
                            full_params = app["params_fixes"]
                            if user_params:
                                full_params += " " + user_params

                            if user["solde"] >= app["cout_par_utilisation"]:
                                # Consommer les crédits
                                user["solde"] -= app["cout_par_utilisation"]
                                user["last_use"] = datetime.now().isoformat()
                                auth_data[st.session_state.user_key] = user
                                save_auth(auth_data)
                                st.session_state.user_data = user

                                # Passer les paramètres à test.py via session_state
                                st.session_state.current_app = app
                                st.session_state.app_params = full_params
                                st.session_state.page = "app"

                                # Basculer vers test.py
                                st.switch_page("test.py")
                            else:
                                st.error("❌ Solde insuffisant")

                        st.markdown("<hr>", unsafe_allow_html=True)

# ============================================
# ROUTAGE PRINCIPAL
# ============================================

def main():
    """Fonction principale avec routage"""

    st.set_page_config(
        page_title="Portail",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    init_session_state()
    apply_custom_css()

    if st.session_state.page == "login":
        page_login()
    elif st.session_state.page == "menu":
        page_menu()

# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()
