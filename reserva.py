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
    </style>
    """, unsafe_allow_html=True)

# --- ARQUIVOS LOCAIS (SÓ PARA CONFIGURAÇÃO) ---
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

# --- FUNÇÕES: CONFIGURAÇÃO DE ESTOQUE (JSON) ---
def carregar_config_qtd():
    # Cria padrão se não existir
    padrao = {"total_projetores": 3}
    if not os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "w") as f: json.dump(padrao, f)
        except: pass
        return padrao
    try:
        with open(ARQUIVO_CONFIG, "r") as f: return json.load(f)
    except: return padrao

def salvar_config_qtd(nova_qtd):
    dados = {"total_projetores": nova_qtd}
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(dados, f)

# --- FUNÇÕES: BANCO DE DADOS (GOOGLE SHEETS) ---
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    conn = get_connection()
    try:
        # Pega a URL direto do secrets (que você configurou no passo 1)
        df = conn.read(ttl=0) 
        if df.empty or "Professor" not in df.columns:
            return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
        df['Data'] = df['Data'].astype(str)
        return df
    except Exception as e:
        # Se der erro, retorna vazio para não quebrar a tela, mas avisa no log
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])

def salvar_nova_reserva(nova_linha_dict):
    conn = get_connection()
    df_atual = carregar_dados()
    novo_df = pd.DataFrame([nova_linha_dict])
    df_final = pd.concat([df_atual, novo_df], ignore_index=True)
    # Atualiza a planilha
    conn.update(data=df_final)

def salvar_dataframe_completo(df):
    conn = get_connection()
    conn.update(data=df)

# --- LOGO ---
def exibir_logo():
    # Tenta mostrar logo se existir, senão mostra texto
    lista_logos = ["logo.jpg", "Logo.jpg", "logo.png"]
    found = False
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        for l in lista_logos:
            if os.path.exists(l):
                st.image(l, width=130)
                found = True
                break
        if not found: st.markdown("## 🏫 CMJP")

# --- INICIALIZAÇÃO ---
config = carregar_config_qtd()
QUANTIDADE_TOTAL_PROJETORES = config.get("total_projetores", 3)

with st.sidebar:
    st.header("Painel de Controle")
    modo_acesso = st.selectbox("Perfil", ["Professor", "Administrador"])
    st.divider()
    
    # Status Lendo do Sheets
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
            
            # Regra 1: Quantidade (Lendo do JSON configurável)
            if len(reservas_hora) >= QUANTIDADE_TOTAL_PROJETORES:
                erros.append(f"❌ {h}: Todos os {QUANTIDADE_TOTAL_PROJETORES} aparelhos ocupados.")
            else:
                # Regra 2: Conflito
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
            
            texto = f"*RESERVA DATASHOW CMJP*\nProf: {nome_prof}\nData: {data_escolhida.strftime('%d/%m')}\nTurmas: {turmas_str}\n{msgs}"
            link = urllib.parse.quote(texto)
            st.balloons()
            st.success("Salvo na Nuvem!")
            st.markdown(f"<a href='https://wa.me/5583986243832?text={link}' target='_blank'><button style='background-color:#d9534f; color:white; border:none; padding:10px; border-radius:5px; width:100%'>🚨 ENVIAR P/ GILMAR</button></a>", unsafe_allow_html=True)
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
        st.success("Autenticado")
        
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗑️ Editar Reservas", "⚙️ Config Estoque"])
        
        df = carregar_dados()
        
        with tab1:
            if not df.empty:
                c1, c2 = st.columns(2)
                c1.metric("Reservas Totais", len(df))
                try:
                    top = df['Professor'].mode()[0]
                    c2.metric("Top Professor", top)
                    contagem = df['Professor'].value_counts().head(5).reset_index()
                    contagem.columns = ['Professor', 'Qtd']
                    st.plotly_chart(px.bar(contagem, x='Qtd', y='Professor', orientation='h'))
                except: st.info("Dados insuficientes para gráficos.")
        
        with tab2:
            st.warning("Alterações aqui afetam a Planilha Google imediatamente.")
            df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="edit_adm")
            if st.button("SALVAR ALTERAÇÕES NA NUVEM"):
                salvar_dataframe_completo(df_edit)
                st.success("Planilha atualizada!")
                st.rerun()

        with tab3:
            st.markdown("### Quantidade de Equipamentos")
            # Aqui permitimos editar o arquivo JSON local
            novo_total = st.number_input("Total de Data Shows:", value=int(QUANTIDADE_TOTAL_PROJETORES))
            if st.button("Atualizar Estoque"):
                salvar_config_qtd(novo_total)
                st.success(f"Atualizado para {novo_total} aparelhos!")
                st.rerun()
