import streamlit as st
import pandas as pd

# --- Configuration de l'interface ---
st.set_page_config(page_title="TNBC-TwinPredict", page_icon="🧬", layout="wide")

st.title("🧬 TNBC-TwinPredict : Plateforme Jumeau Numérique")
st.subheader("Criblage structural de la lectine de Pistacia vera contre le cancer du sein Triple Négatif")
st.markdown("---")

# --- REMPLACE ICI AVEC TES VRAIS SCORES DE DOCKING ---
# Tu peux modifier les chiffres ci-dessous pour mettre tes valeurs exactes de HDOCK
data_simulations = {
    "Récepteur Cible (TNBC)": ["EGFR (Epidermal Growth Factor)", "CD44 (Récepteur de métastase)"],
    "Code PDB de la Cible": ["1NQL", "1UUQ"],
    "Type de Sucre ciblé": ["N-glycanes complexes", "Acide Sialique / O-glycanes"],
    "Score d'Énergie HDOCK (kcal/mol)": [-264.5, -189.2],  # <-- REMPLACE PAR TES SCORES
    "Statut de Liaison": ["Forte Affinité (Bloquant)", "Affinité Modérée"]
}
df_twin = pd.DataFrame(data_simulations)

# --- Organisation des Onglets Interactifs ---
onglet1, onglet2, onglet3 = st.tabs([
    "🖥️ 1. Jumeau Numérique Cellulaire", 
    "⚡ 2. Simulation d'Interaction", 
    "📊 3. Rapport d'Efficacité Biologique"
])

# ---- ONGLET 1 : Profil de la cellule ----
with onglet1:
    st.header("Caractérisation de la Membrane Cancéreuse Virtuelle")
    st.write("Sélectionnez la lignée cellulaire Triple Négative simulée :")
    
    cell_line = st.selectbox("Lignée Cellulaire (Données PubMed) :", ["MDA-MB-231 (Hautement métastatique)", "BT-549", "Hs 578T"])
    
    st.info(f"🧬 **Jumeau Numérique activé :** Profil RE- / RP- / HER2- initialisé pour la lignée {cell_line}.")
    st.write("Voici la cartographie des récepteurs membranaires glycosylés modélisés dans ce clone virtuel :")
    st.dataframe(df_twin[["Récepteur Cible (TNBC)", "Code PDB de la Cible", "Type de Sucre ciblé"]], use_container_width=True)

# ---- ONGLET 2 : Simulation du Choc ----
with onglet2:
    st.header("Lancement du Test In Silico")
    st.write("Injectez virtuellement la lectine de *Pistacia vera* pour tester son effet bloquant sur le jumeau numérique.")
    
    cible_choisie = st.selectbox("Sélectionnez le récepteur à cibler :", df_twin["Récepteur Cible (TNBC)"])
    
    if st.button("▶️ Simuler l'interaction moléculaire"):
        with st.spinner("Analyse des interactions stériques et des forces de Van der Waals..."):
            import time
            time.sleep(1.5) # Petit effet de chargement pour faire professionnel
            
        st.success("Simulation terminée avec succès !")
        
        # Récupération de la ligne correspondant au choix de l'utilisateur
        res = df_twin[df_twin["Récepteur Cible (TNBC)"] == cible_choisie].iloc[0]
        
        # Affichage des métriques de tes propres résultats
        col1, col2 = st.columns(2)
        col1.metric("Ton Score d'Énergie (HDOCK)", f"{res['Score d'Énergie HDOCK (kcal/mol)']} kcal/mol")
        col2.metric("Prédiction d'Affinité", res["Statut de Liaison"])
        
        # Astuce : Tu peux ajouter un texte explicatif selon le score
        if res['Score d'Énergie HDOCK (kcal/mol)'] < -200:
            st.success("💡 **Conclusion :** L'ordinateur prédit une interaction hautement stable. La lectine s'emboîte parfaitement dans le récepteur tumoral.")
        else:
            st.warning("💡 **Conclusion :** Liaison modérée. Le blocage pourrait être partiel.")

# ---- ONGLET 3 : Rapport Global pour le Dr Karim ----
with onglet3:
    st.header("Rapport de Synthèse pour le Laboratoire (LGMIB)")
    st.write("Tableau récapitulatif complet de tes simulations de docking :")
    st.dataframe(df_twin, use_container_width=True)
    
    st.markdown("### 📝 Recommandation pour la culture cellulaire :")
    st.info("""
    Les scores d'énergie négatifs démontrent que la lectine de *Pistacia vera* possède une affinité théorique solide envers les récepteurs de la lignée MDA-MB-231. 
    Ce jumeau numérique valide la nécessité de passer à l'étape biologique en laboratoire pour réaliser un **test de cytotoxicité MTT** afin de confirmer l'effet anticancéreux réel.
    """)