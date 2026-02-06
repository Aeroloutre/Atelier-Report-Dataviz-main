"""
Dashboard Commercial
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Dashboard Commercial",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Couleurs du thème
COLORS = {
    'primary': '#1E3A5F',      # Bleu marine
    'secondary': '#3D5A80',    # Bleu moyen
    'accent': '#00B4D8',       # Cyan
    'success': '#2ECC71',      # Vert
    'warning': '#F39C12',      # Orange
    'danger': '#E74C3C',       # Rouge
    'light': '#F8F9FA',        # Gris clair
    'dark': '#2C3E50'          # Gris foncé
}

# CSS personnalisé
st.markdown(f"""
<style>
    /* Reset et base */
    .main .block-container {{
        padding: 0.5rem 2rem 1rem 2rem;
        max-width: 100%;
    }}
    
    /* Header principal */
    .dashboard-header {{
        background: {COLORS['primary']};
        padding: 1.8rem 2.5rem;
        margin: -1rem -2rem 1.5rem -2rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .header-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .header-icon {{
        font-size: 2.2rem;
    }}
    
    .header-title {{
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }}
    
    .header-subtitle {{
        margin: 0.2rem 0 0 0;
        opacity: 0.7;
        font-size: 0.85rem;
        font-weight: 400;
    }}
    
    .header-right {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }}
    
    .header-stat {{
        text-align: right;
    }}
    
    .header-stat-value {{
        font-size: 1.1rem;
        font-weight: 700;
    }}
    
    .header-stat-label {{
        font-size: 0.7rem;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Cartes KPI */
    .kpi-container {{
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        height: 100%;
        text-align: center;
    }}
    
    .kpi-label {{
        font-size: 0.8rem;
        color: #888;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.4rem;
    }}
    
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {COLORS['dark']};
        margin: 0;
    }}
    
    .kpi-subtitle {{
        font-size: 0.8rem;
        color: {COLORS['accent']};
        font-weight: 500;
        margin-top: 0.4rem;
    }}
    
    /* Section insight */
    .insight-box {{
        padding: 0.5rem 0 0 0;
        margin: 0;
    }}
    
    .insight-box h4 {{
        display: inline;
        color: {COLORS['accent']};
        font-size: 0.8rem;
        font-weight: 600;
    }}
    
    .insight-box p {{
        display: inline;
        color: white;
        font-size: 0.85rem;
        line-height: 1.5;
    }}
    
    /* Titres de section */
    .section-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {COLORS['light']};
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['accent']};
        display: inline-block;
    }}
    
    /* Amélioration des métriques Streamlit */
    div[data-testid="stMetric"] {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}
    
    /* Masquer le footer Streamlit */
    footer {{ visibility: hidden; }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['light']};
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    """Appel API avec gestion d'erreurs"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("🔌 **Connexion impossible** — Vérifiez que l'API est démarrée")
        st.stop()
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()

def format_currency(value: float) -> str:
    """Formate en euros"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M €"
    elif value >= 1_000:
        return f"{value/1_000:.1f}k €"
    return f"{value:,.0f} €"

def format_number(value: int) -> str:
    """Formate les nombres"""
    if value >= 1_000:
        return f"{value/1_000:.1f}k"
    return f"{value:,}".replace(",", " ")

def format_percent(value: float) -> str:
    """Formate les pourcentages"""
    return f"{value:.1f}%"

def create_kpi_card(label: str, value: str, subtitle: str = None):
    """Crée une carte KPI HTML"""
    subtitle_html = f'<p class="kpi-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
    <div class="kpi-container">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
        {subtitle_html}
    </div>
    """

def create_insight_box(title: str, content: str):
    """Crée une boîte d'insight"""
    return f"""
    <div class="insight-box">
        <h4>{title}</h4>
        <p>{content}</p>
    </div>
    """

# ══════════════════════════════════════════════════════════════════════════════
# VÉRIFICATION API
# ══════════════════════════════════════════════════════════════════════════════

try:
    info_api = appeler_api("/")
except:
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="dashboard-header">
    <div class="header-left">
        <span class="header-icon"></span>
        <div>
            <h1 class="header-title">Dashboard Commercial</h1>
            <p class="header-subtitle">Performance des ventes en temps réel</p>
        </div>
    </div>
    <div class="header-right">
        <div class="header-stat">
            <div class="header-stat-value">{info_api['nb_lignes']:,}</div>
            <div class="header-stat-label">Transactions</div>
        </div>
        <div class="header-stat">
            <div class="header-stat-value">{info_api['periode']['debut'][:4]} - {info_api['periode']['fin'][:4]}</div>
            <div class="header-stat-label">Période</div>
        </div>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FILTRES RAPIDES (en haut)
# ══════════════════════════════════════════════════════════════════════════════

valeurs_filtres = appeler_api("/filters/valeurs")

col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])

with col_f1:
    date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
    date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')
    date_range = st.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )
    if len(date_range) == 2:
        date_debut, date_fin = date_range
    else:
        date_debut, date_fin = date_min, date_max

with col_f2:
    region = st.selectbox("Région", ["Toutes"] + valeurs_filtres['regions'])

with col_f3:
    segment = st.selectbox("Segment", ["Tous"] + valeurs_filtres['segments'])

with col_f4:
    categorie = st.selectbox("Catégorie", ["Toutes"] + valeurs_filtres['categories'])

# Paramètres de filtrage
params = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if region != "Toutes":
    params['region'] = region
if segment != "Tous":
    params['segment'] = segment
if categorie != "Toutes":
    params['categorie'] = categorie

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 : KPIs COMMERCIAUX
# ══════════════════════════════════════════════════════════════════════════════

kpi_data = appeler_api("/kpi/globaux", params=params)

# Calcul des métriques dérivées pour les commerciaux
taux_conversion = (kpi_data['nb_commandes'] / kpi_data['nb_clients'] * 100) if kpi_data['nb_clients'] > 0 else 0
profit_par_commande = kpi_data['profit_total'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0

# Affichage des 5 KPIs principaux
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_kpi_card(
        "Chiffre d'affaires",
        format_currency(kpi_data['ca_total']),
        "Objectif principal"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_kpi_card(
        "Profit généré",
        format_currency(kpi_data['profit_total']),
        f"Marge: {format_percent(kpi_data['marge_moyenne'])}"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_kpi_card(
        "Commandes",
        format_number(kpi_data['nb_commandes']),
        f"Panier: {format_currency(kpi_data['panier_moyen'])}"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_kpi_card(
        "Clients actifs",
        format_number(kpi_data['nb_clients']),
        f"{taux_conversion:.1f} cmd/client"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(create_kpi_card(
        "Profit / Commande",
        format_currency(profit_par_commande),
        "Rentabilité"
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 : VISUALISATIONS PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════

col_left, col_right = st.columns([3, 2])

# --- Graphique évolution temporelle ---
with col_left:
    st.markdown('<p class="section-title">Évolution des Ventes</p>', unsafe_allow_html=True)
    
    temporal = appeler_api("/kpi/temporel", params={'periode': 'mois'})
    df_temporal = pd.DataFrame(temporal)
    
    fig_evolution = go.Figure()
    
    # Aire pour le CA
    fig_evolution.add_trace(go.Scatter(
        x=df_temporal['periode'],
        y=df_temporal['ca'],
        name='Chiffre d\'affaires',
        fill='tozeroy',
        line=dict(color=COLORS['accent'], width=2),
        fillcolor='rgba(0, 180, 216, 0.2)'
    ))
    
    # Ligne pour le profit
    fig_evolution.add_trace(go.Scatter(
        x=df_temporal['periode'],
        y=df_temporal['profit'],
        name='Profit',
        line=dict(color=COLORS['success'], width=2, dash='dot')
    ))
    
    fig_evolution.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig_evolution.update_xaxes(showgrid=False)
    fig_evolution.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Insight sur la tendance
    if len(df_temporal) >= 2:
        variation = ((df_temporal['ca'].iloc[-1] - df_temporal['ca'].iloc[-2]) / df_temporal['ca'].iloc[-2] * 100)
        tendance = "en hausse" if variation > 0 else "en baisse"
        st.markdown(create_insight_box(
            "Tendance",
            f"Le CA est {tendance} de {abs(variation):.1f}% par rapport au mois précédent. "
            f"La meilleure période reste {df_temporal.loc[df_temporal['ca'].idxmax(), 'periode']} "
            f"avec {format_currency(df_temporal['ca'].max())} de CA."
        ), unsafe_allow_html=True)

# --- Performance par région ---
with col_right:
    st.markdown('<p class="section-title">Performance Régionale</p>', unsafe_allow_html=True)
    
    geo = appeler_api("/kpi/geographique")
    df_geo = pd.DataFrame(geo)
    
    fig_geo = go.Figure()
    
    fig_geo.add_trace(go.Bar(
        x=df_geo['region'],
        y=df_geo['ca'],
        name='CA',
        marker_color=COLORS['secondary'],
        text=df_geo['ca'].apply(lambda x: format_currency(x)),
        textposition='outside'
    ))
    
    fig_geo.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig_geo.update_xaxes(showgrid=False)
    fig_geo.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Insight sur la région leader
    region_leader = df_geo.iloc[0]
    part_marche = (region_leader['ca'] / df_geo['ca'].sum() * 100)
    st.markdown(create_insight_box(
        "Région leader",
        f"La région {region_leader['region']} représente {part_marche:.0f}% du CA total "
        f"avec {region_leader['nb_clients']} clients actifs."
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 : ANALYSE DES VENTES
# ══════════════════════════════════════════════════════════════════════════════

col_produits, col_categories = st.columns([3, 2])

# --- Top Produits ---
with col_produits:
    st.markdown('<p class="section-title">Produits les Plus Vendus</p>', unsafe_allow_html=True)
    
    top_produits = appeler_api("/kpi/produits/top", params={'limite': 8, 'tri_par': 'ca'})
    df_produits = pd.DataFrame(top_produits)
    
    # Tronquer les noms trop longs
    df_produits['produit_short'] = df_produits['produit'].apply(
        lambda x: x[:40] + '...' if len(x) > 40 else x
    )
    
    fig_produits = px.bar(
        df_produits,
        x='ca',
        y='produit_short',
        orientation='h',
        color='profit',
        color_continuous_scale=['#E74C3C', '#F39C12', '#2ECC71'],
        labels={'ca': 'CA (€)', 'produit_short': '', 'profit': 'Profit'}
    )
    
    fig_produits.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(title="Profit €", thickness=15),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_produits, use_container_width=True)

# --- Répartition par catégorie ---
with col_categories:
    st.markdown('<p class="section-title">Répartition par Catégorie</p>', unsafe_allow_html=True)
    
    categories = appeler_api("/kpi/categories")
    df_cat = pd.DataFrame(categories)
    
    fig_cat = go.Figure()
    
    fig_cat.add_trace(go.Pie(
        labels=df_cat['categorie'],
        values=df_cat['ca'],
        hole=0.5,
        textinfo='label+percent',
        textposition='outside',
        marker_colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent']],
        pull=[0.02, 0, 0]
    ))
    
    fig_cat.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        annotations=[dict(text='CA', x=0.5, y=0.5, font_size=16, showarrow=False)]
    )
    
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # Tableau résumé des marges
    st.markdown("**Marges par catégorie :**")
    for _, row in df_cat.iterrows():
        marge = row['marge_pct']
        color = COLORS['success'] if marge > 10 else (COLORS['warning'] if marge > 5 else COLORS['danger'])
        st.markdown(
            f"<span style='color:{color}; font-weight:600;'>●</span> "
            f"{row['categorie']}: **{marge:.1f}%**",
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 : ANALYSE CLIENTS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-title">Performance Clients</p>', unsafe_allow_html=True)

clients_data = appeler_api("/kpi/clients", params={'limite': 5})

col_c1, col_c2 = st.columns(2)

# --- Top Clients ---
with col_c1:
    df_top_clients = pd.DataFrame(clients_data['top_clients'])
    
    fig_clients = px.bar(
        df_top_clients.head(5),
        x='ca_total',
        y='nom',
        orientation='h',
        title='Top 5 Clients',
        color_discrete_sequence=[COLORS['accent']]
    )
    
    fig_clients.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis={'categoryorder': 'total ascending', 'title': ''},
        xaxis={'title': 'CA Total (€)'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_clients, use_container_width=True)

# --- Performance par segment ---
with col_c2:
    df_segments = pd.DataFrame(clients_data['segments'])
    
    fig_segments = go.Figure()
    
    fig_segments.add_trace(go.Bar(
        x=df_segments['segment'],
        y=df_segments['ca'],
        name='CA',
        marker_color=COLORS['secondary']
    ))
    
    fig_segments.add_trace(go.Bar(
        x=df_segments['segment'],
        y=df_segments['profit'],
        name='Profit',
        marker_color=COLORS['success']
    ))
    
    fig_segments.update_layout(
        title=dict(text='Performance par Segment', font=dict(color='white', size=14)),
        height=320,
        margin=dict(l=0, r=0, t=60, b=0),
        barmode='group',
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(color='white')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_segments, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style='text-align: center; color: #999; font-size: 0.8rem; padding: 1rem;'>
        Dashboard Commercial • Données: {info_api['nb_lignes']:,} transactions 
        • Période: {info_api['periode']['debut']} → {info_api['periode']['fin']}
    </div>
    """,
    unsafe_allow_html=True
)
