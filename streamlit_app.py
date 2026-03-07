import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Principaux indices",
    page_icon="🔐",
    layout="centered"
)

# ============================================
# FICHIER DE PERSISTANCE
# ============================================
DB_FILE = "credits_db.txt"

def load_db():
    """Charge la base de données depuis le fichier"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            # Si fichier corrompu, on retourne la base par défaut
            return get_default_db()
    else:
        return get_default_db()

def save_db(db):
    """Sauvegarde la base de données dans le fichier"""
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def get_default_db():
    """Base de données par défaut"""
    return {
        "DEMO123": {"solde": 50, "proprietaire": "Demo User", "created": "2026-01-01"},
        "TEST456": {"solde": 30, "proprietaire": "Test User", "created": "2026-01-15"},
        "PREMIUM789": {"solde": 100, "proprietaire": "Premium User", "created": "2026-02-01"},
    }

# ============================================
# BASE DE DONNÉES AVEC PERSISTANCE
# ============================================
class GestionPoints:
    """Gestionnaire de points avec persistance fichier"""
    
    def __init__(self):
        # Charge la DB depuis le fichier au démarrage
        if "keys_db_loaded" not in st.session_state:
            st.session_state["keys_db"] = load_db()
            st.session_state["keys_db_loaded"] = True
    
    def _save(self):
        """Sauvegarde dans le fichier"""
        save_db(st.session_state["keys_db"])
    
    def verifier_cle(self, cle):
        return cle in st.session_state["keys_db"]
    
    def get_solde(self, cle):
        if self.verifier_cle(cle):
            return st.session_state["keys_db"][cle]["solde"]
        return 0
    
    def consommer(self, cle, points):
        if self.verifier_cle(cle) and self.get_solde(cle) >= points:
            st.session_state["keys_db"][cle]["solde"] -= points
            self._save()  # Sauvegarde immédiate
            return True
        return False
    
    def ajouter_points(self, cle, points):
        if self.verifier_cle(cle):
            st.session_state["keys_db"][cle]["solde"] += points
            self._save()  # Sauvegarde immédiate
    
    def ajouter_utilisateur(self, cle, proprietaire, points_initiaux=0):
        """Pour ajouter un nouvel utilisateur"""
        if cle not in st.session_state["keys_db"]:
            st.session_state["keys_db"][cle] = {
                "solde": points_initiaux,
                "proprietaire": proprietaire,
                "created": datetime.now().strftime("%Y-%m-%d")
            }
            self._save()
            return True
        return False

# ============================================
# INTERFACE DE CONNEXION
# ============================================
def page_connexion(gestion):
    """Page de login"""
    st.title("🔐 Principaux indices")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Connexion")
        cle = st.text_input("Clé d'accès", type="password", key="login_key")
        
        if st.button("Se connecter", use_container_width=True):
            if gestion.verifier_cle(cle):
                st.session_state["authenticated"] = True
                st.session_state["user_key"] = cle
                st.session_state["user_info"] = st.session_state["keys_db"][cle]
                st.rerun()
            else:
                st.error("❌ Clé invalide")

# ============================================
# APPLICATION PRINCIPALE
# ============================================
def page_application(gestion):
    """Application principale"""
    
    # Barre latérale
    with st.sidebar:
        st.header("👤 Utilisateur")
        st.write(f"**{st.session_state['user_info']['proprietaire']}**")
        st.metric("💰 Solde", f"{st.session_state['user_info']['solde']} points")
        
        st.markdown("---")
        st.subheader("Actions")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
        
        st.markdown("---")
        st.caption(f"Connecté avec : {st.session_state['user_key']}")
    
    # Contenu principal
    st.title("📊 Indices")
    st.markdown("Selectionnez les groupes")
    
    # Initialisation
    if "angle" not in st.session_state:
        st.session_state.angle = 0
    
    # Création du graphique
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + np.radians(st.session_state.angle))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, 'b-', linewidth=2, label=f'Déphasage: {st.session_state.angle}°')
    ax.plot(x, np.sin(x), 'r--', linewidth=1, alpha=0.5, label='Sinus original')
    ax.set_xlabel('x')
    ax.set_ylabel('sin(x)')
    ax.set_title('Sinus avec déphasage')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(-1.2, 1.2)
    
    st.pyplot(fig)
    
    # Contrôles
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 +30° (1 pt)", use_container_width=True):
            if gestion.consommer(st.session_state["user_key"], 1):
                st.session_state.angle += 30
                st.success("Rotation effectuée !")
                st.rerun()
            else:
                st.error("Solde insuffisant !")
    
    with col2:
        if st.button("🔄 +60° (2 pts)", use_container_width=True):
            if gestion.consommer(st.session_state["user_key"], 2):
                st.session_state.angle += 60
                st.success("Rotation effectuée !")
                st.rerun()
            else:
                st.error("Solde insuffisant !")
    
    with col3:
        st.info(f"Angle actuel : {st.session_state.angle}°")
    
    # Réinitialisation
    if st.button("Réinitialiser (gratuit)"):
        st.session_state.angle = 0
        st.rerun()

# ============================================
# ADMINISTRATION
# ============================================
def page_admin(gestion):
    """Interface d'administration"""
    st.title("⚙️ Administration")
    
    tab1, tab2, tab3 = st.tabs(["📋 Utilisateurs", "➕ Ajouter des points", "👤 Nouvel utilisateur"])
    
    with tab1:
        st.subheader("Liste des utilisateurs")
        data = []
        for cle, infos in st.session_state["keys_db"].items():
            data.append({
                "Clé": cle,
                "Propriétaire": infos["proprietaire"],
                "Solde": infos["solde"],
                "Création": infos["created"]
            })
        st.dataframe(data)
        
        # Afficher le chemin du fichier (pour debug)
        st.caption(f"💾 Données sauvegardées dans : {DB_FILE}")
    
    with tab2:
        st.subheader("Ajouter des points")
        col1, col2 = st.columns(2)
        with col1:
            cle_admin = st.selectbox("Sélectionner utilisateur", 
                                    list(st.session_state["keys_db"].keys()))
        with col2:
            points = st.number_input("Points à ajouter", min_value=1, max_value=1000, value=10)
        
        if st.button("Ajouter"):
            gestion.ajouter_points(cle_admin, points)
            st.success(f"{points} points ajoutés à {cle_admin}")
            st.rerun()
    
    with tab3:
        st.subheader("Créer un nouvel utilisateur")
        with st.form("new_user_form"):
            nouvelle_cle = st.text_input("Nouvelle clé")
            nouveau_nom = st.text_input("Nom du propriétaire")
            points_init = st.number_input("Points initiaux", min_value=0, value=50)
            
            if st.form_submit_button("Créer"):
                if nouvelle_cle and nouveau_nom:
                    if gestion.ajouter_utilisateur(nouvelle_cle, nouveau_nom, points_init):
                        st.success(f"Utilisateur {nouveau_nom} créé avec {points_init} points")
                        st.rerun()
                    else:
                        st.error("Cette clé existe déjà")
                else:
                    st.error("Veuillez remplir tous les champs")

# ============================================
# ROUTAGE PRINCIPAL
# ============================================
def main():
    """Fonction principale avec routage"""
    
    # Initialisation du gestionnaire
    gestion = GestionPoints()
    
    # Gestion des sessions
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["is_admin"] = False
    
    # Mode admin caché (ajouter ?admin=true à l'URL)
    params = st.query_params
    if "admin" in params and params["admin"] == "true":
        st.session_state["is_admin"] = True
    
    # Routage
    if st.session_state.get("is_admin", False):
        page_admin(gestion)
    elif not st.session_state["authenticated"]:
        page_connexion(gestion)
    else:
        page_application(gestion)
    
    # Footer
    st.markdown("---")
    st.caption("© 2026 - Philippe")

if __name__ == "__main__":
    main()
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import hashlib
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="App à points",
    page_icon="🔐",
    layout="centered"
)

# ============================================
# BASE DE DONNÉES SIMULÉE (à remplacer par une vraie BD)
# ============================================
class GestionPoints:
    """Gestionnaire de points - version simplifiée pour démo"""
    
    def __init__(self):
        # En production : utilisez SQLite, PostgreSQL, etc.
        if "keys_db" not in st.session_state:
            st.session_state["keys_db"] = {
                "DEMO123": {"solde": 50, "proprietaire": "Demo User", "created": "2026-01-01"},
                "TEST456": {"solde": 30, "proprietaire": "Test User", "created": "2026-01-15"},
                "PREMIUM789": {"solde": 100, "proprietaire": "Premium User", "created": "2026-02-01"},
            }
    
    def verifier_cle(self, cle):
        return cle in st.session_state["keys_db"]
    
    def get_solde(self, cle):
        if self.verifier_cle(cle):
            return st.session_state["keys_db"][cle]["solde"]
        return 0
    
    def consommer(self, cle, points):
        if self.verifier_cle(cle) and self.get_solde(cle) >= points:
            st.session_state["keys_db"][cle]["solde"] -= points
            return True
        return False
    
    def ajouter_points(self, cle, points):
        if self.verifier_cle(cle):
            st.session_state["keys_db"][cle]["solde"] += points

# ============================================
# INTERFACE DE CONNEXION
# ============================================
def page_connexion(gestion):
    """Page de login"""
    st.title("🔐 Application avec système de points")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Connexion")
        cle = st.text_input("Clé d'accès", type="password", key="login_key")
        
        if st.button("Se connecter", use_container_width=True):
            if gestion.verifier_cle(cle):
                st.session_state["authenticated"] = True
                st.session_state["user_key"] = cle
                st.session_state["user_info"] = st.session_state["keys_db"][cle]
                st.rerun()
            else:
                st.error("❌ Clé invalide")
    
    with col2:
        st.subheader("Clés de démo")
        st.info("Utilisez ces clés pour tester :")
        for k, v in st.session_state["keys_db"].items():
            st.write(f"• **{k}** : {v['proprietaire']} ({v['solde']} pts)")

# ============================================
# APPLICATION PRINCIPALE
# ============================================
def page_application(gestion):
    """Application principale avec le sinus"""
    
    # Barre latérale
    with st.sidebar:
        st.header("👤 Utilisateur")
        st.write(f"**{st.session_state['user_info']['proprietaire']}**")
        st.metric("💰 Solde", f"{st.session_state['user_info']['solde']} points")
        
        st.markdown("---")
        st.subheader("Actions")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
        
        st.markdown("---")
        st.caption(f"Connecté avec : {st.session_state['user_key']}")
    
    # Contenu principal
    st.title("📊 Visualisation de sinus")
    st.markdown("Déplacez la courbe en utilisant vos points")
    
    # Initialisation
    if "angle" not in st.session_state:
        st.session_state.angle = 0
    
    # Création du graphique
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x + np.radians(st.session_state.angle))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, 'b-', linewidth=2, label=f'Déphasage: {st.session_state.angle}°')
    ax.plot(x, np.sin(x), 'r--', linewidth=1, alpha=0.5, label='Sinus original')
    ax.set_xlabel('x')
    ax.set_ylabel('sin(x)')
    ax.set_title('Sinus avec déphasage')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(-1.2, 1.2)
    
    st.pyplot(fig)
    
    # Contrôles
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 +30° (1 pt)", use_container_width=True):
            if gestion.consommer(st.session_state["user_key"], 1):
                st.session_state.angle += 30
                st.success("Rotation effectuée !")
                st.rerun()
            else:
                st.error("Solde insuffisant !")
    
    with col2:
        if st.button("🔄 +60° (2 pts)", use_container_width=True):
            if gestion.consommer(st.session_state["user_key"], 2):
                st.session_state.angle += 60
                st.success("Rotation effectuée !")
                st.rerun()
            else:
                st.error("Solde insuffisant !")
    
    with col3:
        st.info(f"Angle actuel : {st.session_state.angle}°")
    
    # Réinitialisation
    if st.button("Réinitialiser (gratuit)"):
        st.session_state.angle = 0
        st.rerun()

# ============================================
# ADMINISTRATION (optionnel)
# ============================================
def page_admin(gestion):
    """Interface d'administration simple"""
    st.title("⚙️ Administration")
    
    tab1, tab2 = st.tabs(["📋 Utilisateurs", "➕ Ajouter des points"])
    
    with tab1:
        st.subheader("Liste des utilisateurs")
        data = []
        for cle, infos in st.session_state["keys_db"].items():
            data.append({
                "Clé": cle,
                "Propriétaire": infos["proprietaire"],
                "Solde": infos["solde"],
                "Création": infos["created"]
            })
        st.dataframe(data)
    
    with tab2:
        st.subheader("Ajouter des points")
        col1, col2 = st.columns(2)
        with col1:
            cle_admin = st.selectbox("Sélectionner utilisateur", 
                                    list(st.session_state["keys_db"].keys()))
        with col2:
            points = st.number_input("Points à ajouter", min_value=1, max_value=1000, value=10)
        
        if st.button("Ajouter"):
            gestion.ajouter_points(cle_admin, points)
            st.success(f"{points} points ajoutés à {cle_admin}")
            st.rerun()

# ============================================
# ROUTAGE PRINCIPAL
# ============================================
def main():
    """Fonction principale avec routage"""
    
    # Initialisation du gestionnaire
    gestion = GestionPoints()
    
    # Gestion des sessions
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["is_admin"] = False
    
    # Mode admin caché (pour démo)
    params = st.query_params
    if "admin" in params and params["admin"] == "true":
        st.session_state["is_admin"] = True
    
    # Routage
    if st.session_state.get("is_admin", False):
        page_admin(gestion)
    elif not st.session_state["authenticated"]:
        page_connexion(gestion)
    else:
        page_application(gestion)
    
    # Footer
    st.markdown("---")
    st.caption("© 2026 - Application de démonstration avec système de points")

if __name__ == "__main__":
    main()

