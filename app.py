import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gastos 2026 - Dashboard", layout="wide")

st.title("📊 Mi Control de Gastos 2026")

# Esta función busca los archivos en la carpeta del repositorio
@st.cache_data
def cargar_datos_del_repositorio():
    meses = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    lista_dfs = []
    meses_encontrados = []

    for mes in meses:
        # Buscamos el archivo con el nombre que tienes en GitHub
        nombre_archivo = f"Gastos2026.xlsx - {mes}.xlsx"
        
        if os.path.exists(nombre_archivo):
            try:
                # Leemos el Excel
                df = pd.read_excel(nombre_archivo, engine='openpyxl')
                
                # Limpieza de columnas
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                if 'GASTOS' in df.columns and 'VALOR' in df.columns:
                    df = df.dropna(subset=['GASTOS', 'VALOR'])
                    df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
                    df = df.dropna(subset=['VALOR'])
                    df['MES_REF'] = mes
                    lista_dfs.append(df)
                    meses_encontrados.append(mes)
            except Exception as e:
                st.sidebar.error(f"Error cargando {mes}: {e}")
    
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True), meses_encontrados
    return pd.DataFrame(), []

# --- EJECUCIÓN ---
df_total, lista_meses = cargar_datos_del_repositorio()

if not df_total.empty:
    # Sidebar con resumen rápido
    st.sidebar.header("📁 Datos en el Repositorio")
    st.sidebar.success(f"Se detectaron {len(lista_meses)} meses.")

    # Pestañas
    tabs = st.tabs(["🏠 Resumen General"] + [f"📅 {m}" for m in lista_meses])

    # Tab General
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Gasto Total Anual", f"${df_total['VALOR'].sum():,.0f}")
        
        # Gráfico comparativo
        resumen_mensual = df_total.groupby('MES_REF', sort=False)['VALOR'].sum().reset_index()
        fig_bar = px.bar(resumen_mensual, x='MES_REF', y='VALOR', 
                         title="Gastos por Mes", color='VALOR',
                         color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabs por cada mes
    for i, mes in enumerate(lista_meses):
        with tabs[i+1]:
            df_mes = df_total[df_total['MES_REF'] == mes]
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"### Detalle de {mes}")
                st.dataframe(df_mes[['GASTOS', 'VALOR']], use_container_width=True)
            with c2:
                st.write("### Distribución")
                fig_pie = px.pie(df_mes, values='VALOR', names='GASTOS', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            st.info(f"Total del mes: **${df_mes['VALOR'].sum():,.0f}**")
else:
    st.error("No se encontraron los archivos .xlsx en el repositorio.")
    st.info("Asegúrate de que los archivos estén en la raíz de tu GitHub con nombres como: `Gastos2026.xlsx - ENERO.xlsx`")
