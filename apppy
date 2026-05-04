import streamlit as st
from datetime import date, timedelta
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Desafio 30 Dias", page_icon="🏆", layout="wide")

# === CONFIG ===
PARTICIPANTES = ["Julia", "Amigo1", "Amigo2", "Amigo3"]  # EDITA AQUI
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

# === CONEXÃO ===
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar():
    df = conn.read(worksheet="registros", ttl=5)
    df = df.dropna(how="all")
    return df if not df.empty else pd.DataFrame(columns=["pessoa", "data", "tarefa"])

def salvar_dia(pessoa, dia, marcadas):
    df = carregar()
    df = df[~((df["pessoa"] == pessoa) & (df["data"] == dia.isoformat()))]
    novos = pd.DataFrame([{"pessoa": pessoa, "data": dia.isoformat(), "tarefa": t} for t in marcadas])
    final = pd.concat([df, novos], ignore_index=True)
    conn.update(worksheet="registros", data=final)

# === UI ===
hoje = date.today()
ontem = hoje - timedelta(days=1)

st.title("🏆 Desafio 30 Dias")
st.caption(f"{INICIO.strftime('%d/%m')} → {FIM.strftime('%d/%m')}")

# Sidebar - marcar checklist
st.sidebar.header("Marcar checklist")
pessoa = st.sidebar.selectbox("Quem é você?", PARTICIPANTES)
opcao = st.sidebar.radio("Dia", [f"Hoje ({hoje.strftime('%d/%m')})", f"Ontem ({ontem.strftime('%d/%m')})"])
dia = hoje if "Hoje" in opcao else ontem

if dia < INICIO or dia > FIM:
    st.sidebar.error("Fora do período do desafio")
else:
    df = carregar()
    feitas = df[(df["pessoa"] == pessoa) & (df["data"] == dia.isoformat())]["tarefa"].tolist()
    st.sidebar.write(f"**{dia.strftime('%d/%m')}**")
    marcadas = []
    for t in TAREFAS:
        if st.sidebar.checkbox(t, value=(t in feitas), key=f"{pessoa}-{dia}-{t}"):
            marcadas.append(t)
    if st.sidebar.button("💾 Salvar", type="primary"):
        salvar_dia(pessoa, dia, marcadas)
        st.cache_data.clear()
        st.sidebar.success("Salvo!")
        st.rerun()

# Ranking
df = carregar()
st.subheader("🏆 Ranking")

pontos = {p: len(df[df["pessoa"] == p]) for p in PARTICIPANTES}
dias_ativos = (min(FIM, hoje) - INICIO).days + 1
max_possivel = dias_ativos * len(TAREFAS) if dias_ativos > 0 else 1
ranking = sorted(pontos.items(), key=lambda x: -x[1])
medals = ["🥇", "🥈", "🥉"] + ["🎖️"] * 10

for i, (p, pts) in enumerate(ranking):
    pct = (pts / max_possivel * 100) if max_possivel else 0
    col1, col2, col3 = st.columns([1, 4, 2])
    col1.markdown(f"### {medals[i]}")
    col2.markdown(f"**{p}**")
    col2.progress(min(pct / 100, 1.0))
    col3.metric("", f"{pts} pts", f"{pct:.0f}%")

# Histórico
st.subheader("📅 Histórico")
dias = [INICIO + timedelta(days=i) for i in range((min(FIM, hoje) - INICIO).days + 1)]
linhas = []
for p in PARTICIPANTES:
    linha = {"Pessoa": p}
    for d in dias:
        n = len(df[(df["pessoa"] == p) & (df["data"] == d.isoformat())])
        linha[d.strftime("%d/%m")] = f"{n}/6" if n else "—"
    linhas.append(linha)
st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

# Detalhes
with st.expander("Ver detalhes por pessoa"):
    p_sel = st.selectbox("Pessoa", PARTICIPANTES, key="detalhe")
    df_p = df[df["pessoa"] == p_sel].sort_values("data", ascending=False)
    st.dataframe(df_p, use_container_width=True, hide_index=True)
