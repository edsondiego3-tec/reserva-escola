import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
import json
import base64

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫", layout="wide")

# --- FUNÇÃO PARA GERAR A MARCA D'ÁGUA ---
def set_background(image_file):
    with open(image_file, "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: 50%; /* Tamanho da logo no fundo (ajuste se precisar) */
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Camada branca semi-transparente para garantir leitura do texto */
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.85); /* 85% de branco por cima da logo */
            z-index: -1;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

# --- ESTILOS VISUAIS (BOTÕES) ---
st.markdown("""
    <style>
    h1, h2, h3 { color: #003366 !important; text-align: center; }
    
    div.stButton > button:first-child {
        background-color: #D4AF37;
        color: #003366;
        font-weight: bold;
        border: 2px solid #003366;
        width: 100%;
        height: 50px;
        font-size: 18px;
    }
    div.stButton > button:hover {
        background-color: #bfa14f;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ARQUIVOS E CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_reservas.csv"
ARQUIVO_CONFIG = "config.json"
SENHA_ADMIN = "cmjp2026"

# WHATSAPP
ZAP_GILMAR = "5583986243832"
ZAP_EDSON = "5583991350479"
ZAP_LOURDINHA = "5583987104722"

HORARIOS_AULA = [
    "1º Horário (07:00 - 07:50)",
    "2º Horário (07:50 - 08:40)",
    "3º Horário (08:40 - 09:20)",
    "Intervalo",
    "4º Horário (09:40 - 10:30)",
    "5º Horário (10:30 - 11
