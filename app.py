import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="TNBC Oncology Twin Engine", page_icon="🏥", layout="wide")

st.title("🏥 TNBC Oncology Twin Engine")
st.subheader("Simulateur Clinique Holistique & Prédiction de Réponse à la Lectine")
st.markdown("---")

# --- BARRE LATÉRALE : ENTRÉE DES PARAMÈTRES DU PATIENT (INPUTS) ---
st.sidebar.header("👤 1. Profil Clinique du Patient")
age = st.sidebar.slider("Âge du patient :", 18, 90, 45)
stade = st.sidebar.selectbox("Stade du Cancer (TNBC) :", ["Stade I (Localisé)", "Stade II", "Stade III (Avancé)", "Stade IV (Métastatique)"])

st.sidebar.header("🍏 2. Mode de vie & Environnement")
regime = st.sidebar.selectbox("Régime Alimentaire :", ["Équilibré / Méditerranéen", "Riche en Sucres / Ultra-transformé", "Cétogène / Faible en glucides"])
stress = st.sidebar.slider("Niveau de Stress Chronique (Échelle de 0 à 10) :", 0, 10, 5)
environnement = st.sidebar.selectbox("Exposition Environnementale (Pollution/Perturbateurs) :", ["Faible", "Modérée", "Élevée (Zone Urbaine/Industrielle)"])

st.sidebar.header("🧬 3. Données Moléculaires & Docking")
score_hdock = st.sidebar.number_input("Score HDOCK de la Lectine sur l'EGFR du patient :", value=-263.0, step=1.0)
fasta_input = st.sidebar.text_area("Séquence FASTA de la cible du Patient (EGFR/MUC1) :", ">Patient_TNBC_EGFR\nMRPSGTAGAALLALLAALCPASRAEEKKVCQGTSNKLTQLGTFEDHFLSLQRMFNNCEVVLGNLEITYVQRNYDLSFLKTIQEVAGYVLIALNTVERIPENLQIIRGNMYYENSYALAVLSNYDANKTGLKELPMRNLQEILHGAVRFSNNPALCNVESIQWRDIVSSDFLSNMSMDFQNHLGSCQKCDPSCPNGSCWGAGEENCQKLTKIICAQQCSGRCRGKSPSDCCHNQCAAGCTGPRESDCLVCRKFRDEATC")

# --- MOTEUR MATHÉMATIQUE DU JUMEAU NUMÉRIQUE (ALGORITHME BIO-CLINIQUE) ---
# On initialise un score d'efficacité de base à partir du docking réel de l'utilisateur
score_base_efficacite = min(95, max(5, int((abs(score_hdock) / 320) * 100)))

# Application des facteurs d'impact cliniques (Modulateurs)
impact_stress = stress * -1.5 # Le stress diminue l'efficacité (immunodépression, résistance)
if regime == "Riche en Sucres / Ultra-transformé":
    impact_regime = -12.0 # Le sucre nourrit la prolifération tumorale TNBC
elif regime == "Cétogène / Faible en glucides":
    impact_regime = 5.0 # Ralentit le métabolisme tumoral
else:
    impact_regime = 0.0

if environnement == "Élevée (Zone Urbaine/Industrielle)":
    impact_env = -5.0
else:
    impact_env = 0.0

# Analyse de la séquence FASTA (Simulation : recherche de mutations de résistance connues)
# Si la séquence contient une mutation fictive par exemple à une position critique, on baisse le score
if "GTSNK" not in fasta_input: 
    impact_mutation = -20.0 # Mutation détectée dans l'interface de liaison
    statut_mutation = "Mutation détectée dans le domaine extracellulaire (Altération de l'épitope)"
else:
    impact_mutation = 0.0
    statut_mutation = "Aucune mutation délétère détectée sur la zone de contact"

# Calcul de la probabilité finale de réponse thérapeutique
probabilite_reponse = max(0, min(100, score_base_efficacite + impact_stress + impact_regime + impact_env + impact_mutation))

# --- INTERFACE DE SORTIE (RAPPORT DÉTAILLÉ) ---
st.header("📋 Rapport Médical Prédictif du Jumeau Numérique")
st.write(f"Ce rapport estime l'efficacité thérapeutique potentielle de la lectine de *Pistacia vera* pour ce profil patient spécifique.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📊 Index de Réponse")
    st.metric(label="Probabilité de Réponse Clinique", value=f"{probabilite_reponse:.1f} %")
    st.progress(probabilite_reponse / 100)
    
    # Statut global
    if probabilite_reponse >= 75:
        st.success("🟢 PROFIL RÉPONDEUR : Forte probabilité de succès thérapeutique.")
    elif probabilite_reponse >= 45:
        st.warning("🟡 RÉPONDEUR MODÉRÉ : Efficacité partielle prévisible. Ajustements requis.")
    else:
        st.error("🔴 NON RÉPONDEUR : Résistance systémique ou moléculaire élevée.")

with col2:
    st.markdown("### 🧬 Analyse des Facteurs d'Influence (Micro vs Macro)")
    
    # Création d'un graphique des impacts pour montrer au Dr Karim ce qui influence la note
    df_impacts = pd.DataFrame({
        'Facteurs': ['Affinité Moléculaire (Docking)', 'Impact Stress/Cortisol', 'Impact Régime Alimentaire', 'Impact Environnement', 'Génétique (Mutation FASTA)'],
        'Score d Impact': [score_base_efficacite, impact_stress, impact_regime, impact_env, impact_mutation]
    })
    fig = px.bar(df_impacts, x='Score d Impact', y='Facteurs', orientation='h', 
                 color='Score d Impact', color_continuous_scale='RdYlGn',
                 title="Poids de chaque variable sur la réponse tumorale")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 📝 Conclusions du Jumeau Numérique pour l'Oncologue & le Laboratoire")

# Génération automatique du texte du rapport selon la combinaison entrée
st.info(f"""
* **Analyse Génomique :** {statut_mutation}. Le score de docking de {score_hdock} kcal/mol démontre une liaison structurelle initiale solide.
* **Environnement & Mode de vie :** Le niveau de stress évalué à {stress}/10 engendre un environnement pro-inflammatoire systémique. Associé à un régime alimentaire de type *{regime}*, le microenvironnement tumoral présente un taux d'agressivité qui modifie la biodisponibilité de la lectine.
* **Recommandation Clinique Générale :** {'Il est fortement recommandé de coupler l\'administration de la lectine à une correction nutritionnelle et une gestion du stress pour maximiser le blocage des récepteurs membranaires.' if probabilite_reponse < 75 else 'Ce patient présente un profil métabolique et moléculaire idéal pour une réponse optimale à la lectine végétale.'}
""")
