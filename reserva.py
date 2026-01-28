import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
import json
import plotly.express as px

# --- CONFIGURAÇÃO INICIAL DA PÁGINA ---
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫", layout="wide")

# --- LISTA OFICIAL DE PROFESSORES (FIXA NO CÓDIGO) ---
# Edite aqui se precisar adicionar alguém novo no futuro
LISTA_PROFESSORES_FIXA = [
    "Selecione seu nome...",
    "ADEMAR (FILOSOFIA)",
    "ANDERSON (MATEMÁTICA)",
    "ARISTELIA (FILOSOFIA)",
    "BRENDA (ED. FISICA)",
    "CAROLINA (GRAMATICA)",
    "DAIANE (BIOLOGIA)",
    "DAYANNE (PORTUGUES)",
    "EDSON (COORDENAÇÃO)",
    "ELAYNE (PSI. PEDAGOGA)",
    "ESLÂNIA (HISTORIA)",
    "FRANCISCO (MATEMÁTICA)",
    "ISADORA (QUIMICA)",
    "JANAINA (LITERATURA)",
    "JANILSON (GEOGRAFIA)",
    "KARLA (FISICA)",
    "LARISSA (MATEMÁTICA)",
    "LOURINHA (COORDENAÇÃO)",
    "LUIZA (ED. FISICA)",
    "MARILIA (CIENCIAS)",
    "MAYARA (ARTES)",
    "PAULO (HISTORIA)",
    "ROSANY (INGLES)"
]

# --- CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1, h2, h3 { color: #003366 !important; text-align: center; font-family: 'Helvetica', sans-serif; }
    
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }

    div.stButton > button:first-child {
        background-color: #D4AF37;
        color: #003366;
        font-weight: bold;
        border: none;
        width: 100%;
        height: 50px;
        font-size: 16px;
        border-radius: 8px;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #bfa14f;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ARQUIVOS ---
ARQUIVO_DADOS = "banco_reservas.csv"
ARQUIVO_CONFIG = "config.json"

# Tenta pegar a senha dos segredos, senão usa a padrão
try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except:
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
    "5º Horário (10:30 - 11:20)",
    "6º Horário (11:20 - 12:10)"
]

TURMAS_ESCOLA = {
    "ENSINO FUNDAMENTAL": ["6º ANO", "7º ANO", "8º ANO", "9º ANO"],
    "ENSINO MÉDIO": ["1ª SÉRIE", "2ª SÉRIE", "3ª SÉRIE"]
}

# --- FUNÇÕES ---
def carregar_config_qtd():
    # Carrega APENAS a quantidade de projetores do arquivo
    padrao = {"total_projetores": 3}
    if not os.path.exists(ARQUIVO_CONFIG):
        return padrao
    try:
        with open(ARQUIVO_CONFIG, "r", encoding='utf-8') as f:
            dados = json.load(f)
            return dados
    except:
        return padrao

def salvar_config_qtd(nova_qtd):
    # Salva APENAS a quantidade
    dados = {"total_projetores": nova_qtd}
    with open(ARQUIVO_CONFIG, "w", encoding='utf-8') as f:
        json.dump(dados, f)

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_multiplas_reservas(lista_reservas):
    df = carregar_dados()
    novo_df = pd.DataFrame(lista_reservas)
    df = pd.concat([df, novo_df], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

def salvar_dataframe_completo(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

def exibir_logo():
    lista_logos = ["logo.jpg", "Logo.jpg", "logo.png", "logo.jpeg", "logo dourada 3d (1) (1)[2014] - Copia.jpg"]
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        for nome in
