import streamlit as st
from datetime import date, timedelta
import pandas as pd
import requests

st.set_page_config(page_title="Desafio 30 Dias", page_icon="🏆", layout="centered")

# === CSS ===
st.markdown("""
<style>
    .stApp { background-color: #f5f0e6; color: #2a2520; }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div { color: #2a2520; }
    section[data-testid="stSidebar"] { background-color: #ebe3d3; border-right: 1px solid #d4c8b0; }
    section[data-testid="stSidebar"] * { color: #2a2520 !important; }
    h1, h2, h3, h4 { color: #2a2520 !important; font-weight: 700 !important; }
    .stApp [data-testid="stCaptionContainer"], .stApp small { color: #6b5d48 !important; }
    .stButton button { background-color: #2a2520 !important; color: #f5f0e6 !important; border: none; border-radius: 6px; font-weight: 600; padding: 0.6rem 1.2rem; }
    .stButton button:hover { background-color: #4a4035 !important; color: #f5f0e6 !important; }
    .stButton button * { color: #f5f0e6 !important; }
    .stProgress > div > div > div > div { background-color: #2a2520 !important; }
    .stProgress > div > div > div { background-color: #d4c8b0 !important; }
    div[data-testid="stExpander"] { border: 1px solid #d4c8b0; border-radius: 8px; background-color: #faf6ed; }
    div[data-testid="stExpander"] summary { color: #2a2520 !important; font-weight: 600; }
    .stDataFrame { border: 1px solid #d4c8b0; border-radius: 6px; }
    .stDataFrame * { color: #2a2520 !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        color: #2a2520 !important; border-color: #b8a888 !important; background-color: #faf6ed !important;
    }
    .stCheckbox label, .stCheckbox label p { color: #2a2520 !important; font-weight: 500; font-size: 1.05rem !important; }
    .stRadio label, .stRadio label p { color: #2a2520 !important; }
    
    .checklist-box {
        background-color: #faf6ed; border: 1px solid #d4c8b0; border-radius: 12px;
        padding: 18px 22px; margin-bottom: 16px;
    }
    
    .rank-card {
        background-color: #faf6ed; border: 1px solid #d4c8b0; border-radius: 10px;
        padding: 14px 18px; margin-bottom: 10px; display: flex; align-items: center; gap: 16px;
    }
    .rank-card.gold { background-color: #f5e9c8; border-color: #d4b96a; }
    .rank-card.silver { background-color: #ece7dd; border-color: #b8b0a0; }
    .rank-card.bronze { background-color: #ecd9c0; border-color: #b89060; }
    .rank-pos { font-size: 1.8rem; font-weight: 700; min-width: 50px; text-align: center; }
    .rank-info { flex: 1; }
    .rank-name { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
    .rank-bar { background-color: #d4c8b0; height: 8px; border-radius: 4px; overflow: hidden; }
    .rank-bar-fill { background-color: #2a2520; height: 100%; border-radius: 4px; }
    .rank-stats { text-align: right; min-width: 90px; }
    .rank-pts { font-size: 1.3rem; font-weight: 700; line-height: 1; }
    .rank-pct { font-size: 0.85rem; color: #6b5d48; margin-top: 2px; }
    
    .unsaved {
        background-color: #f0d8b0; border-left: 4px solid #c47e3a;
        padding: 10px 14px; border-radius: 4px; font-weight: 600; margin: 12px 0;
    }
    .saved {
        background-color: #dde8c8; border-left: 4px solid #6a8a3a;
        padding: 10px 14px; border-radius: 4px; margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# === CONFIG ===
TAREFAS = [
    "30min+ exercício",
    "2L+ água",
    "Sem açúcar",
    "5h+ sono",
    "<6h tela",
    "1+ fruta",
]
INICIO = date(2026, 5, 4)
FIM = date(2026, 6, 3)

URL = st.secrets["gsheets"]["apps_script_url"]

# === BACKEND ===
@st.cache_data(ttl=5)
def carregar():
    r = requests.get(URL, timeout=15)
    rows = r.json()
    if len(rows) <= 1:
        return pd.DataFrame(columns=["pessoa", "data", "tarefa"])
    return pd.DataFrame(rows[1:], columns=rows[0])

def sync_dia(pessoa, dia, marcadas):
    payload = {
        "action": "sync_day",
        "pessoa": pessoa,
        "data": dia.isoformat(),
        "tarefas": marcadas,
    }
    try:
        r = requests.post(URL, json=payload, timeout=20)
        st.write("**DEBUG status:**", r.status_code)
        st.write("**DEBUG resposta bruta:**", r.text[:500])
        try:
            return r.json().get("ok", False)
        except Exception as e:
            st.error(f"Resposta não é JSON: {e}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

# === UI ===
hoje = date.today()
ontem = hoje - timedelta(days=1)

st.title("🏆 Desafio 30 Dias")
st.caption(f"{INICIO.strftime('%d/%m')} → {FIM.strftime('%d/%m')}")

df = carregar()

participantes_existentes = sorted(df["pessoa"].unique().tolist()) if not df.empty else []
if "novos_participantes" not in st.session_state:
    st.session_state.novos_participantes = []
todos_participantes = sorted(set(participantes_existentes + st.session_state.novos_participantes))

# === SIDEBAR ===
st.sidebar.header("Configuração")

with st.sidebar.expander("➕ Entrar no desafio"):
    novo = st.text_input("Seu nome", key="novo_nome")
    if st.button("Adicionar"):
        nome = novo.strip()
        if not nome:
            st.warning("Digita um nome")
        elif nome in todos_part
