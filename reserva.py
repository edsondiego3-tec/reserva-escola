import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
import json
from PIL import Image

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫", layout="wide")

# --- ESTILOS VISUAIS ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
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
    "5º Horário (10:30 - 11:20)",
    "6º Horário (11:20 - 12:10)"
]

TURMAS_ESCOLA = {
    "ENSINO FUNDAMENTAL": ["6º ANO", "7º ANO", "8º ANO", "9º ANO"],
    "ENSINO MÉDIO": ["1ª SÉRIE", "2ª SÉRIE", "3ª SÉRIE"]
}

# --- FUNÇÕES ---
def carregar_config():
    if not os.path.exists(ARQUIVO_CONFIG):
        padrao = {"total_projetores": 3}
        try:
            with open(ARQUIVO_CONFIG, "w") as f:
                json.dump(padrao, f)
        except:
            return padrao
        return padrao
    with open(ARQUIVO_CONFIG, "r") as f:
        return json.load(f)

def salvar_config(nova_config):
    with open(ARQUIVO_CONFIG, "w") as f:
        json.dump(nova_config, f)

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return pd.DataFrame(columns=["Professor", "Data", "Horario", "Nivel", "Turmas", "DataRegistro"])
    return pd.read_csv(ARQUIVO_DADOS)

def salvar_multiplas_reservas(lista_reservas):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame(lista_reservas)], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

def salvar_dataframe_completo(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

# --- CARREGAMENTO INICIAL ---
config = carregar_config()
QUANTIDADE_TOTAL_PROJETORES = config.get("total_projetores", 3)

# --- MENU LATERAL ---
with st.sidebar:
    st.header("Ajustes")
    modo_acesso = st.selectbox("Perfil de Acesso", ["Professor", "Administrador"])
    st.divider()
    st.info(f"Aparelhos na Escola: **{QUANTIDADE_TOTAL_PROJETORES}**")


# ==================================================
# ÁREA DO PROFESSOR
# ==================================================
if modo_acesso == "Professor":
    
    # --- LOGO MENOR E CENTRALIZADA ---
    # Colunas 1-1-1 ajudam a centralizar melhor itens pequenos
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1]) 
    with col_l2:
        lista_logos = ["logo.jpg", "Logo.jpg", "logo.png", "logo dourada 3d (1) (1)[2014] - Copia.jpg"]
        logo_encontrada = None
        for nome in lista_logos:
            if os.path.exists(nome):
                logo_encontrada = nome
                break
        
        if logo_encontrada:
            # width=120 deixa a logo bem discreta e menor
            st.image(logo_encontrada, width=120)
            
    st.markdown("<h3 style='text-align: center; color: #003366;'>Reserva de Data Show</h3>", unsafe_allow_html=True)
    st.markdown("---")

    df_reservas = carregar_dados()

    # FORMULÁRIO
    st.subheader("📝 Nova Solicitação")
    
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        nome_prof = st.text_input("Nome do Professor(a)")
        data_escolhida = st.date_input("Data de Uso", min_value=date.today())
        nivel_selecionado = st.selectbox("Nível de Ensino", list(TURMAS_ESCOLA.keys()))

    with col_form2:
        horarios_selecionados = st.multiselect("Selecione os Horários", HORARIOS_AULA)
        turmas_disponiveis = TURMAS_ESCOLA[nivel_selecionado]
        turmas_selecionadas = st.multiselect("Selecione as Turmas", turmas_disponiveis)

    # --- LÓGICA DE VERIFICAÇÃO (CORRIGIDA) ---
    pode_salvar = False
    
    if horarios_selecionados and turmas_selecionadas:
        st.info("🔎 Verificando disponibilidade...")
        
        erros_encontrados = []
        
        for hora in horarios_selecionados:
            # Filtra reservas APENAS para aquele dia E aquele horário específico
            reservas_neste_horario = df_reservas[
                (df_reservas["Data"] == str(data_escolhida)) & 
                (df_reservas["Horario"] == hora)
            ]
            
            # 1. VERIFICA QUANTIDADE (Regra: Máximo 3 por horário)
            qtd_ocupada = len(reservas_neste_horario)
            if qtd_ocupada >= QUANTIDADE_TOTAL_PROJETORES:
                erros_encontrados.append(f"❌ {hora}: Todos os {QUANTIDADE_TOTAL_PROJETORES} aparelhos ocupados.")
            
            # 2. VERIFICA CONFLITO DE TURMA (Regra: Turma não pode ter 2 reservas no mesmo horário)
            else:
                for turma in turmas_selecionadas:
                    conflito = reservas_neste_horario[reservas_neste_horario["Turmas"].str.contains(turma, na=False)]
                    if not conflito.empty:
                        erros_encontrados.append(f"⚠️ {hora}: A turma {turma} já tem reserva.")

        if erros_encontrados:
            for erro in erros_encontrados:
                st.error(erro)
            pode_salvar = False
        else:
            st.success(f"✅ Tudo certo! Aparelhos disponíveis para os horários selecionados.")
            pode_salvar = True
    
    st.write("") 
    
    # BOTÃO CONFIRMAR
    if st.button("CONFIRMAR RESERVAS AGORA"):
        if not nome_prof:
            st.warning("⚠️ Preencha o nome do professor.")
        elif not horarios_selecionados:
            st.warning("⚠️ Selecione pelo menos um horário.")
        elif not turmas_selecionadas:
            st.warning("⚠️ Selecione pelo menos uma turma.")
        elif not pode_salvar:
            st.error("⚠️ Resolva os conflitos acima antes de reservar.")
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
            
            # WhatsApp
            msg_base = f"*RESERVA DATASHOW CMJP* 🏫\n\n*Prof:* {nome_prof}\n*Data:* {data_escolhida}\n*Turmas:* {turmas_texto}\n*Horários:*{lista_horarios_texto}"
            msg_codificada = urllib.parse.quote(msg_base)
            link_gilmar = f"https://wa.me/{ZAP_GILMAR}?text={msg_codificada}"
            link_edson = f"https://wa.me/{ZAP_EDSON}?text={msg_codificada}"
            link_lourdinha = f"https://wa.me/{ZAP_LOURDINHA}?text={msg_codificada}"

            st.balloons()
            st.success("Reserva Realizada!")
            
            st.markdown(f"""
            <a href="{link_gilmar}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#d9534f; color:white; padding:15px; border-radius:10px; text-align:center; margin-bottom:10px; font-weight:bold; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                    🚨 1. ENVIAR PARA SEU GILMAR (OBRIGATÓRIO)
                </div>
            </a>
            """, unsafe_allow_html=True)
            
            c_z1, c_z2 = st.columns(2)
            with c_z1: st.markdown(f"<a href='{link_edson}' target='_blank' style='text-decoration:none;'><div style='background-color:#D4AF37; color:#003366; padding:10px; border-radius:5px; text-align:center; border:1px solid #003366;'><strong>2. Coord. Médio</strong></div></a>", unsafe_allow_html=True)
            with c_z2: st.markdown(f"<a href='{link_lourdinha}' target='_blank' style='text-decoration:none;'><div style='background-color:#D4AF37; color:#003366; padding:10px; border-radius:5px; text-align:center; border:1px solid #003366;'><strong>3. Coord. Fund.</strong></div></a>", unsafe_allow_html=True)

    # TABELA FINAL
    st.divider()
    st.subheader(f"📅 Agenda do dia {data_escolhida}")
    filtro_hoje = df_reservas[df_reservas["Data"] == str(data_escolhida)]
    if not filtro_hoje.empty:
        # Ordena para ficar bonito
        filtro_hoje = filtro_hoje.sort_values("Horario")
        st.table(filtro_hoje[["Horario", "Turmas", "Professor"]])
    else:
        st.info("Nenhuma reserva para esta data ainda.")

# ==================================================
# ÁREA DO ADMINISTRADOR
# ==================================================
elif modo_acesso == "Administrador":
    
    st.markdown("## 🔒 Painel Administrativo")
    st.info("Área exclusiva para Coordenação.")
    
    senha = st.text_input("Digite a Senha:", type="password")
    
    if senha == SENHA_ADMIN:
        st.success("Acesso Liberado")
        
        with st.expander("⚙️ Quantidade de Aparelhos", expanded=True):
            novo_total = st.number_input("Total de Data Shows (Estoque):", min_value=0, value=int(QUANTIDADE_TOTAL_PROJETORES))
            if st.button("Salvar Quantidade"):
                config["total_projetores"] = novo_total
                salvar_config(config)
                st.success("Atualizado!")
                st.rerun()

        st.markdown("### 🗑️ Gerenciar Reservas")
        st.warning("Selecione para excluir e clique em Salvar.")
        
        df_atual = carregar_dados()
        df_editado = st.data_editor(df_atual, num_rows="dynamic", use_container_width=True, key="admin_editor")
        
        if st.button("💾 SALVAR EXCLUSÕES"):
            salvar_dataframe_completo(df_editado)
            st.success("Banco de dados atualizado!")
            st.rerun()
            
    elif senha != "":
        st.error("Senha incorreta.")
