import streamlit as st
from datetime import date, timedelta
import pandas as pd
import requests

st.set_page_config(page_title="Desafio 30 Dias", page_icon="🏆", layout="centered")

# === CSS minimalista ===
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    section[data-testid="stSidebar"] { background-color: #fafafa; }
    h1, h2, h3 { color: #1a1a1a; font-weight: 600; }
    .stButton button { 
        background-color: #1a1a1a; color: white; border: none; 
        border-radius: 6px; font-weight: 500;
    }
    .stButton button:hover { background-color: #333; color: white; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    .stProgress > div > div > div { background-color: #1a1a1a; }
    div[data-testid="stExpander"] { border: 1px solid #e5e5e5; border-radius: 8px; }
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
@st.cache_data(ttl=10)
def carregar():
    r = requests.get(URL, timeout=15)
    rows = r.json()
    if len(rows) <= 1:
        return pd.DataFrame(columns=["pessoa", "data", "tarefa"])
    return pd.DataFrame(rows[1:], columns=rows[0])

def salvar_dia(pessoa, dia, marcadas):
    payload = {
        "action": "save_day",
        "pessoa": pessoa,
        "data": dia.isoformat(),
        "tarefas": marcadas,
    }
    r = requests.post(URL, json=payload, timeout=15)
    return r.json().get("ok", False)

# === UI ===
hoje = date.today()
ontem = hoje - timedelta(days=1)

st.title("🏆 Desafio 30 Dias")
st.caption(f"{INICIO.strftime('%d/%m')} → {FIM.strftime('%d/%m')}")

df = carregar()

# Lista de participantes = quem já tem registro + quem foi adicionado nessa sessão
participantes_existentes = sorted(df["pessoa"].unique().tolist()) if not df.empty else []
if "novos_participantes" not in st.session_state:
    st.session_state.novos_participantes = []
todos_participantes = sorted(set(participantes_existentes + st.session_state.novos_participantes))

# Sidebar
st.sidebar.header("Marcar checklist")

# Adicionar pessoa
with st.sidebar.expander("➕ Entrar no desafio"):
    novo = st.text_input("Seu nome", key="novo_nome")
    if st.button("Adicionar"):
        nome = novo.strip()
        if not nome:
            st.warning("Digita um nome")
        elif nome in todos_participantes:
            st.warning("Nome já existe")
        else:
            st.session_state.novos_participantes.append(nome)
            st.success(f"{nome} adicionado!")
            st.rerun()

if not todos_participantes:
    st.sidebar.info("Adicione um participante pra começar")
    st.info("Ninguém entrou no desafio ainda. Use a sidebar pra adicionar seu nome.")
    st.stop()

pessoa = st.sidebar.selectbox("Quem é você?", todos_participantes)
opcao = st.sidebar.radio("Dia", [f"Hoje ({hoje.strftime('%d/%m')})", f"Ontem ({ontem.strftime('%d/%m')})"])
dia = hoje if "Hoje" in opcao else ontem

if dia < INICIO or dia > FIM:
    st.sidebar.error("Fora do período do desafio")
else:
    feitas = df[(df["pessoa"] == pessoa) & (df["data"] == dia.isoformat())]["tarefa"].tolist()
    st.sidebar.write(f"**{dia.strftime('%d/%m')}**")
    marcadas = []
    for t in TAREFAS:
        if st.sidebar.checkbox(t, value=(t in feitas), key=f"{pessoa}-{dia}-{t}"):
            marcadas.append(t)
    if st.sidebar.button("Salvar", type="primary"):
        if salvar_dia(pessoa, dia, marcadas):
            st.cache_data.clear()
            st.sidebar.success("Salvo!")
            st.rerun()
        else:
            st.sidebar.error("Erro ao salvar")

# Ranking
st.subheader("Ranking")

pontos = {p: len(df[df["pessoa"] == p]) for p in todos_participantes}
dias_ativos = (min(FIM, hoje) - INICIO).days + 1
max_possivel = dias_ativos * len(TAREFAS) if dias_ativos > 0 else 1
ranking = sorted(pontos.items(), key=lambda x: -x[1])
medals = ["🥇", "🥈", "🥉"] + ["·"] * 20

for i, (p, pts) in enumerate(ranking):
    pct = (pts / max_possivel * 100) if max_possivel else 0
    col1, col2, col3 = st.columns([1, 4, 2])
    col1.markdown(f"### {medals[i]}")
    col2.markdown(f"**{p}**")
    col2.progress(min(pct / 100, 1.0))
    col3.metric("", f"{pts} pts", f"{pct:.0f}%")

# Histórico
st.subheader("Histórico")
dias = [INICIO + timedelta(days=i) for i in range((min(FIM, hoje) - INICIO).days + 1)]
linhas = []
for p in todos_participantes:
    linha = {"Pessoa": p}
    for d in dias:
        n = len(df[(df["pessoa"] == p) & (df["data"] == d.isoformat())])
        linha[d.strftime("%d/%m")] = f"{n}/6" if n else "—"
    linhas.append(linha)
st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

# Detalhes
with st.expander("Ver detalhes por pessoa"):
    p_sel = st.selectbox("Pessoa", todos_participantes, key="detalhe")
    df_p = df[df["pessoa"] == p_sel].sort_values("data", ascending=False)
    st.dataframe(df_p, use_container_width=True, hide_index=True)
