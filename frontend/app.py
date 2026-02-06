"""
🏠 Page d'accueil - Superstore BI
Point d'entrée de l'application multi-page
"""

import streamlit as st

st.set_page_config(
    page_title="Superstore BI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour la page d'accueil
st.markdown("""
<style>
    .main .block-container {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .home-header {
        text-align: center;
        padding: 3rem 0;
    }
    
    .home-header h1 {
        font-size: 3rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    
    .home-header p {
        font-size: 1.2rem;
        color: #666;
    }
    
    .page-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    
    .page-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .page-card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .page-card h3 {
        color: #1E3A5F;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    .page-card p {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="home-header">
    <h1>🛒 Superstore BI</h1>
    <p>Plateforme d'analyse Business Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Navigation cards
st.markdown("### 📊 Choisissez un dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="page-card">
        <div class="page-card-icon">📈</div>
        <h3>Dashboard Commercial</h3>
        <p>Vue d'ensemble de la performance des ventes, KPIs commerciaux, évolution du CA et analyse clients.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder →", key="commercial", use_container_width=True):
        st.switch_page("pages/commercialDashboard.py")

with col2:
    st.markdown("""
    <div class="page-card">
        <div class="page-card-icon">🛒</div>
        <h3>Dashboard Général</h3>
        <p>Analyse complète du dataset Superstore avec filtres avancés, produits, catégories et géographie.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder →", key="general", use_container_width=True):
        st.switch_page("pages/dashboard.py")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; font-size: 0.85rem;'>
        💡 Utilisez le menu latéral pour naviguer entre les pages
    </div>
    """,
    unsafe_allow_html=True
)
