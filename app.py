import streamlit as st
import pandas as pd  # <--- Esto es lo que falta para que 'pd' funcione
import plotly.express as px
from datetime import datetime

# 1. Configuración de la página (DEBE SER LA PRIMERA COMAND DE STREAMLIT)
st.set_page_config(page_title="Gastos por Mes", page_icon="📅", layout="wide")

# 2. Inicialización de datos (Datos de tu libreta incluidos)
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

# --- BARRA LATERAL ---
st.sidebar.header("📝 Nuevo Registro")
with st.sidebar.form("nuevo_gasto"):
    f = st.date_input("Fecha", datetime.now())
    c = st.selectbox("Categoría", ["Vivienda", "Alimentación", "Transporte", "Ocio", "Salud", "Otros"])
    d = st.text_input("Descripción")
    m = st.number_input("Monto ($)", min_value=0.0, step=1000.0)
    if st.form_submit_button("Añadir a la lista"):
        nuevo = pd.DataFrame({'Fecha': [f], 'Categoría': [c], 'Descripción': [d], 'Monto': [m]})
        st.session_state.gastos = pd.concat([st.session_state.gastos, nuevo], ignore_index=True)
        st.rerun()

# --- PROCESAMIENTO DE FECHAS ---
df = st.session_state.gastos.copy()
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Mes_Nombre'] = df['Fecha'].dt.strftime('%B %Y') 
meses_ordenados = df.sort_values(by='Fecha')['Mes_Nombre'].unique().tolist()

st.title("📊 Mi Control de Gastos Mensuales")

if not df.empty:
    # 3. CREACIÓN DE PESTAÑAS (TABS)
    tabs = st.tabs(["🏠 Resumen General"] + [f"📅 {m}" for m in meses_ordenados])

    # Pestaña General
    with tabs[0]:
        total_h = df['Monto'].sum()
        st.metric("Gasto Total Histórico", f"${total_h:,.0f}")
        fig_bar = px.bar(df.groupby('Mes_Nombre', sort=False)['Monto'].sum().reset_index(), 
                         x='Mes_Nombre', y='Monto', title="Gastos por Mes", color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_bar, use_container_width=True)

    # Pestañas Mensuales Dinámicas
    for i, mes in enumerate(meses_ordenados):
        with tabs[i+1]:
            df_mes = df[df['Mes_Nombre'] == mes]
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                st.write(f"### Detalle de Gastos - {mes}")
                st.dataframe(df_mes[['Fecha', 'Categoría', 'Descripción', 'Monto']].sort_values('Fecha'), use_container_width=True)
            
            with col_b:
                st.write("### Porcentaje")
                fig_pie = px.pie(df_mes, values='Monto', names='Categoría', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.success(f"Total gastado en {mes}: **${df_mes['Monto'].sum():,.0f}**")
else:
    st.info("No hay datos disponibles.")

st.sidebar.divider()
if st.sidebar.button("🗑️ Borrar Todo"):
    st.session_state.gastos = pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto'])
    st.rerun()
