"""
Gestionnaire d'authentification universel avec classe
La clé est stockée dans l'instance, plus besoin de la passer à chaque appel
"""

import json
from datetime import datetime

# ============================================
# FICHIER JSON DES AUTORISATIONS
# ============================================
AUTH_FILE = "auth.json"

def load_auth():
    """Charge le fichier auth.json (doit exister)"""
    with open(AUTH_FILE, 'r') as f:
        return json.load(f)

def save_auth(auth_data):
    """Sauvegarde le fichier auth.json"""
    with open(AUTH_FILE, 'w') as f:
        json.dump(auth_data, f, indent=2)

class AuthManager:
    """Gestionnaire d'authentification avec clé stockée dans l'instance"""
    
    def __init__(self, cle=None):
        """
        Initialise le gestionnaire avec une clé optionnelle
        Si clé fournie, vérifie qu'elle existe
        """
        self.cle = cle
        self.auth_data = load_auth()
        self.user_info = None
        
        if cle and cle in self.auth_data:
            self.user_info = self.auth_data[cle]
    
    def verifier_cle(self, cle):
        """Vérifie si une clé existe (sans modifier l'instance)"""
        return cle in self.auth_data
    
    def connecter(self, cle):
        """Connecte l'utilisateur avec sa clé"""
        if cle in self.auth_data:
            self.cle = cle
            self.user_info = self.auth_data[cle]
            return True
        return False
    
    def deconnecter(self):
        """Déconnecte l'utilisateur"""
        self.cle = None
        self.user_info = None
    
    def get_solde(self):
        """Retourne le solde de l'utilisateur connecté"""
        if self.cle and self.user_info:
            return self.user_info["solde"]
        return None
    
    def get_apps(self):
        """Retourne la liste des apps de l'utilisateur connecté"""
        if self.cle and self.user_info:
            return self.user_info["apps"]
        return []
    
    def consommer_credits(self, fichier_app):
        """
        Décompte des crédits pour l'utilisateur connecté
        Plus besoin de passer la clé en paramètre !
        """
        if not self.cle or not self.user_info:
            return False, "❌ Aucun utilisateur connecté"
        
        # Chercher l'app correspondante
        for app in self.user_info["apps"]:
            if app["fichier"] == fichier_app:
                cout = app["cout_par_utilisation"]
                
                if self.user_info["solde"] >= cout:
                    # Mise à jour du solde
                    self.user_info["solde"] -= cout
                    self.user_info["last_use"] = datetime.now().isoformat()
                    
                    # Mise à jour dans auth_data
                    self.auth_data[self.cle] = self.user_info
                    
                    # Sauvegarde
                    save_auth(self.auth_data)
                    
                    return True, f"✅ {cout} crédits consommés. Nouveau solde: {self.user_info['solde']}"
                else:
                    return False, f"❌ Solde insuffisant ({self.user_info['solde']} / {cout} requis)"
        
        return False, f"❌ Application '{fichier_app}' non trouvée"
    
    def ajouter_credits(self, montant):
        """Ajoute des crédits à l'utilisateur connecté"""
        if not self.cle or not self.user_info:
            return False, "❌ Aucun utilisateur connecté"
        
        self.user_info["solde"] += montant
        self.auth_data[self.cle] = self.user_info
        save_auth(self.auth_data)
        
        return True, f"✅ {montant} crédits ajoutés. Nouveau solde: {self.user_info['solde']}"

# ============================================
# VERSION STREAMLIT
# ============================================
try:
    import streamlit as st
    
    def streamlit_app():
        """Version Streamlit de l'application"""
        
        st.set_page_config(
            page_title="Portail d'applications",
            page_icon="🔐",
            layout="wide"
        )
        
        # Initialisation session
        if "auth_manager" not in st.session_state:
            st.session_state["auth_manager"] = AuthManager()
            st.session_state["in_app"] = False
        
        auth = st.session_state["auth_manager"]
        
        # Pages Streamlit
        def page_connexion():
            st.title("🔐 Portail d'applications")
            st.markdown("---")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Connexion")
                cle = st.text_input("Clé d'accès", type="password")
                
                if st.button("Se connecter", use_container_width=True):
                    if auth.connecter(cle):
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("❌ Clé invalide")
            
            with col2:
                st.info("""
                **🔑 Clés disponibles dans auth.json**
                """)
        
        def page_menu():
            with st.sidebar:
                st.header(f"👤 {auth.user_info['nom']}")
                st.metric("💰 Solde", f"{auth.get_solde()} crédits")
                
                st.markdown("---")
                if st.button("🚪 Déconnexion", use_container_width=True):
                    auth.deconnecter()
                    st.session_state["authenticated"] = False
                    st.rerun()
            
            st.title("📋 Applications disponibles")
            
            apps = auth.get_apps()
            
            for i, app in enumerate(apps):
                with st.container():
                    st.subheader(f"📊 {app['nom']}")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"Fichier: `{app['fichier']}`")
                        st.write(f"Paramètres fixes: `{app['params_fixes']}`")
                    with col2:
                        st.metric("Coût", f"{app['cout_par_utilisation']} crédits")
                    
                    user_params = st.text_input(
                        "Paramètres additionnels",
                        key=f"params_{i}",
                        placeholder="ex: period=3mo"
                    )
                    
                    full_params = app['params_fixes']
                    if user_params:
                        full_params += "&" + user_params
                    
                    if st.button(f"🚀 Lancer", key=f"launch_{i}"):
                        if auth.get_solde() >= app['cout_par_utilisation']:
                            st.session_state["in_app"] = True
                            st.session_state["current_app"] = app["fichier"]
                            st.session_state["app_params"] = full_params
                            st.rerun()
                        else:
                            st.error("Solde insuffisant")
                    
                    st.markdown("---")
        
        def run_app():
            st.title(f"📱 Exécution de {st.session_state['current_app']}")
            
            if st.button("🔙 Retour au menu"):
                st.session_state["in_app"] = False
                st.rerun()
            
            st.markdown("---")
            st.info(f"Paramètres: {st.session_state['app_params']}")
            st.markdown("---")
            
            # Simulation
            import time
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            # Consommation des crédits - PLUS BESOIN DE PASSER LA CLÉ !
            result, message = auth.consommer_credits(st.session_state["current_app"])
            
            if result:
                st.success(message)
            else:
                st.error(message)
        
        # Routage Streamlit
        if not auth.cle:
            page_connexion()
        elif st.session_state.get("in_app", False):
            run_app()
        else:
            page_menu()

except ImportError:
    # Mode console/local
    st = None
    print("ℹ️ Mode console détecté")

# ============================================
# VERSION CONSOLE
# ============================================
def console_app():
    """Version console de l'application"""
    
    auth = AuthManager()
    
    while True:
        print("\n" + "="*50)
        print("🔐 PORTAIL D'APPLICATIONS - CONSOLE")
        print("="*50)
        
        if not auth.cle:
            # Non connecté
            cle = input("\nEntrez votre clé (ou 'quit'): ").strip()
            
            if cle.lower() == 'quit':
                break
            
            if auth.connecter(cle):
                print(f"\n✅ Connecté - Bienvenue {auth.user_info['nom']}")
            else:
                print("❌ Clé invalide")
        else:
            # Connecté
            print(f"\n👤 Utilisateur: {auth.user_info['nom']}")
            print(f"💰 Solde: {auth.get_solde()} crédits")
            
            print("\n" + "-"*30)
            print("APPLICATIONS DISPONIBLES:")
            apps = auth.get_apps()
            for i, app in enumerate(apps, 1):
                print(f"{i}. {app['nom']} ({app['cout_par_utilisation']} crédits)")
            print("0. Déconnexion")
            
            choix = input("\nChoix: ").strip()
            
            if choix == '0':
                auth.deconnecter()
                print("👋 Déconnecté")
                continue
            
            try:
                idx = int(choix) - 1
                if 0 <= idx < len(apps):
                    app = apps[idx]
                    
                    print(f"\n📊 {app['nom']}")
                    print(f"Paramètres fixes: {app['params_fixes']}")
                    
                    params = input("Paramètres additionnels (Entrée pour aucun): ").strip()
                    
                    full_params = app['params_fixes']
                    if params:
                        full_params += "&" + params
                    
                    print(f"\n🚀 Lancement avec: {full_params}")
                    
                    if auth.get_solde() < app['cout_par_utilisation']:
                        print("❌ Solde insuffisant")
                        continue
                    
                    # Simulation
                    import time
                    print("Exécution en cours", end="")
                    for _ in range(10):
                        time.sleep(0.1)
                        print(".", end="", flush=True)
                    print(" OK")
                    
                    # Consommation - PLUS BESOIN DE PASSER LA CLÉ !
                    result, message = auth.consommer_credits(app['fichier'])
                    print(message)
                    
                else:
                    print("❌ Choix invalide")
            except ValueError:
                print("❌ Choix invalide")

# ============================================
# POINT D'ENTRÉE
# ============================================
if __name__ == "__main__":
    if st is not None:
        # Mode Streamlit
        streamlit_app()
    else:
        # Mode console
        console_app()
