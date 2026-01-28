import streamlit as st
import pandas as pd
import os
from datetime import date
import urllib.parse
import json
from PIL import Image

# --- CONFIGURAÇÕES DA PÁGINA ---
# ATENÇÃO: Esta deve ser sempre a primeira linha de comando Streamlit
st.set_page_config(page_title="Reserva CMJP", page_icon="🏫", layout="wide")

# --- ESTILOS VISUAIS ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    h1, h2, h3 { color: #003366 !important; text-align: center; }
    
    /* Botão Principal Dourado */
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

# --- CARREGA DADOS INICIAIS ---
config = carregar_config()
QUANTIDADE_TOTAL_PROJETORES = config.get("total_projetores", 3)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # 1. Logo no topo
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    elif os.path.exists("Logo.jpg"): # Tenta com maiúscula caso o windows tenha alterado
        st.image("Logo.jpg", use_container_width=True)
    
    st.divider()
    
    # 2. Informação rápida
    st.info(f"Equipamentos na Escola: **{QUANTIDADE_TOTAL_PROJETORES}**")
    
    # 3. Espaçador para empurrar o menu para baixo
    st.write("")
    st.write("")
    st.write("")
    st.markdown("---")
    
    # 4. MENU DE ACESSO DISCRETO (No final)
    st.caption("Configurações do Sistema")
    modo_acesso = st.selectbox(
        "Alterar Modo de Visualização", 
        ["Professor", "Administrador"], 
        index=0  # O índice 0 garante que 'Professor' seja o padrão
    )

# ==================================================
# ÁREA DO PROFESSOR (PADRÃO)
# ==================================================
if modo_acesso == "Professor":
    
    st.markdown("<h2 style='text-align: center; color: #003366;'>Reserva de Data Show</h2>", unsafe_allow_html=True)
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

    # VERIFICAÇÃO
    if horarios_selecionados:
        st.info("🔎 Verificando disponibilidade...")
        horarios_com_problema = []
        for hora in horarios_selecionados:
            reservas_na_hora = df_reservas[
                (df_reservas["Data"] == str(data_escolhida)) & 
                (df_reservas["Horario"] == hora)
            ]
            qtd_livre = QUANTIDADE_TOTAL_PROJETORES - len(reservas_na_hora)
            if qtd_livre <= 0:
                horarios_com_problema.append(hora)

        if horarios_com_problema:
            st.error(f"❌ ESGOTADO para: {', '.join(horarios_com_problema)}")
            pode_salvar = False
        else:
            st.success("✅ Disponível!")
            pode_salvar = True
    else:
        pode_salvar = False

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
            st.error("⚠️ Horários indisponíveis.")
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
            st.success("Reserva Realizada! Escolha para quem enviar:")
            
            # Botões de WhatsApp
            st.markdown(f"""
            <a href="{link_gilmar}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#d9534f; color:white; padding:15px; border-radius:10px; text-align:center; margin-bottom:10px; font-weight:bold;">
                    🚨 1. ENVIAR PARA SEU GILMAR (OBRIGATÓRIO)
                </div>
            </a>
            """, unsafe_allow_html=True)
            
            c_z1, c_z2 = st.columns(2)
            with c_z1: st.markdown(f"<a href='{link_edson}' target='_blank'><div style='background-color:#D4AF37; color:#003366; padding:10px; border-radius:5px; text-align:center;'><strong>2. Coord. Médio</strong></div></a>", unsafe_allow_html=True)
            with c_z2: st.markdown(f"<a href='{link_lourdinha}' target='_blank'><div style='background-color:#D4AF37; color:#003366; padding:10px; border-radius:5px; text-align:center;'><strong>3. Coord. Fund.</strong></div></a>", unsafe_allow_html=True)

    # TABELA FINAL
    st.divider()
    st.subheader(f"📅 Agenda do dia {data_escolhida}")
    filtro_hoje = df_reservas[df_reservas["Data"] == str(data_escolhida)]
    if not filtro_hoje.empty:
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
        
        # ABA 1: QUANTIDADE
        with st.expander("⚙️ Alterar Quantidade de Aparelhos", expanded=True):
            novo_total = st.number_input("Total de Data Shows disponíveis:", min_value=0, value=int(QUANTIDADE_TOTAL_PROJETORES))
            if st.button("Salvar Nova Quantidade"):
                config["total_projetores"] = novo_total
                salvar_config(config)
                st.success("Quantidade Atualizada!")
                st.rerun()

        # ABA 2: LIMPEZA
        st.markdown("### 🗑️ Cancelar / Excluir Reservas")
        st.warning("Marque a caixa 'delete' na direita para apagar e clique no botão abaixo.")
        
        df_atual = carregar_dados()
        df_editado = st.data_editor(df_atual, num_rows="dynamic", use_container_width=True, key="admin_editor")
        
        if st.button("💾 SALVAR EXCLUSÕES"):
            salvar_dataframe_completo(df_editado)
            st.success("Banco de dados atualizado!")
            st.rerun()
            
    elif senha != "":
        st.error("Senha incorreta.")
