
    import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gastos por Mes", page_icon="📅", layout="wide")

# 1. DATOS INICIALES (Incluyendo los de tu libreta)
if 'gastos' not in st.session_state:
    data_inicial = {
        'Fecha': ['2026-04-01', '2026-04-02', '2026-04-03', '2026-04-04', '2026-04-05', '2026-04-05'],
        'Categoría': ['Vivienda', 'Alimentación', 'Transporte', 'Vivienda', 'Alimentación', 'Ocio'],
        'Descripción': ['Arriendo', 'Supermercado', 'Gasolina', 'Recibo Luz', 'Restaurante', 'Cine'],
        'Monto': [1200000.0, 350000.0, 120000.0, 85000.0, 65000.0, 45000.0]
    }
    df_init = pd.DataFrame(data_inicial)
    df_init['Fecha'] = pd.to_datetime(df_init['Fecha']).dt.date
    st.session_state.gastos = df_init

# --- BARRA LATERAL PARA AGREGAR ---
st.sidebar.header("Añadir Gasto")
with st.sidebar.form("nuevo_gasto"):
    f = st.date_input("Fecha", datetime.now())
    c = st.selectbox("Categoría", ["Vivienda", "Alimentación", "Transporte", "Ocio", "Salud", "Otros"])
    d = st.text_input("Descripción")
    m = st.number_input("Monto ($)", min_value=0.0, step=1000.0)
    if st.form_submit_button("Registrar"):
        nuevo = pd.DataFrame({'Fecha': [f], 'Categoría': [c], 'Descripción': [d], 'Monto': [m]})
        st.session_state.gastos = pd.concat([st.session_state.gastos, nuevo], ignore_index=True)
        st.rerun()

# --- PROCESAMIENTO DE MESES ---
df = st.session_state.gastos
df['Fecha'] = pd.to_datetime(df['Fecha'])
# Crear una columna de "Mes" para agrupar (Eje: "2026-04")
df['Mes_Nombre'] = df['Fecha'].dt.strftime('%B %Y') 
meses_disponibles = df['Mes_Nombre'].unique().tolist()

st.title("📊 Control de Gastos Mensuales")

# Crear las pestañas: "General" + una para cada mes encontrado
tabs = st.tabs(["Resumen General"] + meses_disponibles)

# TAB 0: RESUMEN GENERAL
with tabs[0]:
    col1, col2 = st.columns(2)
    total = df['Monto'].sum()
    col1.metric("Gasto Total Histórico", f"${total:,.2f}")
    
    fig_gen = px.bar(df.groupby('Mes_Nombre')['Monto'].sum().reset_index(), 
                     x='Mes_Nombre', y='Monto', title="Gastos Totales por Mes",
                     color_discrete_sequence=['#003366'])
    st.plotly_chart(fig_gen, use_container_width=True)

# TABS DINÁMICAS POR MES
for i, mes in enumerate(meses_disponibles):
    with tabs[i+1]:
        df_mes = df[df['Mes_Nombre'] == mes]
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader(f"Detalle de {mes}")
            st.table(df_mes[['Fecha', 'Categoría', 'Descripción', 'Monto']].sort_values('Fecha'))
        
        with c2:
            st.subheader("Distribución")
            fig_pie = px.pie(df_mes, values='Monto', names='Categoría', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.metric(f"Total {mes}", f"${df_mes['Monto'].sum():,.2f}")

st.sidebar.divider()
if st.sidebar.button("Borrar todo"):
    st.session_state.gastos = pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto'])
    st.rerun()


