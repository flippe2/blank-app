import sys
import json
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
# LECTURE PARAMETRES
# ============================================
cle = None
params = ""

if streamlit_mode:
    # Récupération depuis le portail via session_state
    cle = st.session_state.get("user_key", None)
    params = st.session_state.get("app_params", "")
else:
    # Mode ligne de commande (inchangé)
    for i, arg in enumerate(sys.argv):
        if arg == "--key" and i + 1 < len(sys.argv):
            cle = sys.argv[i + 1]
        if arg == "--params" and i + 1 < len(sys.argv):
            params = sys.argv[i + 1]

# ============================================
# AFFICHAGE
# ============================================
if streamlit_mode:
    st.title("🧪 Test application")
    st.write("Clé reçue :", cle)
    st.write("Paramètres :", params)

    if st.button("← Retour au menu"):
        st.session_state.page = "menu"
        st.switch_page("AuthManager.py")
else:
    print("\n=== TEST APPLICATION ===")
    print("clé :", cle)
    print("params :", params)

# ============================================
# CHARGEMENT AUTH
# ============================================
with open(AUTH_FILE, "r") as f:
    auth_data = json.load(f)

if cle not in auth_data:
    msg = "❌ Clé invalide"
    if streamlit_mode:
        st.error(msg)
        st.stop()
    else:
        print(msg)
        sys.exit()

user = auth_data[cle]

# ============================================
# FACTURATION
# ============================================
app_name = "test.py"
found = False
for app in user["apps"]:
    if app["fichier"] == app_name:
        found = True
        cout = app["cout_par_utilisation"]
        if user["solde"] < cout:
            msg = f"❌ Solde insuffisant ({user['solde']})"
            if streamlit_mode:
                st.error(msg)
                st.stop()
            else:
                print(msg)
                sys.exit()
        user["solde"] -= cout
        user["last_use"] = datetime.now().isoformat()
        auth_data[cle] = user
        with open(AUTH_FILE, "w") as f:
            json.dump(auth_data, f, indent=2)
        msg = f"{cout} crédits consommés. Nouveau solde : {user['solde']}"
        if streamlit_mode:
            st.success(msg)
        else:
            print(msg)
        break

if not found:
    msg = "❌ Application non autorisée pour cet utilisateur"
    if streamlit_mode:
        st.error(msg)
        st.stop()
    else:
        print(msg)
        sys.exit()

# ============================================
# SIMULATION TRAITEMENT
# ============================================
if streamlit_mode:
    st.write("Traitement en cours...")
else:
    print("Traitement en cours...")

resultat = {
    "status": "OK",
    "params": params,
    "result": 42
}

# ============================================
# RESULTAT
# ============================================
if streamlit_mode:
    st.write("### Résultat")
    st.json(resultat)
else:
    print("\n--- RESULTAT ---")
    print(resultat)
    sys.exit(5)
