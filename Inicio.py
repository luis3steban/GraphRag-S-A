import streamlit as st
from ui_utils import render_header_svg
import os

# Configuración de la página
st.set_page_config(
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg", 
    layout="wide"
)

# Renderizar encabezados
render_header_svg("images/graphrag.svg", 200)
render_header_svg("images/bottom-header.svg", 200)

st.image('images/stack.png', width=100,use_column_width=True)