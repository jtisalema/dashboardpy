import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CAMBIO:
# st.set_page_config() debe ir antes de cualquier elemento Streamlit
# =========================================================
st.set_page_config(
    page_title="Dashboard Hospitalario",
    layout="wide"
)

# =========================================================
# PORTADA
# =========================================================
st.markdown("""
<div style="text-align: center;">
  <img src="https://www.uide.edu.ec/wp-content/uploads/2025/06/logo-uide.webp" width="150" style="display: block; margin: 0 auto;">
  <h1>Maestría en Ciencia de Datos</h1>
  <hr>
  <h2>Trabajo Práctico - Clase 3</h2>
  <h3>Semana: W3 - Componente Práctico 3</h3>
  <h3>Equipo: G8</h3>
  <p><b>Fecha:</b> 05 Mayo 2026</p>
</div>

<br>

<b>Integrantes:</b>
<ul>
<li>JONATHAN FERNANDO TISALEMA LASCANO</li>
<li>JHAIR JOSUE ALARCON QUINTEROS</li>
<li>ADRIAN OLIDER CAICEDO SANTOS</li>
</ul>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# TÍTULO PRINCIPAL
# =========================================================
st.title("Dashboard de Atenciones Hospitalarias")

# =========================================================
# CARGA DE DATOS
# =========================================================
df = pd.read_csv("clinical_analytics.csv")

# =========================================================
# CONVERSIÓN DE FECHAS
# =========================================================
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

df["Discharge Datetime new"] = pd.to_datetime(
    df["Discharge Datetime new"],
    errors="coerce"
)

# =========================================================
# LIMPIEZA BÁSICA
# =========================================================
df["Diagnosis Primary"] = df["Diagnosis Primary"].fillna("Sin diagnóstico")
df["Encounter Status"] = df["Encounter Status"].fillna("Sin estado")
df["Department"] = df["Department"].fillna("Sin departamento")
df["Clinic Name"] = df["Clinic Name"].fillna("Sin clínica")

# =========================================================
# SIDEBAR - FILTROS
# =========================================================
st.sidebar.header("Filtros")

# =========================================================
# FILTRO 1 - DEPARTAMENTO
# =========================================================
departamentos = st.sidebar.multiselect(
    "Departamento",
    options=sorted(df["Department"].dropna().unique()),
    default=sorted(df["Department"].dropna().unique())
)

# =========================================================
# FILTRO 2 - ESTADO
# =========================================================
estado = st.sidebar.multiselect(
    "Estado",
    options=sorted(df["Encounter Status"].dropna().unique()),
    default=sorted(df["Encounter Status"].dropna().unique())
)

# =========================================================
# CAMBIO:
# FILTRO 3 AGREGADO - CLÍNICA
# =========================================================
clinica = st.sidebar.multiselect(
    "Clínica",
    options=sorted(df["Clinic Name"].dropna().unique()),
    default=sorted(df["Clinic Name"].dropna().unique())
)

# =========================================================
# APLICAR FILTROS
# =========================================================
df_filtrado = df[
    (df["Department"].isin(departamentos)) &
    (df["Encounter Status"].isin(estado)) &
    (df["Clinic Name"].isin(clinica))
].copy()

# =========================================================
# MÉTRICAS PRINCIPALES
# =========================================================
col1, col2, col3, col4 = st.columns(4)

# =========================================================
# CAMBIO:
# Se agrega unidad de tiempo "min"
# =========================================================
col1.metric(
    "Total de registros",
    len(df_filtrado)
)

col2.metric(
    "Tiempo promedio de espera",
    f"{round(df_filtrado['Wait Time Min'].mean(), 2)} min"
)

# =========================================================
# CAMBIO:
# Se agrega escala máxima del Care Score (/5)
# =========================================================
col3.metric(
    "Care Score promedio",
    f"{round(df_filtrado['Care Score'].mean(), 2)}/5"
)

col4.metric(
    "Pacientes únicos",
    df_filtrado["Encounter Number"].nunique()
)

st.divider()

# =========================================================
# GRÁFICAS
# =========================================================
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

    # =========================================================
    # CAMBIO:
    # Se agrega unidad de tiempo en eje Y
    # =========================================================
    fig1.update_layout(
        yaxis_title="Tiempo de espera (minutos)",
        xaxis_title="Departamento"
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

# =========================================================
# SEGUNDA FILA DE GRÁFICAS
# =========================================================
col7, col8 = st.columns(2)

with col7:

    st.subheader("Care Score por departamento")

    fig3 = px.box(
        df_filtrado,
        x="Department",
        y="Care Score",
        title="Distribución del Care Score"
    )

    # =========================================================
    # CAMBIO:
    # Se agrega título descriptivo eje Y
    # =========================================================
    fig3.update_layout(
        yaxis_title="Care Score (escala 1-5)",
        xaxis_title="Departamento"
    )

    st.plotly_chart(fig3, width="stretch")

with col8:

    st.subheader("Registros por mes")

    # =========================================================
    # CAMBIO:
    # Uso de .copy() previamente para evitar warning
    # =========================================================
    df_filtrado["Mes"] = (
        df_filtrado["Appt Start Time"]
        .dt.to_period("M")
        .astype(str)
    )

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

    fig4.update_layout(
        xaxis_title="Mes",
        yaxis_title="Cantidad de registros"
    )

    st.plotly_chart(fig4, width="stretch")

st.divider()

# =========================================================
# TABLA FINAL
# =========================================================
st.subheader("Datos filtrados")

st.dataframe(
    df_filtrado,
    width="stretch"
)