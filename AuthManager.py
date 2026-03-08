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
# VERSION STREAMLIT (corrigée)
# ============================================

def streamlit_interface(auth_data):
    """Interface Streamlit avec gestion d'état"""
    
    st.title("🔐 Portail d'applications")
    
    # Initialisation de l'état de session
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_key = None
        st.session_state.user_data = None
    
    # Écran de connexion
    if not st.session_state.authenticated:
        cle = st.text_input("Clé d'accès", type="password", key="login_input")
        
        if cle:  # Si une clé est entrée
            if cle in auth_data:
                st.session_state.authenticated = True
                st.session_state.user_key = cle
                st.session_state.user_data = auth_data[cle]
                st.rerun()  # Recharge l'interface
            else:
                st.error("❌ Clé invalide")
        return  # Sortie pour ne pas afficher le reste
    
    # Utilisateur connecté
    user = st.session_state.user_data
    
    # Sidebar avec infos utilisateur et déconnexion
    with st.sidebar:
        st.header(f"👤 {user['nom']}")
        st.metric("💰 Solde", f"{user['solde']} crédits")
        
        if st.button("🚪 Déconnexion", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_key = None
            st.session_state.user_data = None
            st.rerun()
    
    # Applications disponibles
    st.header("📋 Applications disponibles")
    
    apps = user["apps"]
    
    for i, app in enumerate(apps):
        with st.container():
            st.subheader(f"📊 {app['nom']}")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"Script: `{app['fichier']}`")
            
            with col2:
                st.metric("Coût", f"{app['cout_par_utilisation']} crédits")
            
            # Paramètres additionnels
            params_key = f"params_{i}_{st.session_state.user_key}"
            user_params = st.text_input(
                "Paramètres additionnels",
                key=params_key,
                placeholder="ex: period=3mo"
            )
            
            full_params = app["params_fixes"]
            if user_params:
                full_params += " " + user_params
            
            # Bouton de lancement
            btn_key = f"run_{i}_{st.session_state.user_key}"
            
            with col3:
                if st.button("🚀 Lancer", key=btn_key):
                    run_application(app, full_params, st.session_state.user_key, auth_data)
            
            st.markdown("---")

def run_application(app, full_params, user_key, auth_data):
    """Exécute une application et met à jour le solde"""
    
    cout = app["cout_par_utilisation"]
    user = auth_data[user_key]
    
    if user["solde"] < cout:
        st.error("❌ Solde insuffisant")
        return
    
    # Facturation
    user["solde"] -= cout
    user["last_use"] = datetime.now().isoformat()
    auth_data[user_key] = user
    save_auth(auth_data)
    
    # Mise à jour de l'état session
    st.session_state.user_data = user
    
    st.success(f"✅ {cout} crédits consommés. Nouveau solde: {user['solde']}")
    
    # Exécution du script
    try:
        cmd = [
            sys.executable,  # Utilise le même Python
            app["fichier"],
            "--key",
            user_key,
            "--params",
            full_params
        ]
        
        with st.spinner("Exécution en cours..."):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Timeout de 30 secondes
            )
        
        # Affichage des résultats
        st.write("### 📤 Résultat de l'exécution")
        
        if result.stdout:
            st.code(result.stdout, language="text")
        
        if result.stderr:
            st.error("### ⚠️ Erreurs")
            st.code(result.stderr, language="text")
        
        if result.returncode == 0:
            st.success("✅ Script terminé avec succès")
        else:
            st.warning(f"⚠️ Script terminé avec le code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        st.error("❌ Temps d'exécution dépassé (30s)")
    except FileNotFoundError:
        st.error(f"❌ Script '{app['fichier']}' introuvable")
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")

# ============================================
# VERSION CONSOLE (inchangée)
# ============================================

def console_interface(auth_data):
    """Interface console existante"""
    while True:
        print("\n🔐 PORTAIL D'APPLICATIONS\n")
        cle = input("Clé d'accès (ou 'quit'): ").strip()
        
        if cle.lower() == 'quit':
            break
            
        if cle not in auth_data:
            print("❌ Clé invalide")
            continue
        
        user = auth_data[cle]
        
        while True:
            print("\n" + "="*50)
            print(f"👤 {user['nom']} - 💰 {user['solde']} crédits")
            print("="*50)
            
            apps = user["apps"]
            
            print("\nApplications disponibles :")
            for i, app in enumerate(apps, 1):
                print(f"{i}. {app['nom']} ({app['cout_par_utilisation']} crédits)")
            print("0. Déconnexion")
            
            choix = input("\nChoix : ").strip()
            
            if choix == "0":
                print("👋 Déconnexion")
                break
            
            try:
                idx = int(choix) - 1
                if idx < 0 or idx >= len(apps):
                    print("❌ Choix invalide")
                    continue
            except ValueError:
                print("❌ Choix invalide")
                continue
            
            app = apps[idx]
            
            print(f"\n📊 {app['nom']}")
            print(f"Paramètres fixes: {app['params_fixes']}")
            
            params = input("Paramètres additionnels (Entrée pour aucun): ").strip()
            
            full_params = app["params_fixes"]
            if params:
                full_params += " " + params
            
            cout = app["cout_par_utilisation"]
            
            if user["solde"] < cout:
                print("❌ Solde insuffisant")
                continue
            
            # Facturation
            user["solde"] -= cout
            user["last_use"] = datetime.now().isoformat()
            auth_data[cle] = user
            save_auth(auth_data)
            
            print(f"✅ {cout} crédits consommés. Nouveau solde: {user['solde']}")
            
            # Vérification fichier
            import os
            if not os.path.exists(app["fichier"]):
                print(f"❌ Script '{app['fichier']}' introuvable")
                continue
            
            cmd = [
                sys.executable,
                app["fichier"],
                "--key",
                cle,
                "--params",
                full_params
            ]
            
            print(f"\n🚀 Exécution de: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                print("\n📤 Résultat:")
                print(result.stdout)
            
            if result.stderr:
                print("\n⚠️ Erreurs:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n✅ Succès")
            else:
                print(f"\n❌ Échec (code {result.returncode})")
            
            input("\nAppuyez sur Entrée pour continuer...")

# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()
