"""
Point d'entrée de l'application multi-page
"""

import streamlit as st

st.set_page_config(
    page_title="Superstore BI",
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
    <h1>Accedez à un dashboard personnalisé !</h1>
</div>
""", unsafe_allow_html=True)

# Navigation cards
st.markdown("### Choisissez un dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="page-card">
        <h3>Dashboard Commercial</h3>
    """, unsafe_allow_html=True)
    if st.button("Accéder →", key="commercial", use_container_width=True):
        st.switch_page("pages/Dashboard-Commercial.py")

with col2:
    st.markdown("""
    <div class="page-card">
        <h3>Dashboard donné au départ</h3>
    """, unsafe_allow_html=True)
    if st.button("Accéder →", key="general", use_container_width=True):
        st.switch_page("pages/Dashboard.py")