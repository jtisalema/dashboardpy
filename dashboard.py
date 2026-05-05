import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Dashboard Hospitalario",
    layout="wide"
)

st.title("Dashboard de Atenciones Hospitalarias")

# Cargar datos
df = pd.read_csv("clinical_analytics.csv")

# Convertir fechas
df["Appt Start Time"] = pd.to_datetime(
    df["Appt Start Time"],
    format="%Y-%m-%d %I:%M:%S %p",
    errors="coerce"
)

df["Check-In Time"] = pd.to_datetime(
    df["Check-In Time"],
    format="%Y-%m-%d %I:%M:%S %p",
    errors="coerce"
)
df["Discharge Datetime new"] = pd.to_datetime(df["Discharge Datetime new"], errors="coerce")

# Limpieza básica
df["Diagnosis Primary"] = df["Diagnosis Primary"].fillna("Sin diagnóstico")
df["Encounter Status"] = df["Encounter Status"].fillna("Sin estado")
df["Department"] = df["Department"].fillna("Sin departamento")

# Sidebar con filtros
st.sidebar.header("Filtros")

departamentos = st.sidebar.multiselect(
    "Departamento",
    options=sorted(df["Department"].dropna().unique()),
    default=sorted(df["Department"].dropna().unique())
)

estado = st.sidebar.multiselect(
    "Estado",
    options=sorted(df["Encounter Status"].dropna().unique()),
    default=sorted(df["Encounter Status"].dropna().unique())
)

# Aplicar filtros
df_filtrado = df[
    (df["Department"].isin(departamentos)) &
    (df["Encounter Status"].isin(estado))
]

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de registros", len(df_filtrado))
col2.metric("Tiempo promedio de espera", round(df_filtrado["Wait Time Min"].mean(), 2))
col3.metric("Care Score promedio", round(df_filtrado["Care Score"].mean(), 2))
col4.metric("Pacientes únicos", df_filtrado["Encounter Number"].nunique())

st.divider()

# Gráficas
col5, col6 = st.columns(2)

with col5:
    st.subheader("Tiempo promedio de espera por departamento")

    espera_depto = (
        df_filtrado
        .groupby("Department", as_index=False)["Wait Time Min"]
        .mean()
        .sort_values("Wait Time Min", ascending=False)
    )

    fig1 = px.bar(
        espera_depto,
        x="Department",
        y="Wait Time Min",
        title="Wait Time promedio por departamento"
    )

    st.plotly_chart(fig1, width="stretch")

with col6:
    st.subheader("Cantidad de registros por estado")

    estado_count = (
        df_filtrado
        .groupby("Encounter Status", as_index=False)["Number of Records"]
        .sum()
        .sort_values("Number of Records", ascending=False)
    )

    fig2 = px.pie(
        estado_count,
        names="Encounter Status",
        values="Number of Records",
        title="Distribución por estado"
    )

    st.plotly_chart(fig2, width="stretch")

col7, col8 = st.columns(2)

with col7:
    st.subheader("Care Score por departamento")

    fig3 = px.box(
        df_filtrado,
        x="Department",
        y="Care Score",
        title="Distribución del Care Score"
    )

    st.plotly_chart(fig3, width="stretch")

with col8:
    st.subheader("Registros por mes")

    df_filtrado["Mes"] = df_filtrado["Appt Start Time"].dt.to_period("M").astype(str)

    registros_mes = (
        df_filtrado
        .groupby("Mes", as_index=False)["Number of Records"]
        .sum()
    )

    fig4 = px.line(
        registros_mes,
        x="Mes",
        y="Number of Records",
        markers=True,
        title="Evolución mensual de registros"
    )

    st.plotly_chart(fig4, width="stretch")

st.divider()

# Tabla final
st.subheader("Datos filtrados")
st.dataframe(df_filtrado, width="stretch")