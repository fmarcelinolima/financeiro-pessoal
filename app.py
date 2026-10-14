import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

st.set_page_config(page_title="Gestão Financeira Pessoal", page_icon="💰", layout="wide")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://zisxtwbqapabezwtnfrt.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inppc3h0d2JxYXBhYmV6d3RuZnJ0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MTgwNzYzNCwiZXhwIjoyMDg3MzgzNjM0fQ.2dJzYXBhyMv6d3RuZnJ0iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsInNlb2I6MTc5MDYwMDk2MCwiZXhwIjoyMTA2Mzk2MzYwfq.9FSNJBU2TyvS1IZS6VBVNRhpJiVHxMIgtK72dbMY1I4")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("📊 Gestão Financeira Pessoal")

# Obter dados
contas_res = supabase.from_("contas").select("*").execute()
cartoes_res = supabase.from_("cartoes").select("*").execute()
transacoes_res = supabase.from_("transacoes").select("*").order("data_transacao", desc=True).execute()

df_contas = pd.DataFrame(contas_res.data) if contas_res.data else pd.DataFrame()
df_cartoes = pd.DataFrame(cartoes_res.data) if cartoes_res.data else pd.DataFrame()
df_transacoes = pd.DataFrame(transacoes_res.data) if transacoes_res.data else pd.DataFrame()

# Secção de Contas e Cartões
st.subheader("🏦 Contas & Cartões")
col_bancos, col_cartoes = st.columns(2)

with col_bancos:
    st.markdown("### 🏛️ Saldos em Conta")
    if not df_contas.empty:
        for _, row in df_contas.iterrows():
            saldo = float(row.get('saldo_atual', 0.0) or 0.0)
            st.info(f"**{row['nome']}**: R$ {saldo:,.2f}")
    else:
        st.write("Sem contas registadas.")

with col_cartoes:
    st.markdown("### 💳 Cartões de Crédito")
    if not df_cartoes.empty:
        for _, row in df_cartoes.iterrows():
            limite = float(row.get('limite', 0.0) or 0.0)
            st.success(f"**{row['nome']}** | Limite: R$ {limite:,.2f} *(Fecho dia {row.get('dia_fechamento', '-')})*")
    else:
        st.write("Sem cartões registados.")

st.divider()

# Gráficos e Transações
if not df_transacoes.empty:
    df_transacoes['origem'] = df_transacoes.apply(
        lambda r: r['cartoes']['nome'] if r.get('forma_pagamento') == 'cartao' and r.get('cartoes') else (r['contas']['nome'] if r.get('contas') else '-'),
        axis=1
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("📉 Despesas por Categoria")
        df_despesas = df_transacoes[df_transacoes['tipo'] == 'despesa']
        if not df_despesas.empty:
            fig_cat = px.pie(
                df_despesas,
                values='valor',
                names='categoria',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Sem despesas registadas.")

    with c2:
        st.subheader("💳 Gastos por Origem")
        if not df_despesas.empty:
            fig_origem = px.bar(
                df_despesas.groupby('origem')['valor'].sum().reset_index(),
                x='origem',
                y='valor',
                labels={'valor': 'Total (R$)', 'origem': 'Conta / Cartão'},
                color='origem'
            )
            st.plotly_chart(fig_origem, use_container_width=True)

    st.subheader("📋 Histórico Recente de Transações")
    
    # Exibição linha a linha por containers nativos (100% compatível com telemóvel e túneis)
    for _, item in df_transacoes.iterrows():
        tipo_icone = "🔴" if item['tipo'] == 'despesa' else "🟢"
        origem_str = item['origem']
        valor_float = float(item['valor'] or 0.0)
        
        col_desc, col_cat, col_origem, col_val = st.columns([3, 3, 2, 2])
        with col_desc:
            st.write(f"{tipo_icone} **{item['descricao']}**  \n<small>{item['data_transacao']}</small>", unsafe_allow_html=True)
        with col_cat:
            st.write(f"🏷️ {item['categoria']}")
        with col_origem:
            st.write(f"💳 {origem_str}")
        with col_val:
            st.write(f"**R$ {valor_float:,.2f}**")
        st.divider()

else:
    st.info("Ainda não existem transações registadas.")
