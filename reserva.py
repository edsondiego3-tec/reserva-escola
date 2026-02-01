import streamlit as st
import pandas as pd
from datetime import date
import urllib.parse
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

# --- CONFIGURAÇÕES ---
# Senha Admin
try:
    SENHA_ADMIN = st.secrets["SENHA_ADMIN"]
except:
    SENHA_ADMIN = "cmjp2026"

# Constantes
QUANTIDADE_TOTAL_PROJETORES = 3 # Agora fixo no código para simplificar com Sheets
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

# --- FUNÇÕES DE BANCO DE DADOS (GOOGLE SHEETS) ---
def get_connection():
    # Cria a conexão com o Google Sheets usando os segredos
    return st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    conn = get_connection()
    try:
        # Lê a planilha. ttl=0 garante que não usa cache antigo
        df = conn.read(worksheet="Página1", ttl=0)
        # Se a planilha estiver vazia ou nova, cria as colunas
        if df.empty or "Professor" not in df.columns:
            return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
        # Garante que Data e Horario sejam string para comparação
        df['Data'] = df['Data'].astype(str)
        return df
    except Exception:
        # Se der erro (ex: planilha vazia), retorna dataframe vazio
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])

def salvar_nova_reserva(nova_linha_dict):
    conn = get_connection()
    df_atual = carregar_dados()
    
    # Cria um DF com a nova linha
    novo_df = pd.DataFrame([nova_linha_dict])
    
    # Junta com o antigo
    df_final = pd.concat([df_atual, novo_df], ignore_index=True)
    
    # Salva no Google Sheets
    conn.update(worksheet="Página1", data=df_final)

def salvar_dataframe_completo(df):
    # Usado pelo Admin para exclusão
    conn = get_connection()
    conn.update(worksheet="Página1", data=df)

# --- LOGO ---
def exibir_logo():
    # URL pública ou local (se tiver no github)
    # Como não temos garantia do arquivo local persistente, removi a verificação complexa
    # Se quiser, coloque a logo.jpg no github e use st.image("logo.jpg")
    st.markdown("## 🏫 CMJP") 

# --- INICIALIZAÇÃO ---
# Menu Lateral
with st.sidebar:
    st.header("Painel de Controle")
    modo_acesso = st.selectbox("Perfil", ["Professor", "Administrador"])
    st.divider()
    
    # Status (Lendo do Sheets)
    df_status = carregar_dados()
    reservas_hoje = 0
    if not df_status.empty and "Data" in df_status.columns:
        hoje_str = str(date.today())
        reservas_hoje = len(df_status[df_status["Data"] == hoje_str])
        
    st.caption("Status do Dia")
    col1, col2 = st.columns(2)
    col1.metric("Total", QUANTIDADE_TOTAL_PROJETORES)
    col2.metric("Usados", reservas_hoje)

# ==================================================
# FLUXO PROFESSOR
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
            # Filtra contexto
            reservas_hora = df_reservas[
                (df_reservas["Data"] == str(data_escolhida)) & 
                (df_reservas["Horario"] == h)
            ]
            
            # Regra 1: Quantidade por horário
            if len(reservas_hora) >= QUANTIDADE_TOTAL_PROJETORES:
                erros.append(f"❌ {h}: Todos os aparelhos ocupados.")
            else:
                # Regra 2: Conflito de Turma
                for t in turmas:
                    conflito = reservas_hora[reservas_hora["Turmas"].astype(str).str.contains(t, na=False)]
                    if not conflito.empty:
                        prof_ocupou = conflito.iloc[0]['Professor']
                        erros.append(f"⚠️ {h}: Turma {t} já reservada ({prof_ocupou}).")
        
        if erros:
            for e in erros: st.error(e)
        else:
            st.success("✅ Disponível")
            pode_salvar = True

    if st.button("CONFIRMAR AGENDAMENTO"):
        if pode_salvar:
            turmas_str = ", ".join(turmas)
            msg_zap_horarios = ""
            
            # Salva cada horário individualmente
            for h in horarios:
                nova_reserva = {
                    "Professor": nome_prof,
                    "Data": str(data_escolhida),
                    "Horario": h,
                    "Nivel": nivel,
                    "Turmas": turmas_str,
                    "DataRegistro": str(date.today())
                }
                salvar_nova_reserva(nova_reserva)
                msg_zap_horarios += f"\n⏰ {h}"
            
            # Links WhatsApp
            texto_zap = f"*RESERVA DATASHOW CMJP*\nProf: {nome_prof}\nData: {data_escolhida.strftime('%d/%m')}\nTurmas: {turmas_str}\n{msg_zap_horarios}"
            link_zap = urllib.parse.quote(texto_zap)
            
            st.balloons()
            st.success("Reserva salva na Nuvem! ☁️")
            st.link_button("🚨 ENVIAR P/ GILMAR", f"https://wa.me/5583986243832?text={link_zap}")
            st.rerun() # Atualiza a tela para mostrar na tabela

    st.divider()
    st.subheader(f"Agenda do dia {data_escolhida.strftime('%d/%m')}")
    if not df_reservas.empty:
        filtro = df_reservas[df_reservas["Data"] == str(data_escolhida)]
        if not filtro.empty:
            st.dataframe(filtro[["Horario", "Turmas", "Professor"]], hide_index=True)
        else:
            st.info("Livre")

# ==================================================
# FLUXO ADMIN
# ==================================================
elif modo_acesso == "Administrador":
    st.markdown("## Painel de Gestão")
    if st.text_input("Senha", type="password") == SENHA_ADMIN:
        st.success("Conectado ao Google Sheets")
        
        tab1, tab2 = st.tabs(["Dashboard", "Editar Banco"])
        
        df = carregar_dados()
        
        with tab1:
            if not df.empty:
                c1, c2 = st.columns(2)
                c1.metric("Total Reservas", len(df))
                top_prof = df['Professor'].mode()[0] if not df.empty else "-"
                c2.metric("Top Professor", top_prof)
                
                # Gráfico
                contagem = df['Professor'].value_counts().head(5).reset_index()
                contagem.columns = ['Professor', 'Qtd']
                st.plotly_chart(px.bar(contagem, x='Qtd', y='Professor', orientation='h'))
        
        with tab2:
            st.warning("As alterações aqui refletem direto na planilha.")
            df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            if st.button("SALVAR ALTERAÇÕES NA NUVEM"):
                salvar_dataframe_completo(df_edit)
                st.success("Planilha atualizada!")
                st.rerun()
