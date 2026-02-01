import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
import json
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫", layout="wide")

# --- LISTA DE PROFESSORES (FIXA) ---
LISTA_PROFESSORES_FIXA = [
    "Selecione seu nome...",
    "ADEMAR (FILOSOFIA)", "ANDERSON (MATEMÁTICA)", "ARISTELIA (FILOSOFIA)",
    "BRENDA (ED. FISICA)", "CAROLINA (GRAMATICA)", "DAIANE (BIOLOGIA)",
    "DAYANNE (PORTUGUES)", "EDSON (COORDENAÇÃO)", "ELAYNE (PSI. PEDAGOGA)",
    "ESLÂNIA (HISTORIA)", "FRANCISCO (MATEMÁTICA)", "ISADORA (QUIMICA)",
    "JANAINA (LITERATURA)", "JANILSON (GEOGRAFIA)", "KARLA (FISICA)",
    "LARISSA (MATEMÁTICA)", "LOURINHA (COORDENAÇÃO)", "LUIZA (ED. FISICA)",
    "MARILIA (CIENCIAS)", "MAYARA (ARTES)", "PAULO (HISTORIA)",
    "ROSANY (INGLES)"
]

# --- CSS VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1, h2, h3 { color: #003366 !important; text-align: center; }
    div.stButton > button:first-child {
        background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%;
    }
    /* Classe para destacar o botão do Gilmar */
    .btn-gilmar {
        background-color: #d9534f !important;
        color: white !important;
        font-size: 20px !important;
        padding: 15px !important;
        border-radius: 10px !important;
        text-align: center;
        text-decoration: none;
        display: block;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ARQUIVOS LOCAIS (CONFIG) ---
ARQUIVO_CONFIG = "config.json"

# --- SENHAS E CONSTANTES ---
try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except:
    SENHA_ADMIN = "cmjp2026"

HORARIOS_AULA = [
    "1º Horário (07:00 - 07:50)", "2º Horário (07:50 - 08:40)",
    "3º Horário (08:40 - 09:20)", "Intervalo",
    "4º Horário (09:40 - 10:30)", "5º Horário (10:30 - 11:20)",
    "6º Horário (11:20 - 12:10)"
]
TURMAS_ESCOLA = {
    "ENSINO FUNDAMENTAL": ["6º ANO", "7º ANO", "8º ANO", "9º ANO"],
    "ENSINO MÉDIO": ["1ª SÉRIE", "2ª SÉRIE", "3ª SÉRIE"]
}
# ZAPS
ZAP_GILMAR = "5583986243832"
ZAP_EDSON = "5583991350479"
ZAP_LOURDINHA = "5583987104722"

# --- CONFIGURAÇÃO DE ESTOQUE ---
def carregar_config_qtd():
    padrao = {"total_projetores": 3}
    if not os.path.exists(ARQUIVO_CONFIG):
        return padrao
    try:
        with open(ARQUIVO_CONFIG, "r") as f: return json.load(f)
    except: return padrao

def salvar_config_qtd(nova_qtd):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump({"total_projetores": nova_qtd}, f)

# --- BANCO DE DADOS (GOOGLE SHEETS) ---
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    conn = get_connection()
    try:
        df = conn.read(ttl=0)
        if df.empty or "Professor" not in df.columns:
            return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
        df['Data'] = df['Data'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])

def salvar_nova_reserva(nova_linha_dict):
    conn = get_connection()
    df_atual = carregar_dados()
    novo_df = pd.DataFrame([nova_linha_dict])
    df_final = pd.concat([df_atual, novo_df], ignore_index=True)
    conn.update(data=df_final)

def salvar_dataframe_completo(df):
    conn = get_connection()
    conn.update(data=df)

# --- LOGO ---
def exibir_logo():
    lista_logos = ["logo.jpg", "Logo.jpg", "logo.png"]
    found = False
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        for l in lista_logos:
            if os.path.exists(l):
                st.image(l, width=130)
                found = True
                break
        if not found: st.markdown("## 🏫 CMJP")

# --- INICIALIZAÇÃO ---
config = carregar_config_qtd()
QUANTIDADE_TOTAL_PROJETORES = config.get("total_projetores", 3)

# Inicializa sessão para controlar o botão do Zap
if "reserva_sucesso" not in st.session_state:
    st.session_state.reserva_sucesso = False
if "link_zap_cache" not in st.session_state:
    st.session_state.link_zap_cache = ""

with st.sidebar:
    st.header("Painel de Controle")
    modo_acesso = st.selectbox("Perfil", ["Professor", "Administrador"])
    st.divider()
    
    df_status = carregar_dados()
    reservas_hoje = 0
    if not df_status.empty and "Data" in df_status.columns:
        hoje = str(date.today())
        reservas_hoje = len(df_status[df_status["Data"] == hoje])
        
    st.caption("Status do Dia")
    c1, c2 = st.columns(2)
    c1.metric("Total", QUANTIDADE_TOTAL_PROJETORES)
    c2.metric("Usados", reservas_hoje)

# ==================================================
# ÁREA DO PROFESSOR
# ==================================================
if modo_acesso == "Professor":
    exibir_logo()
    
    # SE A RESERVA FOI FEITA COM SUCESSO, MOSTRA OS BOTÕES
    if st.session_state.reserva_sucesso:
        st.balloons()
        st.success("✅ AGENDAMENTO SALVO NO SISTEMA!")
        st.markdown("### Agora o passo mais importante: AVISE NO WHATSAPP!")
        
        # Recupera o link da memória
        link_zap = st.session_state.link_zap_cache
        
        # Botão Gigante do Gilmar
        st.markdown(f"""
        <a href='https://wa.me/{ZAP_GILMAR}?text={link_zap}' target='_blank' style='text-decoration:none;'>
            <div style='background-color:#d9534f; color:white; padding:20px; border-radius:15px; text-align:center; font-weight:bold; font-size:22px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
                🚨 CLIQUE AQUI: AVISAR SEU GILMAR
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        st.write("")
        c_z1, c_z2 = st.columns(2)
        with c_z1:
            st.markdown(f"<a href='https://wa.me/{ZAP_EDSON}?text={link_zap}' target='_blank'><button style='background-color:#D4AF37; color:#003366; border:none; padding:10px; width:100%; border-radius:5px;'>Coord. Médio</button></a>", unsafe_allow_html=True)
        with c_z2:
            st.markdown(f"<a href='https://wa.me/{ZAP_LOURDINHA}?text={link_zap}' target='_blank'><button style='background-color:#D4AF37; color:#003366; border:none; padding:10px; width:100%; border-radius:5px;'>Coord. Fund.</button></a>", unsafe_allow_html=True)
            
        st.divider()
        if st.button("🔄 Fazer Outra Reserva / Voltar"):
            st.session_state.reserva_sucesso = False
            st.rerun()
            
    else:
        # TELA NORMAL DE RESERVA
        st.markdown("### Agendamento de Data Show")
        st.markdown("---")
        df_reservas = carregar_dados()

        with st.container():
            st.subheader("📝 Nova Solicitação")
            c1, c2 = st.columns(2)
            with c1:
                nome_prof = st.selectbox("Professor(a)", LISTA_PROFESSORES_FIXA)
                data_escolhida = st.date_input("Data", min_value=date.today())
                nivel = st.selectbox("Nível", list(TURMAS_ESCOLA.keys()))
            with c2:
                horarios = st.multiselect("Horários", HORARIOS_AULA)
                turmas = st.multiselect("Turmas", TURMAS_ESCOLA[nivel])

        # Validação
        pode_salvar = False
        if horarios and turmas and nome_prof != "Selecione seu nome...":
            erros = []
            for h in horarios:
                reservas_hora = df_reservas[
                    (df_reservas["Data"] == str(data_escolhida)) & 
                    (df_reservas["Horario"] == h)
                ]
                if len(reservas_hora) >= QUANTIDADE_TOTAL_PROJETORES:
                    erros.append(f"❌ {h}: Todos ocupados.")
                else:
                    for t in turmas:
                        conflito = reservas_hora[reservas_hora["Turmas"].astype(str).str.contains(t, na=False)]
                        if not conflito.empty:
                            prof = conflito.iloc[0]['Professor']
                            erros.append(f"⚠️ {h}: Turma {t} ocupada ({prof}).")
            
            if erros:
                for e in erros: st.error(e)
            else:
                st.success("✅ Disponível")
                pode_salvar = True

        if st.button("CONFIRMAR AGENDAMENTO"):
            if pode_salvar:
                turmas_str = ", ".join(turmas)
                msgs = ""
                for h in horarios:
                    nova = {
                        "Professor": nome_prof, "Data": str(data_escolhida),
                        "Horario": h, "Nivel": nivel,
                        "Turmas": turmas_str, "DataRegistro": str(date.today())
                    }
                    salvar_nova_reserva(nova)
                    msgs += f"\n⏰ {h}"
                
                texto = f"*RESERVA DATASHOW CMJP* 🏫\nProf: {nome_prof}\nData: {data_escolhida.strftime('%d/%m')}\nTurmas: {turmas_str}\n{msgs}"
                link = urllib.parse.quote(texto)
                
                # SALVA NO ESTADO E RECARREGA PARA MOSTRAR OS BOTÕES
                st.session_state.reserva_sucesso = True
                st.session_state.link_zap_cache = link
                st.rerun()

        st.divider()
        st.subheader(f"Agenda do dia {data_escolhida.strftime('%d/%m')}")
        if not df_reservas.empty:
            filtro = df_reservas[df_reservas["Data"] == str(data_escolhida)]
            if not filtro.empty:
                st.dataframe(filtro[["Horario", "Turmas", "Professor"]], hide_index=True, use_container_width=True)
            else: st.info("Livre")

# ==================================================
# ÁREA DO ADMINISTRADOR
# ==================================================
elif modo_acesso == "Administrador":
    st.markdown("## Painel de Gestão")
    if st.text_input("Senha", type="password") == SENHA_ADMIN:
        st.success("Conectado Google Sheets")
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗑️ Editar", "⚙️ Config"])
        df = carregar_dados()
        with tab1:
            if not df.empty:
                c1, c2 = st.columns(2)
                c1.metric("Reservas Totais", len(df))
                try:
                    c2.metric("Top Professor", df['Professor'].mode()[0])
                    contagem = df['Professor'].value_counts().head(5).reset_index()
                    contagem.columns = ['Professor', 'Qtd']
                    st.plotly_chart(px.bar(contagem, x='Qtd', y='Professor', orientation='h'))
                except: pass
        with tab2:
            st.warning("Edição direta na Planilha")
            df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            if st.button("SALVAR NA NUVEM"):
                salvar_dataframe_completo(df_edit)
                st.success("Salvo!")
                st.rerun()
        with tab3:
            novo_total = st.number_input("Total Data Shows:", value=int(QUANTIDADE_TOTAL_PROJETORES))
            if st.button("Atualizar Estoque"):
                salvar_config_qtd(novo_total)
                st.success("Atualizado!")
                st.rerun()
