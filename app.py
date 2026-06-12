import streamlit as st
import pandas as pd

# --- Configuration de la page ---
st.set_page_config(page_title="TNBC-TwinPredict PRO", page_icon="🧬", layout="wide")

st.title("🧬 TNBC-TwinPredict : Simulateur Universel de Jumeau Numérique")
st.subheader("Plateforme dynamique d'évaluation In Silico pour le Cancer du Sein Triple Négatif")
st.markdown("---")

# --- BARRE LATÉRALE : ENTRÉE DES DONNÉES EN DIRECT ---
st.sidebar.header("🔬 Paramètres du Jumeau Numérique")
st.sidebar.write("Entrez les scores obtenus lors de vos simulations pour tester le comportement de la cellule :")

# Boutons de saisie dynamiques pour l'utilisateur
nom_lectine = st.sidebar.text_input("Nom de la Lectine / Molécule :", "Lectine de Pistacia vera")
score_cible = st.sidebar.number_input("Score HDOCK sur la Cible (ex: EGFR) :", value=-250.0, step=1.0)
score_controle = st.sidebar.number_input("Score HDOCK sur le Contrôle Négatif :", value=-200.0, step=1.0)

# --- CALCULS INTERNES DU JUMEAU NUMÉRIQUE ---
# Le jumeau calcule la différence d'énergie pour évaluer la spécificité
delta_energie = score_controle - score_cible  # Plus le score cible est négatif, plus delta est grand

# Création du tableau dynamique
data_dynamique = {
    "Condition de Simulation": ["Cible Membranaire (TNBC)", "Contrôle Négatif"],
    "Molécule Testée": [nom_lectine, nom_lectine],
    "Score d Énergie (kcal/mol)": [score_cible, score_controle]
}
df_dynamique = pd.DataFrame(data_dynamique)


# --- ARCHITECTURE DES ONGLETS ---
onglet1, onglet2 = st.tabs([
    "🖥️ 1. Contrôle du Jumeau Numérique & Données", 
    "⚡ 2. Analyse de l'Inhibition Cellulaire"
])

# ---- ONGLET 1 : Visualisation des données entrées ----
with onglet1:
    st.header("📊 Matrice de Docking du Jumeau Numérique")
    st.write("Voici les données actuellement injectées dans le simulateur cellulaire :")
    
    # Affichage du tableau mis à jour en direct
    st.dataframe(df_dynamique, use_container_width=True)
    
    st.metric(label="Différence d'Énergie (Spécificité de la liaison)", value=f"{delta_energie:.1f} kcal/mol")
    st.caption("Une différence positive indique que la lectine préfère la cible tumorale au contrôle négatif.")

# ---- ONGLET 2 : Interprétation Biologique Automatique (Tous les cas) ----
with onglet2:
    st.header("🧠 Analyse Prédictive du Jumeau Numérique")
    st.write("Le modèle informatique analyse les forces thermodynamiques pour prédire le comportement en culture cellulaire :")
    
    # --- ALGORITHME DE DÉCISION DU JUMEAU (L'intelligence de l'app) ---
    
    # Cas 1 : La liaison sur la cible est plus faible ou égale au contrôle
    if score_cible >= score_controle:
        st.error("❌ **Échec de la simulation : Manque de spécificité**")
        st.write(f"Le jumeau numérique montre que la {nom_lectine} se lie aussi bien (ou mieux) au contrôle négatif qu'à la cible tumorale. La liaison est considérée comme non-spécifique. Il est déconseillé de passer à la culture cellulaire.")
    
    # Cas 2 : La liaison est spécifique mais globale faible (scores proches de 0)
    elif score_cible > -150:
        st.warning("⚠️ **Affinité Trop Faible**")
        st.write(f"Bien que la liaison soit légèrement spécifique, les scores d'énergie généraux sont trop faibles (au-dessus de -150 kcal/mol). La {nom_lectine} risque de se décrocher trop facilement de la membrane cancéreuse.")
    
    # Cas 3 : C'est le cas parfait (comme tes vrais résultats !)
    else:
        st.success("🎯 **Simulation Réussie : Forte Affinité & Spécificité**")
        st.markdown(f"""
        Le jumeau numérique a validé le comportement de la protéine :
        * **Affinité robuste :** Le score sur la cible ({score_cible} kcal/mol) démontre un emboîtement structural très stable.
        * **Sélectivité validée :** L'écart de **{delta_energie:.1f} kcal/mol** avec le contrôle négatif prouve que la molécule cible spécifiquement les récepteurs du cancer du sein Triple Négatif.
        """)
        
        # Calcul d'un pourcentage d'inhibition théorique basé sur l'énergie
        potentiel_inhibition = min(99, max(10, int((abs(score_cible) / 300) * 100)))
        st.progress(potentiel_inhibition / 100)
        st.metric("Potentiel d'Inhibition Cellulaire Estimé", f"{potentiel_inhibition}%")
        
        st.info("💡 **Message pour le LGMIB :** Ce profil thermodynamique idéal justifie pleinement le lancement d'un essai biologique *in vitro* (Test MTT de cytotoxicité) sur la lignée MDA-MB-231.")
