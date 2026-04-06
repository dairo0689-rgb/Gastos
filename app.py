import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Control de Gastos", page_icon="💰", layout="wide")

# Inicializar el estado de la sesión para guardar los datos
if 'gastos' not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto'])

# Título y Sidebar
st.title("💰 Mi Calculadora de Gastos")
st.sidebar.header("Añadir Nuevo Gasto")

# Formulario de entrada en la barra lateral
with st.sidebar.form("formulario_gastos"):
    fecha = st.date_input("Fecha", datetime.now())
    categoria = st.selectbox("Categoría", ["Alimentación", "Transporte", "Vivienda", "Ocio", "Salud", "Otros"])
    descripcion = st.text_input("Descripción (Ej: Cena, Gasolina)")
    monto = st.number_input("Monto ($)", min_value=0.0, format="%.2f")
    
    boton_añadir = st.form_submit_button("Añadir Gasto")

if boton_añadir:
    nuevo_gasto = pd.DataFrame({
        'Fecha': [fecha],
        'Categoría': [categoria],
        'Descripción': [descripcion],
        'Monto': [monto]
    })
    st.session_state.gastos = pd.concat([st.session_state.gastos, nuevo_gasto], ignore_index=True)
    st.success("¡Gasto registrado!")

# --- VISUALIZACIÓN DE DATOS ---
df = st.session_state.gastos

if not df.empty:
    # Métricas principales
    total_gastado = df['Monto'].sum()
    st.metric(label="Gasto Total Acumulado", value=f"${total_gastado:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Listado de Gastos")
        st.dataframe(df.sort_values(by='Fecha', ascending=False), use_container_width=True)

    with col2:
        st.subheader("Distribución por Categoría")
        fig = px.pie(df, values='Monto', names='Categoría', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico de evolución temporal
    st.subheader("Evolución de Gastos en el Tiempo")
    df_tiempo = df.groupby('Fecha')['Monto'].sum().reset_index()
    fig_linea = px.line(df_tiempo, x='Fecha', y='Monto', markers=True)
    st.plotly_chart(fig_linea, use_container_width=True)

    # Opción para borrar datos
    if st.button("Limpiar todos los datos"):
        st.session_state.gastos = pd.DataFrame(columns=['Fecha', 'Categoría', 'Descripción', 'Monto'])
        st.rerun()
else:
    st.info("Aún no has registrado gastos. Usa el panel de la izquierda para empezar.")

st.sidebar.divider()
st.sidebar.write("Desarrollado por: Dairo Romero")

