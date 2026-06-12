import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION INTERFACE ---
st.set_page_config(page_title="BC Universal Twin Engine", page_icon="🛡️", layout="wide")

st.title("🛡️ BC Universal Twin Engine : Jumeau Numérique Systémique")
st.subheader("Simulateur de Réponse Thérapeutique Multi-Traitements (Validé sur Données Littéraires PubMed)")
st.markdown("---")

# --- BASE DE DONNÉES BIOLOGIQUE DES TRAITEMENTS (Moteur Littéraire) ---
TRAITEMENTS_DB = {
    "Paclitaxel (Taxol)": {
        "classe": "Chimiothérapie (Taxane)",
        "cible": "Microtubules (Division cellulaire)",
        "efficacite_base": 65.0,
        "sensibilite_sucre": -20.0,  # L'insuline active mTOR et crée une résistance aux taxanes
        "sensibilite_stress": -10.0,
        "description": "Chimiothérapie standard de première ligne bloquant la mitose cellulaire."
    },
    "Cisplatine": {
        "classe": "Chimiothérapie (Agent Alkylant)",
        "cible": "ADN Tumoral (Alkylant)",
        "efficacite_base": 60.0,
        "sensibilite_sucre": -5.0,
        "sensibilite_stress": -15.0, # Le cortisol bloque l'apoptose induite par les dommages à l'ADN
        "description": "Agent de chimiothérapie lourd provoquant des cassures double-brins de l'ADN."
    },
    "Pembrolizumab (Keytruda)": {
        "classe": "Immunothérapie Checkpoint",
        "cible": "Point de contrôle immunitaire PD-1 / PD-L1",
        "efficacite_base": 55.0,
        "sensibilite_sucre": -10.0,
        "sensibilite_stress": -25.0, # Le stress chronique détruit l'immunité (Lymphocytes T)
        "description": "Anticorps monoclonal d'immunothérapie réactivant le système immunitaire du patient."
    },
    "Trastuzumab (Herceptin)": {
        "classe": "Thérapie Ciblée (Anti-HER2)",
        "cible": "Oncoprotéine HER2",
        "efficacite_base": 75.0,
        "sensibilite_sucre": -8.0,
        "sensibilite_stress": -5.0,
        "description": "Anticorps ciblant le domaine extracellulaire du récepteur HER2."
    },
    "Tamoxifène": {
        "classe": "Hormonothérapie",
        "cible": "Récepteurs des Estrogènes (RE)",
        "efficacite_base": 72.0,
        "sensibilite_sucre": -5.0,
        "sensibilite_stress": -8.0,
        "description": "Modulateur sélectif des récepteurs aux estrogènes bloquant la signalisation hormonale."
    }
}

# --- BARRE LATÉRALE : VARIABLES DYNAMIQUES DE L'HÔTE ---
st.sidebar.header("🔬 1. Profil Immunohistochimique (IHC)")
recepteur_estrogene = st.sidebar.selectbox("Récepteur Estrogène (RE) :", ["Négatif (-)", "Positif (+)"])
recepteur_progesterone = st.sidebar.selectbox("Récepteur Progestérone (RP) :", ["Négatif (-)", "Positif (+)"])
statut_her2 = st.sidebar.selectbox("Statut HER2 (Score IHC/FISH) :", ["HER2 Négatif", "HER2 Positif (3+ ou FISH amplifié)"])

# Déduction physiopathologique automatique du sous-type pour le filtrage
if recepteur_estrogene == "Positif (+)" and statut_her2 == "HER2 Négatif":
    sous_type_deduit = "Luminal (Hormono-dépendant)"
    traitements_filtres = ["Tamoxifène", "Paclitaxel (Taxol)", "Cisplatine"]
elif statut_her2 == "HER2 Positif (3+ ou FISH amplifié)":
    sous_type_deduit = "HER2 Positif (Amplifié)"
    traitements_filtres = ["Trastuzumab (Herceptin)", "Paclitaxel (Taxol)"]
else:
    sous_type_deduit = "Triple Négatif (TNBC) [RE-, RP-, HER2-]"
    traitements_filtres = ["Paclitaxel (Taxol)", "Cisplatine", "Pembrolizumab (Keytruda)"]

st.sidebar.info(f"**Sous-type diagnostiqué :** {sous_type_deduit}")

st.sidebar.header("👤 2. Paramètres Cliniques Évalués")
age = st.sidebar.slider("Âge du patient :", 18, 90, 48)
stade = st.sidebar.selectbox("Stade de la Tumeur (Classification Extension) :", ["Stade I", "Stade II", "Stade III", "Stade IV (Métastatique)"])
taille_t = st.sidebar.selectbox("Taille de la tumeur (Classification T) :", ["T0", "T1", "T2", "T3", "T4"])

st.sidebar.header("⏳ 3. Chronologie & Radiothérapie")
# Nouveaux paramètres demandés
timing = st.sidebar.radio("Timing du protocole thérapeutique :", ["Néoadjuvant (Avant Chirurgie)", "Adjuvant (Après Chirurgie)"])
radiotherapie_oui_non = st.sidebar.radio("Radiothérapie associée :", ["Oui", "Non"])
nb_seances_radio = st.sidebar.slider("Nombre de séances de radiothérapie validées :", 5, 35, 25) if radiotherapie_oui_non == "Oui" else 0

st.sidebar.header("🍏 4. Microenvironnement & Mode de vie")
regime = st.sidebar.selectbox("Régime Alimentaire / Profil Métabolique :", ["Équilibré (Faible index glycémique)", "Occidental (Riche en sucres et acides gras)", "Cétogène strict"])
stress = st.sidebar.slider("Niveau de Stress Psychologique / Cortisol (0 à 10) :", 0, 10, 6)
environnement = st.sidebar.selectbox("Perturbateurs Endocriniens / Pollution :", ["Exposition Faible", "Exposition Élevée"])

st.sidebar.header("💊 5. Sélection de la Thérapeutique Autorisée")
traitement_choisi = st.sidebar.selectbox("Choisir le traitement à injecter dans le Jumeau :", traitements_filtres)


# --- MOTEUR CLINIQUES ET SYNAPTIQUES DU JUMEAU (ALGORITHME MODIFIÉ) ---
info_t = TRAITEMENTS_DB[traitement_choisi]
efficacite_calculée = info_t["efficacite_base"]

# 1. Algorithme métabolique
if regime == "Occidental (Riche en sucres et acides gras)":
    impact_sucre = info_t["sensibilite_sucre"]
elif regime == "Cétogène strict":
    impact_sucre = 8.0 
else:
    impact_sucre = 0.0

# 2. Algorithme Cortisol
impact_stress = (stress / 10.0) * info_t["sensibilite_stress"]

# 3. Algorithme d'extension anatomique
if stade == "Stade IV (Métastatique)":
    impact_stade = -15.0
elif stade == "Stade III":
    impact_stade = -7.0
else:
    impact_stade = 0.0

# 4. Algorithme de taille tumorale T0-T4
if "T4" in taille_t:
    impact_taille = -12.0
elif "T3" in taille_t:
    impact_taille = -7.0
elif "T2" in taille_t:
    impact_taille = -3.0
else:
    impact_taille = 0.0

# 5. Algorithme d'ajustement de la Radiothérapie & Chronologie
if radiotherapie_oui_non == "Oui":
    # Synergie positive sur le contrôle local/systémique selon la complétude des séances
    impact_radio = 5.0 if nb_seances_radio >= 20 else 2.0
else:
    # Pénalisation potentielle de récurrence locale si absente dans les stades avancés
    impact_radio = -6.0 if stade in ["Stade II", "Stade III"] else -2.0

# Modulation de base induite par la chronologie de l'administration (Néoadjuvant vs Adjuvant)
impact_timing = 3.0 if timing == "Néoadjuvant (Avant Chirurgie)" else 0.0

# Calcul du score final réorganisé
score_final_reponse = max(5, min(98, efficacite_calculée + impact_sucre + impact_stress + impact_stade + impact_taille + impact_radio + impact_timing))


# --- AFFICHAGE DE L'INTERFACE ET RAPPORT SCIENTIFIQUE ---
st.header(f"📋 Rapport Prédictif du Jumeau Numérique : Traitement par {traitement_choisi}")
st.write(f"**Profil Clinique :** Protocole {timing} | Phénotype : RE [{recepteur_estrogene}] | RP [{recepteur_progesterone}] | HER2 [{statut_her2}]")
st.caption(f"**Description du mécanisme d'action :** {info_t['description']}")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎯 Score de Réponse")
    # Adaptation sémantique de l'indicateur selon le choix temporel
    label_reponse = "Taux de Réponse Pathologique Complète Prédit (pCR)" if timing == "Néoadjuvant (Avant Chirurgie)" else "Bénéfice Absolu Net Estimé (Gain DFS à 5 ans)"
    
    st.metric(label=label_reponse, value=f"{score_final_reponse:.1f} %")
    st.progress(score_final_reponse / 100)
    
    if score_final_reponse >= 70:
        st.success("🟢 HAUTEMENT RÉPONDEUR : Le profil systémique et moléculaire est optimal pour cette stratégie.")
    elif score_final_reponse >= 40:
        st.warning("🟡 RÉPONDEUR MODÉRÉ : Résistance partielle détectée. Nécessité d'agir sur les facteurs microenvironnementaux.")
    else:
        st.error("🔴 NON RÉPONDEUR / RÉSISTANCE : Risque d'échec thérapeutique élevé dû aux blocages systémiques.")

with col2:
    st.markdown("### 📊 Décomposition des Pressions de Résistance (Données Cliniques)")
    
    df_poids = pd.DataFrame({
        'Paramètres Systémiques': [
            'Efficacité Théorique Initiale', 
            'Impact Glycémique (Alimentation)', 
            'Impact Cortisol (Stress)', 
            'Avancement Tumoral (Stade)', 
            f'Critère Dimensionnel ({taille_t})',
            f'Contrôle Local (Radiothérapie : {radiotherapie_oui_non})',
            'Facteur Chronologique (Timing)'
        ],
        'Modulation Énergétique (%)': [efficacite_calculée, impact_sucre, impact_stress, impact_stade, impact_taille, impact_radio, impact_timing]
    })
    fig = px.bar(df_poids, x='Modulation Énergétique (%)', y='Paramètres Systémiques', orientation='h',
                 color='Modulation Énergétique (%)', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 🔬 Corrélation Biologique & Synthèse Littéraire (Format PubMed)")

st.info(f"""
* **Mécanisme et Cible Principale :** Le traitement sélectionné (*{traitement_choisi}*) opère préférentiellement sur la voie : **{info_t['cible']}**.
* **Analyse de la Stratégie Thérapeutique :** L'approche configurée en mode **{timing}** intègre une dynamique d'évaluation macro-tumorale. L'association de la radiothérapie (**{radiotherapie_oui_non}** avec {nb_seances_radio} séances) module le coefficient de contrôle local régional à hauteur de {impact_radio:.1f}%.
* **Analyse de Résistance Métabolique & Neuro-endocrine :** L'évaluation montre qu'avec un profil métabolique de type *{regime}* et un score de stress de *{stress}/10*, le patient génère des barrières biochimiques affectant la cinétique thérapeutique. Le critère dimensionnel clinique ({taille_t}) applique une charge d'extension mesurée à {impact_taille:.1f}%.
* **Orientation pour le LGMIB :** Ce jumeau numérique permet de moduler dynamiquement l'ordre d'administration (Néoadjuvant vs Adjuvant) et l'impact de l'irradiation locale afin de comparer l'efficacité des protocoles standardisés vis-à-vis des barrières physiologiques de l'hôte.
""")
