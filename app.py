import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Consolidador Gastos 2026", layout="wide")

# Nombre del archivo maestro
MASTER_FILE = "Gastos_Consolidados_2026.xlsx"

def limpiar_datos(df, mes_nombre):
    """Limpia los datos de los CSV para que sean legibles"""
    # Filtramos filas donde 'GASTOS' o 'VALOR' sean nulos
    df = df.dropna(subset=['GASTOS', 'VALOR'])
    # Convertimos VALOR a numérico
    df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
    df = df.dropna(subset=['VALOR'])
    # Añadimos columna de mes para identificarlo
    df['Mes'] = mes_nombre
    return df[['Mes', 'GASTOS', 'VALOR', 'FECHA', 'ESTADO']]

@st.cache_data
def cargar_todo_el_año():
    """Carga y une todos los archivos CSV que subiste"""
    meses = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    lista_dfs = []
    
    for mes in meses:
        filename = f"Gastos2026.xlsx - {mes}.csv"
        if os.path.exists(filename):
            temp_df = pd.read_csv(filename)
            df_limpio = limpiar_datos(temp_df, mes)
            lista_dfs.append(df_limpio)
    
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("📊 Visualizador de Gastos 2026")
st.write("Datos extraídos de tus hojas de cálculo mensuales.")

df_total = cargar_todo_el_año()

if not df_total.empty:
    # 1. PESTAÑAS
    nombres_meses = df_total['Mes'].unique().tolist()
    tabs = st.tabs(["🏠 Resumen Anual"] + [f"📅 {m}" for m in nombres_meses])

    # PESTAÑA RESUMEN
    with tabs[0]:
        col1, col2 = st.columns([1, 2])
        resumen_mes = df_total.groupby('Mes', sort=False)['VALOR'].sum().reset_index()
        
        with col1:
            st.metric("Gasto Total Año", f"${df_total['VALOR'].sum():,.0f}")
            st.write("### Gastos por Mes")
            st.dataframe(resumen_mes, use_container_width=True)
        
        with col2:
            fig = px.bar(resumen_mes, x='Mes', y='VALOR', 
                         title="Comparativa Mensual",
                         color='VALOR', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

    # PESTAÑAS POR MES
    for i, mes in enumerate(nombres_meses):
        with tabs[i+1]:
            df_mes = df_total[df_total['Mes'] == mes]
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"#### Detalle de {mes}")
                st.dataframe(df_mes.drop(columns=['Mes']), use_container_width=True)
            
            with c2:
                st.write("#### Distribución")
                # Top 5 gastos del mes
                fig_pie = px.pie(df_mes, values='VALOR', names='GASTOS', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.info(f"Total gastado en {mes}: **${df_mes['VALOR'].sum():,.0f}**")

    # 2. BOTÓN PARA DESCARGAR TODO UNIFICADO
    st.sidebar.divider()
    df_total.to_excel(MASTER_FILE, index=False)
    with open(MASTER_FILE, "rb") as f:
        st.sidebar.download_button(
            label="📥 Descargar todo el 2026 en Excel",
            data=f,
            file_name="Consolidado_Gastos_2026.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.error("No se encontraron los archivos CSV. Asegúrate de que los nombres coincidan.")

st.sidebar.write("Archivos detectados:", len(df_total['Mes'].unique()) if not df_total.empty else 0)
