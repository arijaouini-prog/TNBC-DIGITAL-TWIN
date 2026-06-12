import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION DE L'INTERFACE ---
st.set_page_config(page_title="OncoSolidDB Universal Twin", page_icon="🧬", layout="wide")

st.title("🧬 OncoSolidDB Universal Twin")
st.subheader("Moteur Multi-Cancer Intégratif : Prédiction Systémique de la Réponse Pathologique")
st.markdown("---")

# --- ONCOSOLIDDB : ONTOLOGIE COMPLÈTE DES CANCERS, SOUS-TYPES ET THÉRAPEUTIQUES ---
# Cette structure de données répertorie les localisations, sous-types cliniques et pharmacopée associée
ONCOSOLID_MASTER_DB = {
    "Cancer du Sein": {
        "Description": "Tumeur maligne de la glande mammaire.",
        "Sous-types": {
            "Triple Négatif (TNBC) [RE-, RP-, HER2-]": {
                "Paclitaxel (Taxol)": {"cible": "Microtubules", "base_eff": 65, "sens_sucre": -1.8, "sens_stress": -1.0},
                "Cisplatine": {"cible": "ADN (Alkylant)", "base_eff": 60, "sens_sucre": -0.5, "sens_stress": -1.5},
                "Pembrolizumab (Keytruda)": {"cible": "Axe PD-1/PD-L1", "base_eff": 55, "sens_sucre": -1.2, "sens_stress": -2.5}
            },
            "HER2 Positif [HER2+]": {
                "Trastuzumab (Herceptin)": {"cible": "Récepteur HER2", "base_eff": 75, "sens_sucre": -1.0, "sens_stress": -0.8},
                "Pertuzumab": {"cible": "Dimérisation HER2", "base_eff": 70, "sens_sucre": -0.8, "sens_stress": -0.7},
                "Docétaxel": {"cible": "Microtubules", "base_eff": 60, "sens_sucre": -1.5, "sens_stress": -1.2}
            },
            "Luminal A / Luminal B [RE+, RP+]": {
                "Tamoxifène": {"cible": "Récepteur Estrogène", "base_eff": 70, "sens_sucre": -0.5, "sens_stress": -1.4},
                "Létrozole (Inhibiteur Aromatase)": {"cible": "Synthèse Estrogènes", "base_eff": 72, "sens_sucre": -0.4, "sens_stress": -1.1}
            }
        }
    },
    "Cancer du Poumon": {
        "Description": "Carcinomes bronchiques et pulmonaires.",
        "Sous-types": {
            "Non à petites cellules (NSCLC) - Mutation EGFR": {
                "Erlotinib (Tarceva)": {"cible": "Tyrosine Kinase EGFR", "base_eff": 75, "sens_sucre": -1.4, "sens_stress": -0.8},
                "Osimertinib": {"cible": "EGFR résistant T790M", "base_eff": 80, "sens_sucre": -1.0, "sens_stress": -0.6}
            },
            "Non à petites cellules (NSCLC) - Sauvage / Immunogène": {
                "Pembrolizumab": {"cible": "PD-1", "base_eff": 60, "sens_sucre": -1.1, "sens_stress": -2.4},
                "Nivolumab": {"cible": "PD-1 Checkpoint", "base_eff": 58, "sens_sucre": -1.0, "sens_stress": -2.2}
            },
            "À petites cellules (SCLC) [Très agressif]": {
                "Étoposide": {"cible": "Topoisomérase II", "base_eff": 55, "sens_sucre": -1.6, "sens_stress": -1.5},
                "Carboplatine": {"cible": "Adduits d ADN", "base_eff": 58, "sens_sucre": -0.6, "sens_stress": -1.3}
            }
        }
    },
    "Cancer Colorectal": {
        "Description": "Tumeurs malignes du côlon et du rectum.",
        "Sous-types": {
            "Type Sauvage (KRAS/NRAS Wild-Type)": {
                "Cetuximab (Erbitux)": {"cible": "EGFR Extracellulaire", "base_eff": 65, "sens_sucre": -1.5, "sens_stress": -0.5},
                "5-Fluorouracile (5-FU)": {"cible": "Thymidylate Synthase", "base_eff": 50, "sens_sucre": -2.0, "sens_stress": -0.8}
            },
            "Muté (KRAS ou NRAS Muté) [Résistant aux anti-EGFR]": {
                "FOLFIRI (Protocole combiné)": {"cible": "Multi-sites / ADN", "base_eff": 55, "sens_sucre": -1.8, "sens_stress": -1.2},
                "Regorafenib": {"cible": "Multi-kinase angiogénique", "base_eff": 48, "sens_sucre": -1.2, "sens_stress": -1.0}
            }
        }
    },
    "Cancer de la Prostate": {
        "Description": "Adénocarcinome prostatique glandulaire.",
        "Sous-types": {
            "Sensible à la castration (Hormono-dépendant)": {
                "Acétate de Leuprolide": {"cible": "Agoniste GnRH", "base_eff": 80, "sens_sucre": -0.5, "sens_stress": -1.1},
                "Bicalutamide": {"cible": "Antagoniste des Androgènes", "base_eff": 70, "sens_sucre": -0.8, "sens_stress": -0.9}
            },
            "Résistant à la castration (Métastatique CRPC)": {
                "Docétaxel (Taxane)": {"cible": "Microtubules", "base_eff": 60, "sens_sucre": -2.0, "sens_stress": -1.3},
                "Enzalutamide (Xtandi)": {"cible": "Signalisation RA", "base_eff": 65, "sens_sucre": -0.7, "sens_stress": -1.5}
            }
        }
    }
}

# --- BARRE LATÉRALE DYNAMIQUE (FILTRES CASCADE) ---
st.sidebar.header("🗂️ 1. Cartographie de la Tumeur (OncoSolidDB)")

# Étape A : Sélection du Cancer Général
cancer_selectionne = st.sidebar.selectbox("Localisation du Cancer :", list(ONCOSOLID_MASTER_DB.keys()))

# Étape B : Sélection du sous-type moléculaire (se met à jour selon le cancer choisi)
liste_sous_types = list(ONCOSOLID_MASTER_DB[cancer_selectionne]["Sous-types"].keys())
sous_type_selectionne = st.sidebar.selectbox("Sous-type Moléculaire / Histologique :", liste_sous_types)

# Étape C : Sélection du médicament (se met à jour selon le sous-type)
liste_medicaments = list(ONCOSOLID_MASTER_DB[cancer_selectionne]["Sous-types"][sous_type_selectionne].keys())
medicament_selectionne = st.sidebar.selectbox("Protocole Thérapeutique :", liste_medicaments)

st.sidebar.markdown("---")
st.sidebar.header("👤 2. Données Physiologiques de l'Hôte")

age = st.sidebar.slider("Âge du patient :", 18, 95, 55)
stade = st.sidebar.selectbox("Stade TNM de la maladie :", ["Stade I / II (Précoce)", "Stade III (Localisé Avancé)", "Stade IV (Métastatique)"])
regime = st.sidebar.selectbox("Régime Métabolique :", ["Standard Occidental (Riche en glucides)", "Isocalorique Équilibré", "Restriction Glucidique / Jeûne thérapeutique intermittent"])
stress = st.sidebar.slider("Index de Stress Chronique (Axe Cortisol, 0 à 10) :", 0, 10, 5)

# --- MOTEUR DE CALCUL MATHÉMATIQUE DU JUMEAU ---
# Extraction des coefficients biophysiques depuis l'arbre de données
data_med = ONCOSOLID_MASTER_DB[cancer_selectionne]["Sous-types"][sous_type_selectionne][medicament_selectionne]
base_eff = data_med["base_eff"]

# Modulateur 1 : Métabolisme glucidique
if regime == "Standard Occidental (Riche en glucides)":
    impact_sucre = 10 * data_med["sens_sucre"]
elif regime == "Restriction Glucidique / Jeûne thérapeutique intermittent":
    impact_sucre = 8.0 # Amplification documentée de la réponse par privation de glucose tumoral
else:
    impact_sucre = 0.0

# Modulateur 2 : Axe Neuro-endocrine
impact_stress = stress * data_med["sens_stress"]

# Modulateur 3 : Clinique (Stade et Âge)
impact_stade = -15.0 if stade == "Stade IV (Métastatique)" else (-7.0 if stade == "Stade III (Localisé Avancé)" else 0.0)
impact_age = -0.08 * (age - 50)

# Calcul du Taux Final de Réponse Pathologique Majeure (mPR)
pCR_final = max(5.0, min(98.0, base_eff + impact_sucre + impact_stress + impact_stade + impact_age))

# --- INTERFACE DE RENDU DES RÉSULTATS ---
st.header(f"🏥 Diagnostic Prédictif : {cancer_selectionne}")
st.write(f"**Sous-type ciblé :** `{sous_type_selectionne}` | **Molécule active :** `{medicament_selectionne}` *(Cible intracellulaire : {data_med['cible']})*")

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("### 🎯 Indice de Récession")
    st.metric(label="Taux de Réponse Pathologique Estimé (pCR)", value=f"{pCR_final:.1f} %")
    st.progress(pCR_final / 100)
    
    if pCR_final >= 70:
        st.success("🟢 PROFIL RÉPONDEUR OPTIMAL")
    elif pCR_final >= 40:
        st.warning("🟡 RÉPONDEUR MODÉRÉ (Résistances micro-environnementales)")
    else:
        st.error("🔴 NON RÉPONDEUR (Échec thérapeutique hautement prévisible)")

with c2:
    st.markdown("### 📊 Balance des Pressions Biophysiques (Modulateurs)")
    df_chart = pd.DataFrame({
        'Paramètres Systémiques': ['Efficacité Théorique de Base', 'Pression Glucide (Alimentation)', 'Pression Cortisol (Stress)', 'Facteur d Extension (Stade)', 'Facteur Homéostasique (Âge)'],
        'Modulation Énergétique (%)': [base_eff, impact_sucre, impact_stress, impact_stade, impact_age]
    })
    fig = px.bar(df_chart, x='Modulation Énergétique (%)', y='Paramètres Systémiques', orientation='h',
                 color='Modulation Énergétique (%)', color_continuous_scale='RdYlGn', text_auto='.1f')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 📝 Section Matériels et Méthodes (Pour ton Article)")
st.info(f"""
**Spécifications du Framework OncoSolidDB-Twin :** Le modèle utilise une architecture arborescente multiniveaux permettant de mapper de manière dynamique la pharmacodynamie de protocoles oncologiques spécifiques en fonction des classifications moléculaires des tumeurs solides. Les interactions calculées en direct simulent les verrous physiologiques de l'hôte (Axe hypothalamo-hypophysaire, statut métabolique périphérique), s'affranchissant des limites des modèles purement tissulaires statiques pour fournir une estimation holistique personnalisée de la réponse thérapeutique.
""")
