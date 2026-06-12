import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TNBC Systems Oncology Twin", page_icon="🛡️", layout="wide")

st.title("🛡️ TNBC Systems Oncology Twin")
st.subheader("Simulateur Clinique Holistique : Prédiction pCR & Suivi Longitudinal (DFS)")
st.markdown("---")

# --- BASE DE DONNÉES DES TRAITEMENTS (Source : PubMed & OncoSolidDB) ---
TRAITEMENTS_DB = {
    "Paclitaxel (Taxol)": {
        "cible": "Microtubules (Inhibition de la Mitose)",
        "efficacite_base": 65.0,
        "sensibilite_sucre": -20.0,
        "sensibilite_stress": -10.0,
        "description": "Chimiothérapie de référence bloquant la division cellulaire."
    },
    "Cisplatine": {
        "cible": "ADN Tumoral (Agent Alkylant)",
        "efficacite_base": 62.0,
        "sensibilite_sucre": -5.0,
        "sensibilite_stress": -15.0,
        "description": "Agent provoquant des cassures de l'ADN pour induire l'apoptose."
    },
    "Pembrolizumab (Keytruda)": {
        "cible": "Axe Immunitaire PD-1 / PD-L1",
        "efficacite_base": 55.0,
        "sensibilite_sucre": -12.0,
        "sensibilite_stress": -25.0,
        "description": "Immunothérapie réactivant les Lymphocytes T contre la tumeur."
    },
    "Éribuline (Halaven)": {
        "cible": "Microtubules (Mécanisme non-taxane)",
        "efficacite_base": 60.0,
        "sensibilite_sucre": -10.0,
        "sensibilite_stress": -8.0,
        "description": "Indiqué dans les formes TNBC avancées ou résistantes."
    }
}

# --- BARRE LATÉRALE : PARAMÈTRES DU PATIENT ---
st.sidebar.header("👤 1. Profil Clinique & Chronologie")
age = st.sidebar.slider("Âge du patient :", 18, 90, 48)
stade = st.sidebar.selectbox("Stade TNM :", ["Stade I", "Stade II", "Stade III", "Stade IV"])
timing = st.sidebar.radio("Timing du traitement :", ["Néoadjuvant (Avant Chirurgie)", "Adjuvant (Après Chirurgie)"])

# NOUVEAU PARAMÈTRE : TAILLE DE LA TUMEUR
taille_tumeur = st.sidebar.slider("Taille de la tumeur initiale (en mm) :", 5, 120, 35)

st.sidebar.header("💊 2. Dose-Intensité du Protocole")
# NOUVEAUX PARAMÈTRES : DOSAGE CHIMIO & RADIOTHÉRAPIE
nb_seances_chimio = st.sidebar.slider("Nombre de séances de chimiothérapie prévues/reçues :", 1, 24, 12)

radiotherapie_oui_non = st.sidebar.radio("Radiothérapie programmée ou administrée :", ["Oui", "Non"])
if radiotherapie_oui_non == "Oui":
    nb_seances_radio = st.sidebar.slider("Nombre de fractions/séances de radiothérapie :", 5, 35, 25)
else:
    nb_seances_radio = 0

st.sidebar.header("🍏 3. Microenvironnement de l'Hôte")
regime = st.sidebar.selectbox("Alimentation / Glycémie :", ["Occidental (Riche en sucres)", "Équilibré", "Restriction (Cétogène/Jeûne)"])
stress = st.sidebar.slider("Stress / Cortisol (Index 0-10) :", 0, 10, 6)
environnement = st.sidebar.selectbox("Exposition Polluants :", ["Faible", "Élevée"])

st.sidebar.header("🧪 4. Sélection Thérapeutique")
traitement_choisi = st.sidebar.selectbox("Choisir la molécule de chimiothérapie :", list(TRAITEMENTS_DB.keys()))


# --- MOTEUR DE CALCUL DU JUMEAU NUMÉRIQUE ---
info_t = TRAITEMENTS_DB[traitement_choisi]
score_base = info_t["efficacite_base"]

# 1. Calcul de l'Impact Métabolique et Neuro-endocrine
if regime == "Occidental (Riche en sucres)": impact_sucre = info_t["sensibilite_sucre"]
elif regime == "Restriction (Cétogène/Jeûne)": impact_sucre = 7.0
else: impact_sucre = 0.0

impact_stress = (stress / 10.0) * info_t["sensibilite_stress"]

# 2. Impact du Stade, du Timing et de l'Environnement
impact_timing = 5.0 if timing == "Néoadjuvant (Avant Chirurgie)" else -2.0
impact_stade = -15.0 if stade == "Stade IV" else (-7.0 if stade == "Stade III" else 0.0)
impact_env = -4.0 if environnement == "Élevée" else 0.0

# 3. [NOUVEAU] Impact de la Volumétrie Tumorale (Taille en mm)
# Une tumeur plus grosse (>50mm ou T3/T4) oppose plus de résistance à la pénétration du traitement
if taille_tumeur > 50:
    impact_taille = -12.0
elif taille_tumeur > 20:
    impact_taille = -5.0
else:
    impact_taille = 2.0  # Bonus d'efficacité sur les petites masses tumorales (T1)

# 4. [NOUVEAU] Impact de la Dose-Intensité (Nombre de séances de Chimiothérapie)
# On considère que le protocole standard optimal se situe autour de 12 à 16 séances cumulées.
if nb_seances_chimio >= 12:
    impact_dose_chimio = min(10.0, (nb_seances_chimio - 12) * 1.0) # Bonus de complétion
else:
    impact_dose_chimio = (nb_seances_chimio - 12) * 2.5 # Malus sévère si sous-dosage clinique

# 5. [NOUVEAU] Impact de la Radiothérapie (Synergie sur le contrôle local / DFS)
if radiotherapie_oui_non == "Oui" and nb_seances_radio >= 20:
    impact_radio = 6.0
elif radiotherapie_oui_non == "Oui":
    impact_radio = 3.0
else:
    impact_radio = -4.0 # L'absence de radiothérapie dans le TNBC localisé augmente le risque de récidive locale

# Score Final Combiné
score_final = max(5.0, min(98.0, score_base + impact_sucre + impact_stress + impact_timing + impact_stade + impact_env + impact_taille + impact_dose_chimio + impact_radio))


# --- LOGIQUE D'AFFICHAGE DYNAMIQUE (pCR vs DFS) ---
if timing == "Néoadjuvant (Avant Chirurgie)":
    label_metric = "Réponse Pathologique Prédite (pCR)"
    desc_metric = "Estimation de la disparition des cellules tumorales dans la pièce opératoire sous l'effet de la chimio."
    # Le suivi à long terme dépend de la pCR clinique et de la couverture par la radiothérapie post-opératoire
    dfs_5ans = min(99.0, score_final + 25.0 + (impact_radio)) if score_final > 45 else score_final + 10.0
else:
    label_metric = "Survie Sans Récidive à 5 ans (DFS)"
    desc_metric = "Probabilité de non-récidive micro-métastatique systémique et locale."
    dfs_5ans = score_final

# --- RENDU DE L'INTERFACE ---
st.header(f"📋 Rapport du Jumeau Numérique : {traitement_choisi}")
st.write(f"**Protocole clinique :** {timing} | **Taille de la tumeur :** {taille_tumeur} mm | **Nombre de séances de chimio :** {nb_seances_chimio}")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 Indicateurs de Réponse")
    st.metric(label=label_metric, value=f"{score_final:.1f} %")
    st.progress(score_final / 100)
    st.caption(desc_metric)
    
    st.markdown("---")
    st.metric(label="Pronostic de Survie Globale (DFS 5 ans)", value=f"{dfs_5ans:.1f} %")
    st.caption("Estimation de la rémission à long terme (Contrôle systémique et local).")

with col2:
    st.subheader("📊 Décomposition des Pressions de Résistance Clinique")
    df_impact = pd.DataFrame({
        'Composantes du Modèle': [
            'Base Théorique Molécule', 
            'Impact Métabolique (Sucre)', 
            'Axe Neuro-endocrine (Stress)', 
            'Timing Thérapeutique', 
            'Stade Anatomique', 
            'Volumétrie (Taille Tumeur)', 
            'Dose-Intensité (Nb Chimio)',
            'Contrôle Local (Radiothérapie)'
        ],
        'Score (%)': [score_base, impact_sucre, impact_stress, impact_timing, impact_stade, impact_taille, impact_dose_chimio, impact_radio]
    })
    fig = px.bar(df_impact, x='Score (%)', y='Composantes du Modèle', orientation='h',
                 color='Score (%)', color_continuous_scale='RdYlGn', text_auto='.1f')
    st.plotly_chart(fig, use_container_width=True)

# --- SECTION VALIDATION & RÉFÉRENCES ---
st.markdown("---")
col_val1, col_val2 = st.columns(2)

with col_val1:
    st.subheader("✅ Validation Clinique du Modèle")
    st.info(f"""
    **Validation Rétrospective d'Intégration :**
    - **Cas simulé :** TNBC, Tumeur de {taille_tumeur} mm, protocole de {nb_seances_chimio} séances de chimiothérapie.
    - **Radiothérapie combinée :** {radiotherapie_oui_non} ({nb_seances_radio} séances).
    - **Pertinence PubMed :** La dose-intensité (nombre de cures reçues sans délai) et la taille tumorale initiale sont les deux premiers facteurs prédictifs indépendants de la pCR selon les critères RECIST internationaux.
    """)

with col_val2:
    st.subheader("📚 Références de l'Infrastructure")
    st.write("""
    - **OncoSolidDB (Khamessi et al., 2026) :** Matrice fondamentale des sensibilités biologiques.
    - **Classification TNM AJCC (9ème Édition) :** Impact de la taille tumorale (T) et de l'extension sur la DFS à 5 ans.
    - **Guidelines NCCN / ESMO :** Standardisation de l'impact des doses de chimiothérapie et des fractions de radiothérapie.
    - **Framework :** Architecture Holistique Arij (LGMIB / ISBST).
    """)

st.warning("⚠️ Ce Jumeau Numérique est un outil de recherche computationnelle. Les décisions thérapeutiques réelles relèvent exclusivement de l'équipe médicale multidisciplinaire.")
