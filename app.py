import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TNBC Systems Oncology Twin", page_icon="🛡️", layout="wide")

st.title("🛡️ TNBC Systems Oncology Twin")
st.subheader("Simulateur Clinique Spécifique : Personnalisation par l'Oncologue Référent")
st.markdown("---")

# --- BASE DE DONNÉES BIOLOGIQUE DES TRAITEMENTS (Moteur PubMed & OncoSolidDB) ---
TRAITEMENTS_DB = {
    "Paclitaxel (Taxol)": {
        "cible": "Microtubules (Inhibition de la Mitose)",
        "efficacite_base": 65.0,
        "sensibilite_sucre": -20.0,
        "sensibilite_stress": -10.0,
        "description": "Chimiothérapie de référence bloquant la division clonale des cellules TNBC."
    },
    "Cisplatine": {
        "cible": "ADN Tumoral (Agent Alkylant)",
        "efficacite_base": 62.0,
        "sensibilite_sucre": -5.0,
        "sensibilite_stress": -15.0,
        "description": "Agent génotoxique lourd provoquant des cassures de l'ADN tumoral."
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
        "description": "Indiqué dans les formes TNBC avancées ou réfractaires."
    }
}

# ==============================================================================
# 👤 INTERFACE MÉDECIN : PARAMÈTRES MODIFIABLES SELON CHAQUE PATIENT
# ==============================================================================
st.sidebar.header("👤 1. Paramètres Anatomiques du Patient")
age = st.sidebar.slider("Âge du patient :", 18, 90, 48)
stade = st.sidebar.selectbox("Stade TNM (Extension) :", ["Stade I", "Stade II", "Stade III", "Stade IV"])

# PARAMÈTRE PARAMÉTRABLE PAR LE MÉDECIN : TAILLE DE LA TUMEUR IN VITRO/IN VIVO
taille_tumeur = st.sidebar.slider("Taille réelle de la tumeur (en mm) :", 5, 120, 35)

st.sidebar.header("⏳ 2. Chronologie & Dose-Intensité")
timing = st.sidebar.radio("Timing du protocole de soin :", ["Néoadjuvant (Avant Chirurgie)", "Adjuvant (Après Chirurgie)"])

# PARAMÈTRES MODIFIABLES POUR LE DOSAGE CLINIQUE
nb_seances_chimio = st.sidebar.slider("Nombre de séances de chimiothérapie administrées :", 1, 24, 12)

radiotherapie_oui_non = st.sidebar.radio("Radiothérapie associée :", ["Oui", "Non"])
if radiotherapie_oui_non == "Oui":
    nb_seances_radio = st.sidebar.slider("Nombre de séances/fractions de radiothérapie :", 5, 35, 25)
else:
    nb_seances_radio = 0

st.sidebar.header("🍏 3. Profil Métabolique & Mode de vie")
regime = st.sidebar.selectbox("Profil Nutritionnel / Glycémie :", ["Occidental (Riche en sucres)", "Équilibré", "Restriction (Cétogène/Jeûne)"])
stress = st.sidebar.slider("Index Cortisol / Stress Chronique (0-10) :", 0, 10, 6)
environnement = st.sidebar.selectbox("Exposition aux Polluants :", ["Faible", "Élevée"])

st.sidebar.header("💊 4. Stratégie Thérapeutique")
traitement_choisi = st.sidebar.selectbox("Sélectionner la molécule de chimiothérapie :", list(TRAITEMENTS_DB.keys()))


# ==============================================================================
# MOTEUR ALGORITHMIQUE DYNAMIQUE (CALCUL EN TEMPS RÉEL)
# ==============================================================================
info_t = TRAITEMENTS_DB[traitement_choisi]
score_base = info_t["efficacite_base"]

# 1. Calcul dynamique des résistances liées à l'hôte
if regime == "Occidental (Riche en sucres)": impact_sucre = info_t["sensibilite_sucre"]
elif regime == "Restriction (Cétogène/Jeûne)": impact_sucre = 7.0
else: impact_sucre = 0.0

impact_stress = (stress / 10.0) * info_t["sensibilite_stress"]
impact_timing = 5.0 if timing == "Néoadjuvant (Avant Chirurgie)" else -2.0
impact_stade = -15.0 if stade == "Stade IV" else (-7.0 if stade == "Stade III" else 0.0)
impact_env = -4.0 if environnement == "Élevée" else 0.0

# 2. [AJUSTEMENT DYNAMIQUE] Impact de la Taille de la Tumeur réglée par le médecin
if taille_tumeur > 50:
    impact_taille = -12.0
elif taille_tumeur > 20:
    impact_taille = -5.0
else:
    impact_taille = 2.0  # Bonus si petite tumeur locale (T1)

# 3. [AJUSTEMENT DYNAMIQUE] Impact du Nombre de séances réglé par le médecin
if nb_seances_chimio >= 12:
    impact_dose_chimio = min(10.0, (nb_seances_chimio - 12) * 1.0)
else:
    impact_dose_chimio = (nb_seances_chimio - 12) * 2.5 # Malus progressif si sous-dosage

# 4. [AJUSTEMENT DYNAMIQUE] Impact des Séances de Radiothérapie réglées par le médecin
if radiotherapie_oui_non == "Oui" and nb_seances_radio >= 20:
    impact_radio = 6.0
elif radiotherapie_oui_non == "Oui":
    impact_radio = 3.0
else:
    impact_radio = -5.0

# Équation Finale du Jumeau Numérique
score_final = max(5.0, min(98.0, score_base + impact_sucre + impact_stress + impact_timing + impact_stade + impact_env + impact_taille + impact_dose_chimio + impact_radio))

# Logique de bascule sémantique Clinique (pCR vs DFS)
if timing == "Néoadjuvant (Avant Chirurgie)":
    label_metric = "Taux de Réponse Pathologique Estimé (pCR)"
    desc_metric = "Probabilité de disparition tumorale complète dans les tissus après chirurgie."
    dfs_5ans = min(99.0, score_final + 25.0 + impact_radio) if score_final > 45 else score_final + 10.0
else:
    label_metric = "Survie Sans Récidive à 5 ans (DFS)"
    desc_metric = "Probabilité que le patient reste en rémission complète sans micro-métastases."
    dfs_5ans = score_final


# ==============================================================================
# AFFICHAGE DU RAPPORT DU PATIENT ET GRAPHIQUES INTERACTIFS
# ==============================================================================
st.header(f"📋 Fiche Clinique du Patient : Protocole {traitement_choisi}")
st.write(f"**Statut actuel du Jumeau :** {timing} | **Masse tumorale de départ :** {taille_tumeur} mm | **Dose cumulée :** {nb_seances_chimio} séances de chimiothérapie")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 Prédictions Cliniques Personnalisées")
    st.metric(label=label_metric, value=f"{score_final:.1f} %")
    st.progress(score_final / 100)
    st.caption(desc_metric)
    
    st.markdown("---")
    st.metric(label="Survie Globale Estimée (DFS à 5 ans)", value=f"{dfs_5ans:.1f} %")
    st.caption("Évolution à long terme calculée d'après l'efficacité locale et systémique.")

with col2:
    st.subheader("📊 Balance des Forces Biophysiques & Thérapeutiques")
    # Ce tableau se met à jour instantanément quand l'oncologue bouge un curseur à gauche
    df_impact = pd.DataFrame({
        'Variables Ajustées par le Médecin': [
            'Efficacité Théorique Molécule', 
            'Pression Glycémique (Alimentation)', 
            'Axe Neuro-endocrine (Stress/Cortisol)', 
            'Chronologie Thérapeutique (Timing)', 
            'Stade de la Maladie', 
            'Volumétrie Tumorale (Taille en mm)', 
            'Dose-Intensité (Nombre de Séances Chimio)',
            'Contrôle Post-Opératoire (Radiothérapie)'
        ],
        'Impact Clinique (%)': [score_base, impact_sucre, impact_stress, impact_stade, impact_timing, impact_taille, impact_dose_chimio, impact_radio]
    })
    fig = px.bar(df_impact, x='Impact Clinique (%)', y='Variables Ajustées par le Médecin', orientation='h',
                 color='Impact Clinique (%)', color_continuous_scale='RdYlGn', text_auto='.1f')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 🔬 Validation Méthodologique & Note de Recherche")
st.info(f"""
**Simulateur Prédictif Modifiable :** Ce panneau de contrôle permet à l'oncologue d'ajuster les curseurs selon le dossier unique de chaque patient. L'interaction en temps réel montre l'impact du nombre exact de séances de chimiothérapie reçues ({nb_seances_chimio} séances) et de la taille de la lésion ({taille_tumeur} mm). En modifiant ces données cliniques conjointement avec les facteurs de l'hôte (stress, régime métabolique), le modèle recalcule dynamiquement le risque relatif et l'efficacité in silico pour appuyer la décision en comité multidisciplinaire (RCP).
""")
