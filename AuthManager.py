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
# PROGRAMME
# ============================================

auth_data = load_auth()

while True:

    # ========================================
    # LOGIN
    # ========================================

    if streamlit_mode:
        st.title("🔐 Portail d'applications")
        cle = st.text_input("Clé d'accès", type="password")
        if not cle:
            st.stop()
    else:
        print("\n🔐 PORTAIL D'APPLICATIONS\n")
        cle = input("Clé d'accès : ")

    if cle not in auth_data:

        if streamlit_mode:
            st.error("❌ Clé invalide")
            st.stop()
        else:
            print("❌ Clé invalide")
            continue

    user = auth_data[cle]

    # ========================================
    # SESSION UTILISATEUR
    # ========================================

    while True:

        if streamlit_mode:
            st.write(f"### 👤 {user['nom']}")
            st.write(f"💰 Solde : {user['solde']} crédits")
        else:
            print("\n--------------------------------")
            print("Utilisateur :", user["nom"])
            print("Solde :", user["solde"], "crédits")

        apps = user["apps"]

        # ====================================
        # MENU
        # ====================================

        if streamlit_mode:

            for i, app in enumerate(apps):

                st.write(f"### {app['nom']}")
                st.write("Coût :", app["cout_par_utilisation"])

                params = st.text_input(
                    "Paramètres additionnels",
                    key=f"params_{i}"
                )

                if st.button("Lancer", key=f"run_{i}"):

                    full_params = app["params_fixes"]
                    if params:
                        full_params += " " + params

                    cout = app["cout_par_utilisation"]

                    if user["solde"] < cout:
                        st.error("❌ Solde insuffisant")
                        continue

                    # facturation
                    user["solde"] -= cout
                    user["last_use"] = datetime.now().isoformat()
                    auth_data[cle] = user
                    save_auth(auth_data)

                    st.success(f"{cout} crédits consommés")

                    try :
                        cmd = [
                            "python",
                            app["fichier"],
                            "--key",
                            cle,
                            "--params",
                            full_params
                        ]

                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True
                        )

                        st.write("### Résultat")
                        st.code(result.stdout)

                        if result.stderr:
                            st.error(result.stderr)

                    except :
                        st.error("❌ Application introuvable")
                        continue


            if st.button("🚪 Déconnexion"):
                break

            st.stop()

        else:

            print("\nApplications disponibles :\n")

            for i, app in enumerate(apps):
                print(f"{i+1}. {app['nom']} ({app['cout_par_utilisation']} crédits)")

            print("0. Déconnexion")

            choix = input("\nChoix : ")

            if choix == "0":
                print("Déconnexion\n")
                break

            try:
                idx = int(choix) - 1
            except:
                print("Choix invalide")
                continue

            if idx < 0 or idx >= len(apps):
                print("Choix invalide")
                continue

            app = apps[idx]

            params = input("Paramètres additionnels : ")

            full_params = app["params_fixes"]
            if params:
                full_params += " " + params

            cout = app["cout_par_utilisation"]

            if user["solde"] < cout:
                print("❌ Solde insuffisant")
                continue

            # facturation
            user["solde"] -= cout
            user["last_use"] = datetime.now().isoformat()
            auth_data[cle] = user
            save_auth(auth_data)

            print(f"{cout} crédits consommés")

            # vérification fichier
            import pathlib
            if not pathlib.Path(app["fichier"]).exists():
                print("❌ Application introuvable")
                continue

            cmd = [
                "python",
                app["fichier"],
                "--key",
                cle,
                "--params",
                full_params
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            print("\n--- RESULTAT ---\n")

            print(result.stdout)
            print("return code :", result.returncode)

            if result.stderr:
                print("\n--- ERREURS ---\n")
                print(result.stderr)
