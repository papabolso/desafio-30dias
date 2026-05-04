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
    .stButton button { background-color: #2a2520 !important; color: #f5f0e6 !important; border: none; border-radius: 6px; font-weight: 600; }
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

def toggle_tarefa(pessoa, dia, tarefa):
    payload = {
        "action": "toggle",
        "pessoa": pessoa,
        "data": dia.isoformat(),
        "tarefa": tarefa,
    }
    r = requests.post(URL, json=payload, timeout=15)
    return r.json().get("ok", False)

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

# === CHECKLIST ===
if dia < INICIO or dia > FIM:
    st.error("Fora do período do desafio")
else:
    feitas_salvas = set(df[(df["pessoa"] == pessoa) & (df["data"] == dia.isoformat())]["tarefa"].tolist())
    
    st.subheader(f"Checklist — {pessoa}")
    st.markdown(f"""
    <div class="checklist-box">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div style="font-size:1.2rem; font-weight:700;">📅 {dia.strftime('%d/%m/%Y')}</div>
            <div style="font-size:1rem; color:#6b5d48; font-weight:600;">{len(feitas_salvas)}/{len(TAREFAS)} feitas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Cada clique salva automaticamente. Clica de novo pra desmarcar.")
    
    cols = st.columns(2)
    for idx, t in enumerate(TAREFAS):
        with cols[idx % 2]:
            estava = t in feitas_salvas
            agora = st.checkbox(t, value=estava, key=f"{pessoa}-{dia}-{t}")
            if agora != estava:
                with st.spinner("Salvando..."):
                    if toggle_tarefa(pessoa, dia, t):
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Erro ao salvar")

# === Ranking ===
st.subheader("Ranking")
pontos = {p: len(df[df["pessoa"] == p]) for p in todos_participantes}
dias_ativos = (min(FIM, hoje) - INICIO).days + 1
max_possivel = dias_ativos * len(TAREFAS) if dias_ativos > 0 else 1
ranking = sorted(pontos.items(), key=lambda x: -x[1])
medals = ["🥇", "🥈", "🥉"]
classes = ["gold", "silver", "bronze"]

for i, (p, pts) in enumerate(ranking):
    pct = (pts / max_possivel * 100) if max_possivel else 0
    if i < 3:
        pos = medals[i]
        cls = classes[i]
    else:
        pos = f"{i+1}º"
        cls = ""
    
    st.markdown(f"""
    <div class="rank-card {cls}">
        <div class="rank-pos">{pos}</div>
        <div class="rank-info">
            <div class="rank-name">{p}</div>
            <div class="rank-bar"><div class="rank-bar-fill" style="width: {min(pct, 100)}%;"></div></div>
        </div>
        <div class="rank-stats">
            <div class="rank-pts">{pts} pts</div>
            <div class="rank-pct">{pct:.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Histórico ===
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

with st.expander("Ver detalhes por pessoa"):
    p_sel = st.selectbox("Pessoa", todos_participantes, key="detalhe")
    df_p = df[df["pessoa"] == p_sel].sort_values("data", ascending=False)
    st.dataframe(df_p, use_container_width=True, hide_index=True)
