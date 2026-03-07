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

