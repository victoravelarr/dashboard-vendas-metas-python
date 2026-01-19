# 1. importar bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px


# 2. carregar base de dados
df = pd.read_excel("base_vendas_com_metas.xlsx")


# 3. tratar dados
df["faturamento"] = df["valor_unitario"] * df["quantidade"]
df["ano"] = df["data"].dt.year
df["mes"] = df["data"].dt.month


# 4. título e descrição
st.title("Resumo de Vendas e Atingimento de Metas")
st.caption("Visão geral do faturamento, desempenho por produto e cumprimento de metas")
st.subheader("Filtros")


# 5. filtros
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    meses = st.multiselect("Mês", sorted(df["mes"].unique()))

with col_filtro2:
    anos = st.multiselect("Ano", sorted(df["ano"].unique()))

with col_filtro3:
    produtos = st.multiselect("Produto(s)", sorted(df["produto"].unique()))


if anos:
    df = df[df["ano"].isin(anos)]

if meses:
    df = df[df["mes"].isin(meses)]

if produtos:
    df = df[df["produto"].isin(produtos)]


# 6. cálculos principais (APÓS filtros)
faturamento_total = df["faturamento"].sum()

faturamento_mensal = (df.groupby(["ano", "mes"])["faturamento"].sum().reset_index())

meta_mensal = (df.groupby(["ano", "mes"])["meta_mensal"].first().reset_index())

comparativo = faturamento_mensal.merge(meta_mensal, on=["ano", "mes"])

comparativo["percentual_meta"] = (comparativo["faturamento"] / comparativo["meta_mensal"]) * 100

comparativo["status"] = comparativo["percentual_meta"].apply(lambda x: "Meta batida" if x >= 100 else "Meta não batida")

comparativo = comparativo.sort_values(["ano", "mes"])

faturamento_produto = (df.groupby("produto", as_index=False)["faturamento"].sum())


# 7. métricas
st.divider()

col_fat, col_met = st.columns(2)

with col_fat:
    st.metric("Faturamento total", f"R$ {faturamento_total:,.2f}")

with col_met:
    if not comparativo.empty:
        st.metric("Atingimento médio da meta", f"{comparativo['percentual_meta'].mean():.1f}%")
    else:
        st.metric("Atingimento médio da meta", "—")


col1, col2 = st.columns(2)

with col1:
    st.metric("Quantidade vendida", f"{df['quantidade'].sum():,}")

with col2:
    if df["quantidade"].sum() > 0:
        ticket_medio = faturamento_total / df["quantidade"].sum()
        st.metric("Ticket médio", f"R$ {ticket_medio:,.2f}")
    else:
        st.metric("Ticket médio", "—")


# 8. gráficos
st.subheader("Faturamento x Meta Mensal")
if not comparativo.empty:
    st.bar_chart(comparativo.set_index("mes")[["faturamento", "meta_mensal"]])
else:
    st.info("Selecione filtros para visualizar o comparativo.")


st.subheader("Evolução das Vendas")
if not df.empty:st.bar_chart(df.groupby("data")["faturamento"].sum())


st.subheader("Distribuição do Faturamento por Produto")
if not faturamento_produto.empty:
    fig = px.pie(faturamento_produto, names="produto", values="faturamento", title="Participação no Faturamento por Produto")

    fig.update_traces(textinfo="percent+label", textfont_size=17, textposition="inside")

    fig.update_traces(pull=[0.05 if i == faturamento_produto["faturamento"].idxmax() else 0 for i in range(len(faturamento_produto))])

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhum dado disponível para o gráfico de produtos.")