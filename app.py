import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

st.set_page_config(page_title="Gestão Financeira Pessoal", page_icon="💰", layout="wide")

# Ler diretamente dos Secrets do Streamlit
# Credenciais diretas com fallback
SUPABASE_URL = "https://zisxtwbqapabezwtnfrt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inppc3h0d2JxYXBhYmV6d3RuZnJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE4MDc2M3QsImV4cCI6MjA4NzM4MzYzNH0.Qldjmw-9v68u7jvyjp12LA4djOhnPI9CqtgQy9gbNvQ"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("📊 Gestão Financeira Pessoal")

# Obter dados
try:
    contas_res = supabase.from_("contas").select("*").execute()
    cartoes_res = supabase.from_("cartoes").select("*").execute()
    transacoes_res = supabase.from_("transacoes").select("*").order("data_transacao", desc=True).execute()

    df_contas = pd.DataFrame(contas_res.data) if contas_res.data else pd.DataFrame()
    df_cartoes = pd.DataFrame(cartoes_res.data) if cartoes_res.data else pd.DataFrame()
    df_transacoes = pd.DataFrame(transacoes_res.data) if transacoes_res.data else pd.DataFrame()
except Exception as e:
    st.error(f"Erro ao carregar dados do Supabase: {e}")
    df_contas, df_cartoes, df_transacoes = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Secção de Contas e Cartões
st.subheader("🏦 Contas & Cartões")
col_bancos, col_cartoes = st.columns(2)

with col_bancos:
    st.markdown("### 🏛️ Saldos em Conta")
    if not df_contas.empty:
        for _, row in df_contas.iterrows():
            saldo = float(row.get('saldo_inicial', 0.0) or 0.0)
            st.info(f"**{row['nome']}**: R$ {saldo:,.2f}")
    else:
        st.write("Sem contas registadas.")

with col_cartoes:
    st.markdown("### 💳 Cartões de Crédito")
    if not df_cartoes.empty:
        for _, row in df_cartoes.iterrows():
            st.warning(f"**{row['nome']}** | Fecho: dia {row.get('dia_fechamento', '-')} | Vencimento: dia {row.get('dia_vencimento', '-')}")
    else:
        st.write("Sem cartões registados.")

st.markdown("---")
st.subheader("📋 Transações Registadas")

if not df_transacoes.empty:
    col_kpi1, col_kpi2 = st.columns(2)
    total_despesas = df_transacoes[df_transacoes['tipo'] == 'despesa']['valor'].sum() if 'tipo' in df_transacoes.columns else df_transacoes['valor'].sum()
    col_kpi1.metric("Total Lançado", f"R$ {total_despesas:,.2f}")
    col_kpi2.metric("Qtd. Transações", len(df_transacoes))
    
    colunas_exibir = [c for c in ['data_transacao', 'descricao', 'valor', 'categoria', 'forma_pagamento'] if c in df_transacoes.columns]
    st.dataframe(df_transacoes[colunas_exibir], use_container_width=True)
else:
    st.info("Ainda não existem transações registadas.")
