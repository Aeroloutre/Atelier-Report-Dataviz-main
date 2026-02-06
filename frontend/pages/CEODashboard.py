"""
🎯 Dashboard Exécutif - Superstore
📊 Indicateurs clés de performance pour la direction
🚀 Vue stratégique et KPI de haut niveau
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import numpy as np

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="🎯 CEO Dashboard - Superstore",
    page_icon="📊",
    layout="wide",  # Mode large pour utiliser tout l'écran
    initial_sidebar_state="collapsed"  # Sidebar réduite pour focus sur les KPI
)

# === STYLES CSS EXÉCUTIFS ===
st.markdown("""
<style>
    /* Style pour les cartes KPI exécutives */
    .executive-kpi {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        border-left: 5px solid #3498db;
    }
    
    /* Style spécifique pour les montants dans les KPI */
    .executive-kpi h1 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        font-weight: 900;
    }
    
    .alert-kpi {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .success-kpi {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Amélioration des métriques exécutives */
    .stMetric {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2c3e50;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Style des titres exécutifs */
    h1 {
        color: #2c3e50;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #34495e;
        font-weight: 700;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    
    /* Style du sidebar exécutif */
    .css-1d391kg {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Style pour les alertes */
    .alert-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
# Utilise la variable d'environnement API_URL si définie (pour Docker),
# sinon utilise localhost (pour développement local)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# === FONCTIONS HELPERS ===

@st.cache_data(ttl=300)  # Cache de 5 minutes
def appeler_api(endpoint: str, params: dict = None):
    """
    Appelle l'API et retourne les données
    Le cache évite de recharger les mêmes données
    
    Args:
        endpoint: Chemin de l'endpoint (ex: "/kpi/globaux")
        params: Paramètres de requête (optionnel)
        
    Returns:
        dict ou list: Données retournées par l'API
    """
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Lève une exception si erreur HTTP
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ **Impossible de se connecter à l'API**")
        st.info(f"💡 Vérifiez que l'API est démarrée sur: {API_URL}")
        st.info("📝 Commande: `python backend/main.py` ou `docker-compose up`")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("⏱️ **Timeout : l'API met trop de temps à répondre**")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ **Erreur HTTP** : {e}")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Erreur inattendue** : {e}")
        st.stop()

def formater_euro(valeur: float) -> str:
    """Formate un nombre en euros"""
    return f"{valeur:,.2f} €".replace(",", " ").replace(".", ",")

def formater_nombre(valeur: int) -> str:
    """Formate un grand nombre avec espaces"""
    return f"{valeur:,}".replace(",", " ")

def formater_pourcentage(valeur: float) -> str:
    """Formate un pourcentage"""
    return f"{valeur:.2f}%"

def calculer_evolution(valeur_actuelle: float, valeur_precedente: float) -> dict:
    """Calcule l'évolution entre deux valeurs"""
    if valeur_precedente == 0:
        return {"evolution": 0, "tendance": "stable", "couleur": "gray"}
    
    evolution = ((valeur_actuelle - valeur_precedente) / valeur_precedente) * 100
    
    if evolution > 5:
        return {"evolution": evolution, "tendance": "forte_hausse", "couleur": "#27ae60"}
    elif evolution > 0:
        return {"evolution": evolution, "tendance": "hausse", "couleur": "#2ecc71"}
    elif evolution > -5:
        return {"evolution": evolution, "tendance": "baisse", "couleur": "#f39c12"}
    else:
        return {"evolution": evolution, "tendance": "forte_baisse", "couleur": "#e74c3c"}

def generer_insight_automatique(kpi_data: dict) -> list:
    """Génère des insights automatiques pour le CEO"""
    insights = []
    
    # Analyse de la marge
    if kpi_data['marge_moyenne'] > 20:
        insights.append("🟢 **Excellente rentabilité** : Marge supérieure à 20%")
    elif kpi_data['marge_moyenne'] < 10:
        insights.append("🔴 **Attention** : Marge faible (<10%), optimisation nécessaire")
    
    # Analyse du panier moyen
    if kpi_data['panier_moyen'] > 500:
        insights.append("🟢 **Bon panier moyen** : Clients à forte valeur")
    elif kpi_data['panier_moyen'] < 200:
        insights.append("🟡 **Panier moyen faible** : Opportunité d'upselling")
    
    # Analyse de la productivité
    ca_par_client = kpi_data['ca_total'] / kpi_data['nb_clients'] if kpi_data['nb_clients'] > 0 else 0
    if ca_par_client > 1000:
        insights.append("🟢 **Clients très rentables** : CA/client élevé")
    
    return insights

# === VÉRIFICATION CONNEXION API ===
with st.spinner("🔄 Connexion à l'API..."):
    try:
        info_api = appeler_api("/")
        st.success(f"✅ Connecté à l'API - Dataset : {info_api['dataset']} ({info_api['nb_lignes']} lignes)")
    except:
        st.error(f"❌ L'API n'est pas accessible sur {API_URL}")
        st.info("💡 Le dashboard s'affichera en mode dégradé")

# === HEADER EXÉCUTIF ===
# Navigation en haut à droite
col_nav, col_title, col_refresh = st.columns([1, 4, 1])

with col_nav:
    st.markdown("### 🔄 Navigation")
    if st.button("📊 Dashboard Standard", use_container_width=True, help="Accéder au dashboard détaillé"):
        st.markdown("""
        <meta http-equiv="refresh" content="0; url=http://localhost:8501">
        <script>window.open('http://localhost:8501', '_blank')</script>
        """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1>🎯 TABLEAU DE BORD EXÉCUTIF</h1>
        <h3 style='color: #7f8c8d; font-weight: 400;'>Superstore - Indicateurs Clés de Performance</h3>
    </div>
    """, unsafe_allow_html=True)

with col_refresh:
    st.markdown("### ⚡ Actions")
    if st.button("🔄 Actualiser", use_container_width=True):
        st.rerun()

# Affichage de la date et heure actuelle
st.markdown(f"📅 **Dernière mise à jour** : {datetime.now().strftime('%d/%m/%Y à %H:%M')} | 🎯 **Mode CEO** | 📊 [Dashboard Standard ↗](http://localhost:8501)")

st.divider()

# === SIDEBAR - FILTRES EXÉCUTIFS ===
st.sidebar.markdown("## 🎯 FILTRES STRATÉGIQUES")
st.sidebar.markdown("*Vue d'ensemble personnalisable*")

# Récupération des valeurs disponibles pour les filtres
try:
    valeurs_filtres = appeler_api("/filters/valeurs")
except:
    # Valeurs par défaut si l'API n'est pas disponible
    valeurs_filtres = {
        'plage_dates': {
            'min': '2020-01-01',
            'max': '2023-12-31'
        },
        'regions': ['Central', 'East', 'South', 'West'],
        'segments': ['Consumer', 'Corporate', 'Home Office'],
        'categories': ['Furniture', 'Office Supplies', 'Technology']
    }

# --- Sélecteur rapide de période ---
st.sidebar.subheader("📊 Analyse Période")
periode_type = st.sidebar.selectbox(
    "Sélectionner une période",
    options=["Dernière année complète", "6 derniers mois", "Trimestre actuel", "Mois actuel", "Personnalisée"],
    help="Période d'analyse pour les KPI"
)

# Calcul des dates selon la sélection
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')
date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')

if periode_type == "Dernière année complète":
    date_fin = date_max
    date_debut = date_fin - timedelta(days=365)
elif periode_type == "6 derniers mois":
    date_fin = date_max
    date_debut = date_fin - timedelta(days=180)
elif periode_type == "Trimestre actuel":
    date_fin = date_max
    date_debut = date_fin - timedelta(days=90)
elif periode_type == "Mois actuel":
    date_fin = date_max
    date_debut = date_fin - timedelta(days=30)
else:  # Personnalisée
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_debut = st.sidebar.date_input(
            "Du",
            value=date_min,
            min_value=date_min,
            max_value=date_max
        )
    with col2:
        date_fin = st.sidebar.date_input(
            "Au",
            value=date_max,
            min_value=date_min,
            max_value=date_max
        )

# --- Filtre vue d'ensemble ---
st.sidebar.subheader("🔍 Focus Analytique")
vue_focus = st.sidebar.radio(
    "Vue stratégique",
    options=["Vue globale", "Par région", "Par segment"],
    help="Ajuster l'analyse selon la vue souhaitée"
)

# Filtres conditionnels selon la vue
region = "Toutes"
segment = "Tous"
categorie = "Toutes"

if vue_focus == "Par région":
    region = st.sidebar.selectbox(
        "Région à analyser",
        options=["Toutes"] + valeurs_filtres['regions']
    )
elif vue_focus == "Par segment":
    segment = st.sidebar.selectbox(
        "Segment à analyser",
        options=["Tous"] + valeurs_filtres['segments']
    )

st.sidebar.divider()
st.sidebar.markdown("💡 **Dashboard optimisé pour la direction**")
st.sidebar.markdown("📊 **Mise à jour automatique toutes les 5 minutes**")

# === PRÉPARATION DES PARAMÈTRES ===
params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if categorie != "Toutes":
    params_filtres['categorie'] = categorie
if region != "Toutes":
    params_filtres['region'] = region
if segment != "Tous":
    params_filtres['segment'] = segment

# === SECTION 1 : KPI EXÉCUTIFS ===
st.markdown("## 📊 INDICATEURS CLÉS EXÉCUTIFS")

with st.spinner("📈 Chargement des KPI stratégiques..."):
    try:
        kpi_data = appeler_api("/kpi/globaux", params=params_filtres)
    except:
        st.error("❌ **Impossible de charger les KPI** - L'API n'est pas disponible")
        st.stop()

# Génération des insights automatiques
insights = generer_insight_automatique(kpi_data)

# === KPI PRINCIPAUX ===
st.markdown("### 💰 Performance Financière")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="executive-kpi">
        <h2 style="margin: 0; font-size: 2.5em;">💰</h2>
        <h3 style="margin: 10px 0;">CHIFFRE D'AFFAIRES</h3>
        <h1 style="margin: 0; font-size: 2.2em;">{}</h1>
        <p style="margin: 10px 0; opacity: 0.9;">Total des ventes</p>
    </div>
    """.format(formater_euro(kpi_data['ca_total'])), unsafe_allow_html=True)

with col2:
    couleur_marge = "#27ae60" if kpi_data['marge_moyenne'] > 15 else "#f39c12" if kpi_data['marge_moyenne'] > 10 else "#e74c3c"
    st.markdown("""
    <div class="executive-kpi" style="background: linear-gradient(135deg, {} 0%, {} 100%);">
        <h2 style="margin: 0; font-size: 2.5em;">📈</h2>
        <h3 style="margin: 10px 0;">MARGE GLOBALE</h3>
        <h1 style="margin: 0; font-size: 2.2em;">{}</h1>
        <p style="margin: 10px 0; opacity: 0.9;">Rentabilité moyenne</p>
    </div>
    """.format(couleur_marge, couleur_marge.replace('#', '#4'), formater_pourcentage(kpi_data['marge_moyenne'])), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="executive-kpi">
        <h2 style="margin: 0; font-size: 2.5em;">💵</h2>
        <h3 style="margin: 10px 0;">PROFIT TOTAL</h3>
        <h1 style="margin: 0; font-size: 2.2em;">{}</h1>
        <p style="margin: 10px 0; opacity: 0.9;">Bénéfice net</p>
    </div>
    """.format(formater_euro(kpi_data['profit_total'])), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="executive-kpi">
        <h2 style="margin: 0; font-size: 2.5em;">👥</h2>
        <h3 style="margin: 10px 0;">BASE CLIENTS</h3>
        <h1 style="margin: 0; font-size: 2.2em;">{}</h1>
        <p style="margin: 10px 0; opacity: 0.9;">Clients actifs</p>
    </div>
    """.format(formater_nombre(kpi_data['nb_clients'])), unsafe_allow_html=True)

st.markdown("### 🎯 Performance Opérationnelle")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="🧾 Commandes",
        value=formater_nombre(kpi_data['nb_commandes']),
        help="Volume d'activité total"
    )

with col6:
    st.metric(
        label="🛒 Panier Moyen",
        value=formater_euro(kpi_data['panier_moyen']),
        help="CA / Nombre de commandes"
    )

with col7:
    articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
    st.metric(
        label="📦 Articles/Commande",
        value=f"{articles_par_commande:.1f}",
        help="Nombre moyen d'articles par commande"
    )

with col8:
    ca_par_client = kpi_data['ca_total'] / kpi_data['nb_clients'] if kpi_data['nb_clients'] > 0 else 0
    st.metric(
        label="💰 CA/Client",
        value=formater_euro(ca_par_client),
        help="Chiffre d'affaires par client"
    )

# === INSIGHTS AUTOMATIQUES ===
if insights:
    st.markdown("### 🧠 Insights Stratégiques")
    for insight in insights:
        st.markdown(f"- {insight}")

    # Alertes spéciales
    col_alert1, col_alert2 = st.columns(2)
    
    if kpi_data['marge_moyenne'] < 10:
        with col_alert1:
            st.markdown("""
            <div class="alert-kpi">
                <h3>⚠️ ALERTE MARGE</h3>
                <p>Rentabilité critique - Action requise</p>
            </div>
            """, unsafe_allow_html=True)
    
    if ca_par_client > 1000:
        with col_alert2:
            st.markdown("""
            <div class="success-kpi">
                <h3>🎯 EXCELLENTE PERFORMANCE</h3>
                <p>Clients à très forte valeur</p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# === SECTION 2 : VUES STRATÉGIQUES ===
st.markdown("## 📈 ANALYSES STRATÉGIQUES")

# === VUE D'ENSEMBLE FINANCIÈRE ===
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📊 Évolution Financière")
    
    # Évolution temporelle (par mois pour vision CEO)
    try:
        temporal = appeler_api("/kpi/temporel", params={'periode': 'mois'})
    except:
        st.error("❌ Impossible de charger les données temporelles")
        temporal = {'mois': [], 'ca': [], 'profit': []}
    df_temporal = pd.DataFrame(temporal)
    
    # Graphique CA et Profit avec tendance
    fig_exec = go.Figure()
    
    # CA avec remplissage
    fig_exec.add_trace(go.Scatter(
        x=df_temporal['periode'],
        y=df_temporal['ca'],
        mode='lines+markers',
        name='Chiffre d\'affaires',
        line=dict(color='#2c3e50', width=4),
        fill='tozeroy',
        fillcolor='rgba(44, 62, 80, 0.1)',
        hovertemplate='<b>CA</b>: %{y:,.0f}€<br><b>Période</b>: %{x}<extra></extra>'
    ))
    
    # Profit avec ligne distincte
    fig_exec.add_trace(go.Scatter(
        x=df_temporal['periode'],
        y=df_temporal['profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='#27ae60', width=3),
        hovertemplate='<b>Profit</b>: %{y:,.0f}€<br><b>Période</b>: %{x}<extra></extra>'
    ))
    
    # Ligne de tendance CA
    if len(df_temporal) > 3:
        x_numeric = np.array(range(len(df_temporal)))
        slope, intercept = np.polyfit(x_numeric, df_temporal['ca'], 1)
        trend_line = [intercept + slope * x for x in x_numeric]
        
        fig_exec.add_trace(go.Scatter(
            x=df_temporal['periode'],
            y=trend_line,
            mode='lines',
            name='Tendance CA',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            showlegend=False
        ))
    
    fig_exec.update_layout(
        title="Évolution Mensuelle - Vue Exécutive",
        xaxis_title="Période",
        yaxis_title="Montant (€)",
        height=400,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_exec, use_container_width=True)

with col_right:
    st.markdown("### 🎯 KPI Synthétiques")
    
    # Calculs pour la période
    ca_moyen = df_temporal['ca'].mean()
    profit_moyen = df_temporal['profit'].mean()
    croissance_ca = ((df_temporal['ca'].iloc[-1] - df_temporal['ca'].iloc[0]) / df_temporal['ca'].iloc[0] * 100) if len(df_temporal) > 1 else 0
    
    # Métriques synthétiques
    st.metric(
        label="📈 CA Mensuel Moyen",
        value=formater_euro(ca_moyen),
        delta=f"{croissance_ca:.1f}% vs début période"
    )
    
    st.metric(
        label="💰 Profit Mensuel Moyen", 
        value=formater_euro(profit_moyen)
    )
    
    # Analyse de saisonnalité (simple)
    mois_max = df_temporal.loc[df_temporal['ca'].idxmax()]
    st.metric(
        label="🏆 Meilleur Mois",
        value=mois_max['periode'],
        delta=formater_euro(mois_max['ca'])
    )
    
    # Prédiction simple (trend)
    if len(df_temporal) > 2:
        x_numeric = np.array(range(len(df_temporal)))
        slope, intercept = np.polyfit(x_numeric, df_temporal['ca'], 1)
        prediction_next = intercept + slope * len(df_temporal)
        
        st.markdown("### 🔮 Projection")
        st.metric(
            label="📊 CA Prochain Mois (trend)",
            value=formater_euro(max(0, prediction_next)),
            help="Basé sur la tendance actuelle"
        )

# === PERFORMANCE PAR SECTEUR ===
st.markdown("### 🏢 Performance par Secteur d'Activité")

col_cat, col_reg = st.columns(2)

with col_cat:
    st.markdown("#### 📦 Catégories")
    try:
        categories = appeler_api("/kpi/categories")
    except:
        st.error("❌ Impossible de charger les données de catégories")
        categories = []
    df_cat = pd.DataFrame(categories)
    
    # Graphique combiné CA et Marge
    fig_cat_exec = go.Figure()
    
    # Barres CA
    fig_cat_exec.add_trace(go.Bar(
        name='CA (€)',
        x=df_cat['categorie'],
        y=df_cat['ca'],
        marker_color='#34495e',
        text=df_cat['ca'].apply(lambda x: f"{x/1000:.0f}K"),
        textposition='outside',
        yaxis='y',
        offsetgroup=1
    ))
    
    # Ligne de marge
    fig_cat_exec.add_trace(go.Scatter(
        name='Marge (%)',
        x=df_cat['categorie'],
        y=df_cat['marge_pct'],
        mode='lines+markers+text',
        marker=dict(color='#e74c3c', size=10),
        line=dict(color='#e74c3c', width=3),
        text=df_cat['marge_pct'].apply(lambda x: f"{x:.1f}%"),
        textposition='top center',
        yaxis='y2'
    ))
    
    # Double axe Y
    fig_cat_exec.update_layout(
        title="CA et Rentabilité par Catégorie",
        xaxis_title="Catégorie",
        yaxis=dict(title="CA (€)", side="left"),
        yaxis2=dict(title="Marge (%)", side="right", overlaying="y"),
        height=350,
        showlegend=True,
        legend=dict(x=0.02, y=0.98)
    )
    
    st.plotly_chart(fig_cat_exec, use_container_width=True)

with col_reg:
    st.markdown("#### 🌍 Régions")
    try:
        geo = appeler_api("/kpi/geographique")
    except:
        st.error("❌ Impossible de charger les données géographiques")
        geo = {'regions': [], 'ca': [], 'profit': []}
    df_geo = pd.DataFrame(geo)
    
    # Graphique radar des régions
    fig_geo_exec = go.Figure()
    
    # Normalisation des données pour le radar (0-100)
    ca_norm = (df_geo['ca'] / df_geo['ca'].max() * 100)
    profit_norm = (df_geo['profit'] / df_geo['profit'].max() * 100)
    clients_norm = (df_geo['nb_clients'] / df_geo['nb_clients'].max() * 100)
    
    colors = ['#2c3e50', '#27ae60', '#e74c3c', '#f39c12']
    
    for i, region in enumerate(df_geo['region']):
        fig_geo_exec.add_trace(go.Scatterpolar(
            r=[ca_norm.iloc[i], profit_norm.iloc[i], clients_norm.iloc[i], ca_norm.iloc[i]],
            theta=['CA', 'Profit', 'Clients', 'CA'],
            fill='toself',
            name=region,
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig_geo_exec.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="Performance Régionale (Normalisée)",
        height=350,
        showlegend=True
    )
    
    st.plotly_chart(fig_geo_exec, use_container_width=True)

# === TOP PERFORMERS ===
st.markdown("### 🏆 TOP PERFORMERS")

col_client, col_product = st.columns(2)

with col_client:
    st.markdown("#### 👑 Clients VIP (Top 5)")
    try:
        clients_data = appeler_api("/kpi/clients", params={'limite': 5})
    except:
        st.error("❌ Impossible de charger les données clients")
        clients_data = []
    df_top_clients = pd.DataFrame(clients_data['top_clients'])
    
    # Graphique clients VIP
    fig_clients_exec = px.bar(
        df_top_clients,
        x='ca_total',
        y='nom',
        orientation='h',
        title="Clients à Plus Forte Valeur",
        labels={'ca_total': 'CA Total (€)', 'nom': 'Client'},
        color='ca_total',
        color_continuous_scale='Blues',
        height=300
    )
    fig_clients_exec.update_traces(
        text=df_top_clients['ca_total'].apply(lambda x: f"{x/1000:.0f}K€"),
        textposition='inside'
    )
    st.plotly_chart(fig_clients_exec, use_container_width=True)

with col_product:
    st.markdown("#### 🎯 Produits Star (Top 5)")
    try:
        top_produits = appeler_api("/kpi/produits/top", params={'limite': 5, 'tri_par': 'profit'})
    except:
        st.error("❌ Impossible de charger les top produits")
        top_produits = []
    df_produits = pd.DataFrame(top_produits)
    
    # Graphique produits star par profit
    fig_products_exec = px.bar(
        df_produits,
        x='profit',
        y='produit',
        orientation='h',
        title="Produits les Plus Rentables",
        labels={'profit': 'Profit (€)', 'produit': 'Produit'},
        color='profit',
        color_continuous_scale='Greens',
        height=300
    )
    fig_products_exec.update_traces(
        text=df_produits['profit'].apply(lambda x: f"{x:.0f}€"),
        textposition='inside'
    )
    fig_products_exec.update_yaxes(title_text="")  # Enlever le label Y pour plus d'espace
    st.plotly_chart(fig_products_exec, use_container_width=True)

st.divider()

# === SECTION 3 : TABLEAU DE BORD STRATÉGIQUE ===
st.markdown("## 🎯 SYNTHÈSE STRATÉGIQUE")

# === ANALYSE CLIENT STRATÉGIQUE ===
try:
    clients_data = appeler_api("/kpi/clients", params={'limite': 5})
except:
    st.error("❌ Impossible de charger les données clients pour la synthèse")
    clients_data = {'recurrence': {'clients_fideles': 0, 'total_clients': 0}}

col_fidelisation, col_segments, col_performance = st.columns([1, 1, 1])

with col_fidelisation:
    st.markdown("### 💎 Fidélisation Client")
    rec = clients_data['recurrence']
    
    # Calculs stratégiques
    taux_fidelisation = (rec['clients_recurrents'] / rec['total_clients'] * 100) if rec['total_clients'] > 0 else 0
    ca_moyen_par_client = kpi_data['ca_total'] / kpi_data['nb_clients'] if kpi_data['nb_clients'] > 0 else 0
    
    # Métriques de fidélisation
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        couleur_fidelisation = "#27ae60" if taux_fidelisation > 60 else "#f39c12" if taux_fidelisation > 40 else "#e74c3c"
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: {couleur_fidelisation}; border-radius: 10px; color: white;">
            <h2 style="margin: 0;">{taux_fidelisation:.1f}%</h2>
            <p style="margin: 5px;">Taux Fidélisation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #34495e; border-radius: 10px; color: white;">
            <h2 style="margin: 0;">{rec['nb_commandes_moyen']:.1f}</h2>
            <p style="margin: 5px;">Commandes/Client</p>
        </div>
        """, unsafe_allow_html=True)
    
    # LTV approximative (simple)
    ltv_approx = ca_moyen_par_client * rec['nb_commandes_moyen']
    st.metric(
        label="💰 LTV Estimée",
        value=formater_euro(ltv_approx),
        help="Lifetime Value approximative"
    )

with col_segments:
    st.markdown("### 💼 Performance Segments")
    df_segments = pd.DataFrame(clients_data['segments'])
    
    # Graphique segments optimisé
    fig_segments_exec = px.pie(
        df_segments,
        values='ca',
        names='segment',
        title="Répartition CA par Segment",
        color_discrete_sequence=['#2c3e50', '#27ae60', '#e74c3c'],
        height=300
    )
    fig_segments_exec.update_traces(
        textposition='inside',
        textinfo='percent+label',
        showlegend=False
    )
    fig_segments_exec.update_layout(
        font=dict(size=12),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_segments_exec, use_container_width=True)
    
    # Segment le plus rentable
    segment_top = df_segments.loc[df_segments['ca'].idxmax()]
    st.metric(
        label="🏆 Segment Leader",
        value=segment_top['segment'],
        delta=formater_euro(segment_top['ca'])
    )

with col_performance:
    st.markdown("### 📊 Indicateurs Clés")
    
    # Concentration client (part des top 5)
    top_5_ca = sum(client['ca_total'] for client in clients_data['top_clients'])
    concentration = (top_5_ca / kpi_data['ca_total'] * 100) if kpi_data['ca_total'] > 0 else 0
    
    st.metric(
        label="🎯 Concentration Top 5",
        value=f"{concentration:.1f}%",
        help="Part du CA des 5 meilleurs clients"
    )
    
    # Client moyen vs VIP
    client_vip_moyen = top_5_ca / 5
    ratio_vip = client_vip_moyen / ca_moyen_par_client if ca_moyen_par_client > 0 else 0
    
    st.metric(
        label="⭐ Ratio VIP/Moyen",
        value=f"{ratio_vip:.1f}x",
        help="Combien les VIP rapportent vs client moyen"
    )
    
    # Opportunité upselling (basé sur panier moyen)
    if kpi_data['panier_moyen'] < 300:
        opportunity = "🟡 Upselling"
    elif kpi_data['panier_moyen'] > 600:
        opportunity = "🟢 Premium"
    else:
        opportunity = "🔵 Standard"
    
    st.metric(
        label="🚀 Opportunité",
        value=opportunity,
        delta=formater_euro(kpi_data['panier_moyen'])
    )

# === RESUME EXÉCUTIF ===
st.markdown("### 📋 RÉSUMÉ EXÉCUTIF")

col_resume1, col_resume2 = st.columns(2)

with col_resume1:
    st.markdown("#### 💪 FORCES")
    
    forces = []
    if kpi_data['marge_moyenne'] > 15:
        forces.append("✅ Rentabilité excellente")
    if taux_fidelisation > 50:
        forces.append("✅ Bonne fidélisation client")
    if concentration < 30:
        forces.append("✅ Base client diversifiée")
    if kpi_data['panier_moyen'] > 400:
        forces.append("✅ Panier moyen élevé")
    
    if not forces:
        forces.append("📊 Base solide à optimiser")
    
    for force in forces[:4]:  # Max 4 éléments
        st.markdown(f"- {force}")

with col_resume2:
    st.markdown("#### 🔧 AXES D'AMÉLIORATION")
    
    ameliorations = []
    if kpi_data['marge_moyenne'] < 15:
        ameliorations.append("⚠️ Optimiser la rentabilité")
    if taux_fidelisation < 50:
        ameliorations.append("⚠️ Améliorer la rétention")
    if concentration > 40:
        ameliorations.append("⚠️ Diversifier la clientèle")
    if kpi_data['panier_moyen'] < 300:
        ameliorations.append("⚠️ Développer l'upselling")
    
    if not ameliorations:
        ameliorations.append("🎯 Maintenir l'excellence")
    
    for amelioration in ameliorations[:4]:  # Max 4 éléments
        st.markdown(f"- {amelioration}")

# === ACTIONS RECOMMANDÉES ===
st.markdown("### 🎯 ACTIONS PRIORITAIRES")

actions = []

if kpi_data['marge_moyenne'] < 12:
    actions.append({
        "priorite": "🔴 URGENT",
        "action": "Révision des prix et coûts",
        "impact": "Rentabilité",
        "delai": "Immédiat"
    })

if taux_fidelisation < 40:
    actions.append({
        "priorite": "🟡 IMPORTANT",
        "action": "Programme de fidélisation",
        "impact": "Rétention client",
        "delai": "30 jours"
    })

if concentration > 50:
    actions.append({
        "priorite": "🟡 IMPORTANT", 
        "action": "Diversification commerciale",
        "impact": "Réduction du risque",
        "delai": "90 jours"
    })

if kpi_data['panier_moyen'] < 250:
    actions.append({
        "priorite": "🟢 OPPORTUNITÉ",
        "action": "Stratégie cross-selling",
        "impact": "CA par transaction",
        "delai": "60 jours"
    })

if actions:
    df_actions = pd.DataFrame(actions)
    st.dataframe(
        df_actions,
        use_container_width=True,
        hide_index=True,
        column_config={
            "priorite": "Priorité",
            "action": "Action",
            "impact": "Impact",
            "delai": "Délai"
        }
    )
else:
    st.success("🎉 **Performance optimale** - Maintenir la stratégie actuelle")

# === FOOTER EXÉCUTIF ===
st.divider()
st.markdown("---")

# Informations de navigation
st.info("""
🔄 **Navigation** : 
- 🎯 **Dashboard CEO** (actuel) : http://localhost:8502
- 📊 **Dashboard Standard** : http://localhost:8501
- 🔗 **API Backend** : http://localhost:8000
""")

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("""
    <div style='text-align: center; color: #2c3e50;'>
        <h4>📊 TABLEAU DE BORD EXÉCUTIF</h4>
        <p>Superstore Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

with col_footer2:
    st.markdown(f"""
    <div style='text-align: center; color: #7f8c8d;'>
        <p><strong>Dernière mise à jour</strong></p>
        <p>{datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)

with col_footer3:
    st.markdown("""
    <div style='text-align: center; color: #34495e;'>
        <h4>🎯 KPI EN TEMPS RÉEL</h4>
        <p>Dashboard stratégique</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: #95a5a6; margin-top: 20px;'>
    <p>🔒 Dashboard confidentiel • 📈 Données temps réel • 🎯 Vision stratégique</p>
</div>
""", unsafe_allow_html=True)
