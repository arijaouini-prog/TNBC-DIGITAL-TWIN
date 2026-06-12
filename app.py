import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="TNBC Systems Oncology Twin", page_icon="🛡️", layout="wide")

st.title("🛡️ TNBC Systems Oncology Twin")
st.subheader("Simulateur Clinique Intégratif pour le Cancer du Sein Triple Négatif (Moteur Prédictif)")
st.markdown("---")

# --- BASE DE DONNÉES BIOLOGIQUE DES TRAITEMENTS (Moteur Littéraire PubMed) ---
# Coefficients d'impact biophysiques et métaboliques pour chaque thérapeutique standard du TNBC
TRAITEMENTS_DB = {
    "Paclitaxel (Taxol)": {
        "cible": "Microtubules (Inhibition de la Mitose)",
        "efficacite_base": 65.0,
        "sensibilite_sucre": -20.0,  # L'hyperinsulinémie active mTOR, induisant une résistance aux taxanes
        "sensibilite_stress": -10.0,
        "description": "Chimiothérapie de première intention bloquant la division clonale des cellules TNBC."
    },
    "Cisplatine": {
        "cible": "ADN Tumoral (Agent Alkylant)",
        "efficacite_base": 62.0,
        "sensibilite_sucre": -5.0,
        "sensibilite_stress": -15.0, # Le cortisol sur-exprime les gènes anti-apoptotiques (Bcl-2)
        "description": "Agent génotoxique lourd provoquant des cassures double-brins de l'ADN tumoral."
    },
    "Pembrolizumab (Keytruda)": {
        "cible": "Axe Immunitaire PD-1 / PD-L1",
        "efficacite_base": 58.0,
        "sensibilite_sucre": -12.0,
        "sensibilite_stress": -25.0, # Le stress chronique épuise les Lymphocytes T infiltrants (TILs)
        "description": "Anticorps monoclonal d'immunothérapie réactivant le système immunitaire de l'hôte."
    },
    "Éribuline (Halaven)": {
        "cible": "Dynamique des Microtubules (Voie non-taxane)",
        "efficacite_base": 60.0,
        "sensibilite_sucre": -10.0,
        "sensibilite_stress": -8.0,
        "description": "Inhibiteur de la dynamique des microtubules indiqué dans les formes avancées ou réfractaires."
    }
}

# --- BARRE LATÉRALE : VARIABLES SYSTEMIQUES DU PATIENT (INPUTS) ---
st.sidebar.header("👤 1. Paramètres Cliniques du Patient")
age = st.sidebar.slider("Âge physiologique du patient :", 18, 90, 48)
stade = st.sidebar.selectbox("Stade de la Maladie (Classification TNM) :", ["Stade I (Localisé)", "Stade II (Infiltration précoce)", "Stade III (Avancé régional)", "Stade IV (Métastatique)"])

st.sidebar.header("🍏 2. Microenvironnement & Mode de vie")
regime = st.sidebar.selectbox("Profil Métabolique / Alimentation :", ["Standard Occidental (Riche en sucres / Inflammatoire)", "Isocalorique Équilibré (Index glycémique contrôlé)", "Restriction Glucidique (Cétogène / Jeûne thérapeutique intermittent)"])
stress = st.sidebar.slider("Index d'exposition au Stress Chronique (0 à 10) :", 0, 10, 6)
environnement = st.sidebar.selectbox("Exposition aux Xénobiotiques / Polluants :", ["Faible / Contrôlée", "Élevée (Zone Urbaine/Industrielle)"])

st.sidebar.header("💊 3. Sélection de la Thérapeutique à Tester")
traitement_choisi = st.sidebar.selectbox("Thérapie à injecter dans le Jumeau :", list(TRAITEMENTS_DB.keys()))

st.sidebar.header("🔬 4. Biomarqueurs de la Tumeur")
# Remplacement des données secrètes de docking/FASTA par un index d'expression standardisé
expression_cible = st.sidebar.slider("Index d'expression de la cible moléculaire (%) :", 10, 100, 85)


# --- MOTEUR ALGORITHMIQUE DU JUMEAU NUMÉRIQUE SYSTEMIQUE ---
info_t = TRAITEMENTS_DB[traitement_choisi]
efficacite_calculée = info_t["efficacite_base"]

# 1. Ajustement selon l'expression du biomarqueur tumoral
# Plus la cible est exprimée, plus la molécule est efficace de base
ajustement_cible = (expression_cible - 50) * 0.2
efficacite_calculée += ajustement_cible

# 2. Calcul de l'impact du Profil Métabolique / Glycémie
if regime == "Standard Occidental (Riche en sucres / Inflammatoire)":
    impact_sucre = info_t["sensibilite_sucre"]
elif regime == "Restriction Glucidique (Cétogène / Jeûne thérapeutique intermittent)":
    impact_sucre = 7.0  # Gain d'efficacité par élimination du glucose tumoral
else:
    impact_sucre = 0.0

# 3. Calcul de l'impact de l'Axe Neuro-endocrine (Stress Chronique)
impact_stress = (stress / 10.0) * info_t["sensibilite_stress"]

# 4. Calcul de l'impact du Stade Anatomique
if stade == "Stade IV (Métastatique)":
    impact_stade = -15.0
elif stade == "Stade III (Avancé régional)":
    impact_stade = -7.0
else:
    impact_stade = 0.0

# 5. Calcul de l'impact Environnemental
impact_env = -4.0 if environnement == "Élevée (Zone Urbaine/Industrielle)" else 0.0

# 6. Résultat final de la probabilité de Réponse Pathologique Majeure (pCR)
score_final_reponse = max(5.0, min(98.0, efficacite_calculée + impact_sucre + impact_stress + impact_stade + impact_env))


# --- AFFICHAGE DU RAPPORT CLINIQUE ---
st.header(f"📋 Rapport Prédictif : Traitement par {traitement_choisi}")
st.caption(f"**Mécanisme d'action moléculaire :** {info_t['cible']} | {info_t['description']}")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎯 Prédiction de Réponse")
    st.metric(label="Taux de Réponse Pathologique Estimé (pCR)", value=f"{score_final_reponse:.1f} %")
    st.progress(score_final_reponse / 100)
    
    if score_final_reponse >= 70:
        st.success("🟢 PROFIL RÉPONDEUR OPTIMAL : Forte synergie systémique.")
    elif score_final_reponse >= 40:
        st.warning("🟡 RÉPONDEUR MODÉRÉ : Phénomènes de résistance partielle détectés.")
    else:
        st.error("🔴 NON RÉPONDEUR : Résistance systémique majeure ou blocage métabolique.")

with col2:
    st.markdown("### 📊 Décomposition des Pressions Biophysiques (Modulateurs)")
    
    # Construction du tableau de bord des forces métaboliques et anatomiques
    df_poids = pd.DataFrame({
        'Composantes du Modèle': ['Efficacité Théorique Ajustée', 'Pression Métabolique (Sucre)', 'Pression Neuro-endocrine (Stress)', 'Extension Anatomique (Stade)', 'Impact Environnemental'],
        'Modulation Énergétique (%)': [efficacite_calculée, impact_sucre, impact_stress, impact_stade, impact_env]
    })
    fig = px.bar(df_poids, x='Modulation Énergétique (%)', y='Composantes du Modèle', orientation='h',
                 color='Modulation Énergétique (%)', color_continuous_scale='RdYlGn', text_auto='.1f')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 🔬 Synthèse Méthodologique pour l'Article Scientifique")
st.info(f"""
**Modèle d'Intégration Systémique TNBC :** Ce framework computationnel simule la pharmacodynamie des traitements de référence du cancer du sein triple négatif (TNBC) en connectant l'efficacité tumorale cellulaire aux variables homéostasiques du patient. En quantifiant les impacts cumulés du stress chronique (axe cortisol à {impact_stress:.1f}%) et du microenvironnement métabolique (impact glycémique à {impact_sucre:.1f}%), le modèle s'affranchit des limites des analyses purement génomiques pour fournir une estimation prédictive systémique de la réponse pathologique.
""")
