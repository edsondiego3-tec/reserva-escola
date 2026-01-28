import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
from PIL import Image

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫")

# --- ESTILOS VISUAIS (AZUL E DOURADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1, h2, h3 { color: #003366 !important; text-align: center; }
    
    /* Botão Principal */
    div.stButton > button:first-child {
        background-color: #D4AF37;
        color: #003366;
        font-weight: bold;
        border: 2px solid #003366;
    }
    div.stButton > button:hover {
        background-color: #bfa14f;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO SISTEMA ---
ARQUIVO_DADOS = "banco_reservas.csv"
QUANTIDADE_TOTAL_PROJETORES = 3

# NÚMEROS DE WHATSAPP
ZAP_GILMAR = "5583986243832"    # Obrigatório
ZAP_EDSON = "5583991350479"     # Coord. Médio
ZAP_LOURDINHA = "5583987104722" # Coord. Fundamental

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

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_multiplas_reservas(lista_reservas):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame(lista_reservas)], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

# --- CABEÇALHO COM LOGO ---
col_esq, col_meio, col_dir = st.columns([3, 2, 3])

with col_meio:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=150)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.warning("⚠️ Logo não encontrada.")

st.markdown("### Sistema de Reserva de Data Show")
st.markdown("---")

df_reservas = carregar_dados()

# --- FORMULÁRIO ---
st.subheader("Nova Reserva")

col1, col2 = st.columns(2)
with col1:
    nome_prof = st.text_input("Nome do Professor(a)")
    data_escolhida = st.date_input("Data de Uso", min_value=date.today())
    nivel_selecionado = st.selectbox("Nível de Ensino", list(TURMAS_ESCOLA.keys()))

with col2:
    horarios_selecionados = st.multiselect("Selecione os Horários", HORARIOS_AULA)
    turmas_disponiveis = TURMAS_ESCOLA[nivel_selecionado]
    turmas_selecionadas = st.multiselect("Selecione as Turmas", turmas_disponiveis)

# --- VERIFICAÇÃO ---
if horarios_selecionados:
    st.info("Verificando disponibilidade...")
    horarios_com_problema = []
    
    for hora in horarios_selecionados:
        reservas_na_hora = df_reservas[
            (df_reservas["Data"] == str(data_escolhida)) & 
            (df_reservas["Horario"] == hora)
        ]
        # Conta simples: Total - Ocupados = Livres
        qtd_livre = QUANTIDADE_TOTAL_PROJETORES - len(reservas_na_hora)
        
        if qtd_livre <= 0:
            horarios_com_problema.append(hora)

    if horarios_com_problema:
        st.error(f"❌ Esgotado para: {', '.join(horarios_com_problema)}")
        pode_salvar = False
    else:
        st.success(f"✅ Disponível!")
        pode_salvar = True
else:
    pode_salvar = False

# --- BOTÃO DE RESERVAR ---
if st.button("CONFIRMAR RESERVAS"):
    if not nome_prof:
        st.warning("Preencha o nome do professor.")
    elif not horarios_selecionados:
        st.warning("Selecione pelo menos um horário.")
    elif not turmas_selecionadas:
        st.warning("Selecione pelo menos uma turma.")
    elif not pode_salvar:
        st.error("Horários indisponíveis.")
    else:
        novas_reservas = []
        lista_horarios_texto = ""
        turmas_texto = ", ".join(turmas_selecionadas)

        for hora in horarios_selecionados:
            novas_reservas.append({
                "Professor": nome_prof,
                "Data": str(data_escolhida),
                "Horario": hora,
                "Nivel": nivel_selecionado,
                "Turmas": turmas_texto,
                "DataRegistro": date.today()
            })
            lista_horarios_texto += f"\n⏰ {hora}"

        salvar_multiplas_reservas(novas_reservas)
        
        # Links WhatsApp
        msg_base = f"*RESERVA DATASHOW CMJP* 🏫\n\n*Prof:* {nome_prof}\n*Data:* {data_escolhida}\n*Turmas:* {turmas_texto}\n*Horários:*{lista_horarios_texto}"
        msg_codificada = urllib.parse.quote(msg_base)
        
        link_gilmar = f"https://wa.me/{ZAP_GILMAR}?text={msg_codificada}"
        link_edson = f"https://wa.me/{ZAP_EDSON}?text={msg_codificada}"
        link_lourdinha = f"https://wa.me/{ZAP_LOURDINHA}?text={msg_codificada}"

        st.balloons()
        st.success("Reserva Salva! Envie os comprovantes:")
        st.divider()
        
        st.markdown("#### 📱 Envio de Comprovante")
        
        # Botão Gilmar
        st.markdown(f"""
        <a href="{link_gilmar}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#d9534f; color:white; padding:15px; border-radius:10px; text-align:center; margin-bottom:10px;">
                <strong>1. ENVIAR PARA SEU GILMAR (OBRIGATÓRIO) 🚨</strong>
            </div>
        </a>
        """, unsafe_allow_html=True)

        col_zap1, col_zap2 = st.columns(2)
        with col_zap1:
            st.markdown(f"""<a href="{link_edson}" target="_blank" style="text-decoration:none;"><div style="background-color:#D4AF37; color:#003366; padding:10px; border-radius:10px; text-align:center;"><strong>2. Coord. Médio (Edson)</strong></div></a>""", unsafe_allow_html=True)
        with col_zap2:
            st.markdown(f"""<a href="{link_lourdinha}" target="_blank" style="text-decoration:none;"><div style="background-color:#D4AF37; color:#003366; padding:10px; border-radius:10px; text-align:center;"><strong>3. Coord. Fund. (Lourdinha)</strong></div></a>""", unsafe_allow_html=True)

# --- VISÃO GERAL ---
st.divider()
st.subheader(f"📅 Reservas do dia {data_escolhida}")
filtro_hoje = df_reservas[df_reservas["Data"] == str(data_escolhida)]

if not filtro_hoje.empty:
    filtro_hoje = filtro_hoje.sort_values("Horario")
    st.table(filtro_hoje[["Horario", "Turmas", "Professor"]])
else:
    st.write("Nenhuma reserva para esta data.")
