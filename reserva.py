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
        for nome in lista_logos:
            if os.path.exists(nome):
                st.image(nome, width=130)
                return

# --- INICIALIZAÇÃO ---
config = carregar_config_qtd()
QUANTIDADE_TOTAL_PROJETORES = config.get("total_projetores", 3)

# --- MENU LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    modo_acesso = st.selectbox("Perfil", ["Professor", "Administrador"])
    st.divider()
    
    # Status Rápido
    df_rapido = carregar_dados()
    reservas_hoje = 0
    if not df_rapido.empty:
        reservas_hoje = len(df_rapido[df_rapido["Data"] == str(date.today())])
    
    st.caption("Status do Dia")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Total", QUANTIDADE_TOTAL_PROJETORES)
    col_s2.metric("Usados", reservas_hoje)
    
    st.progress(min(reservas_hoje / max(QUANTIDADE_TOTAL_PROJETORES, 1), 1.0))

# ==================================================
# FLUXO 1: PROFESSOR
# ==================================================
if modo_acesso == "Professor":
    exibir_logo()
    st.markdown("<h3 style='margin-top:-10px;'>Agendamento de Equipamentos</h3>", unsafe_allow_html=True)
    st.markdown("---")

    df_reservas = carregar_dados()

    with st.container():
        st.subheader("📝 Nova Solicitação")
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            # USA A LISTA FIXA DO CÓDIGO
            nome_prof = st.selectbox("Selecione seu Nome", LISTA_PROFESSORES_FIXA)
            data_escolhida = st.date_input("Data de Uso", min_value=date.today())
            nivel_selecionado = st.selectbox("Nível de Ensino", list(TURMAS_ESCOLA.keys()))

        with col_form2:
            horarios_selecionados = st.multiselect("Horários Necessários", HORARIOS_AULA)
            turmas_disponiveis = TURMAS_ESCOLA[nivel_selecionado]
            turmas_selecionadas = st.multiselect("Turmas (Para o mesmo horário)", turmas_disponiveis)

    pode_salvar = False
    
    if horarios_selecionados and turmas_selecionadas and nome_prof != "Selecione seu nome...":
        
        erros_encontrados = []
        
        for hora in horarios_selecionados:
            reservas_neste_horario = df_reservas[
                (df_reservas["Data"] == str(data_escolhida)) & 
                (df_reservas["Horario"] == hora)
            ]
            
            # REGRA: Limite por Horário
            if len(reservas_neste_horario) >= QUANTIDADE_TOTAL_PROJETORES:
                erros_encontrados.append(f"❌ {hora}: Todos os {QUANTIDADE_TOTAL_PROJETORES} aparelhos ocupados.")
            else:
                # REGRA: Conflito de Turma
                for turma in turmas_selecionadas:
                    conflito = reservas_neste_horario[reservas_neste_horario["Turmas"].str.contains(turma, na=False)]
                    if not conflito.empty:
                        prof_conflito = conflito.iloc[0]['Professor']
                        erros_encontrados.append(f"⚠️ {hora}: Turma {turma} já reservada por {prof_conflito}.")

        if erros_encontrados:
            for erro in erros_encontrados:
                st.error(erro)
        else:
            st.success(f"✅ Disponível para agendamento.")
            pode_salvar = True
    elif nome_prof == "Selecione seu nome...":
        st.warning("👈 Selecione seu nome na lista para continuar.")

    st.write("")
    
    if st.button("CONFIRMAR AGENDAMENTO"):
        if not pode_salvar:
            st.error("Corrija os erros acima antes de prosseguir.")
        else:
            novas_reservas = []
            lista_horarios_msg = ""
            turmas_texto = ", ".join(turmas_selecionadas)

            for hora in horarios_selecionados:
                novas_reservas.append({
                    "Professor": nome_prof,
                    "Data": str(data_escolhida),
                    "Horario": hora,
                    "Nivel": nivel_selecionado,
                    "Turmas": turmas_texto,
                    "DataRegistro": str(date.today())
                })
                lista_horarios_msg += f"\n⏰ {hora}"

            salvar_multiplas_reservas(novas_reservas)
            
            msg_base = f"*RESERVA DATASHOW CMJP* 🏫\n\n*Prof:* {nome_prof}\n*Data:* {data_escolhida.strftime('%d/%m/%Y')}\n*Turmas:* {turmas_texto}\n*Horários:*{lista_horarios_msg}"
            msg_enc = urllib.parse.quote(msg_base)
            
            st.balloons()
            st.success("✅ Reserva salva com sucesso!")
            
            col_z1, col_z2, col_z3 = st.columns(3)
            with col_z1:
                st.markdown(f"<a href='https://wa.me/{ZAP_GILMAR}?text={msg_enc}' target='_blank'><button style='background-color:#d9534f; color:white; border:none; padding:10px; width:100%; border-radius:5px;'>🚨 AVISE SEU GILMAR</button></a>", unsafe_allow_html=True)
            with col_z2:
                st.markdown(f"<a href='https://wa.me/{ZAP_EDSON}?text={msg_enc}' target='_blank'><button style='background-color:#D4AF37; color:#003366; border:none; padding:10px; width:100%; border-radius:5px;'>Coord. Médio</button></a>", unsafe_allow_html=True)
            with col_z3:
                st.markdown(f"<a href='https://wa.me/{ZAP_LOURDINHA}?text={msg_enc}' target='_blank'><button style='background-color:#D4AF37; color:#003366; border:none; padding:10px; width:100%; border-radius:5px;'>Coord. Fund.</button></a>", unsafe_allow_html=True)

    st.divider()
    st.subheader(f"📅 Agenda: {data_escolhida.strftime('%d/%m/%Y')}")
    filtro_hoje = df_reservas[df_reservas["Data"] == str(data_escolhida)]
    
    if not filtro_hoje.empty:
        filtro_hoje = filtro_hoje.sort_values("Horario")
        st.dataframe(filtro_hoje[["Horario", "Turmas", "Professor"]], hide_index=True, use_container_width=True)
    else:
        st.info("Nenhuma reserva registrada para esta data.")

# ==================================================
# FLUXO 2: ADMINISTRADOR
# ==================================================
elif modo_acesso == "Administrador":
    st.markdown("## 🔒 Painel de Gestão")
    senha = st.text_input("Senha de Acesso:", type="password")
    
    if senha == SENHA_ADMIN:
        st.success("Acesso Autenticado")
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗑️ Gerenciar", "⚙️ Estoque"])
        
        with tab1:
            st.markdown("### Indicadores de Uso")
            df_dash = carregar_dados()
            if not df_dash.empty:
                col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
                col_kpi1.metric("Total Reservas", len(df_dash))
                col_kpi3.metric("Top Professor", df_dash['Professor'].mode()[0] if not df_dash.empty else "-")
                
                st.divider()
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    fig_pizza = px.pie(df_dash, names='Nivel', hole=0.4)
                    st.plotly_chart(fig_pizza, use_container_width=True)
                with col_g2:
                    contagem = df_dash['Professor'].value_counts().head(10).reset_index()
                    contagem.columns = ['Professor', 'Qtd']
                    fig_bar = px.bar(contagem, x='Qtd', y='Professor', orientation='h')
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Sem dados para gráficos.")

        with tab2:
            st.markdown("### Banco de Dados")
            df_atual = carregar_dados()
            df_editado = st.data_editor(df_atual, num_rows="dynamic", use_container_width=True, key="adm_editor")
            if st.button("💾 SALVAR ALTERAÇÕES"):
                salvar_dataframe_completo(df_editado)
                st.success("Atualizado!")
                st.rerun()

        with tab3:
            st.markdown("### Configurações de Estoque")
            st.info("Nota: A lista de professores é fixa no sistema.")
            novo_total = st.number_input("Total Data Shows:", value=int(QUANTIDADE_TOTAL_PROJETORES))
            
            if st.button("Atualizar Estoque"):
                salvar_config_qtd(novo_total)
                st.success("Quantidade Atualizada!")
                st.rerun()
    elif senha != "":
        st.error("Senha incorreta.")
