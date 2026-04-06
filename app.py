import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gastos 2026 - Dashboard", layout="wide")

st.title("📊 Mi Control de Gastos 2026")

def limpiar_datos(df, nombre_mes):
    """Limpia las columnas de la hoja de Excel"""
    try:
        # Limpiar nombres de columnas: quitar espacios y a MAYÚSCULAS
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        if 'GASTOS' in df.columns and 'VALOR' in df.columns:
            df = df.dropna(subset=['GASTOS', 'VALOR'])
            df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
            df = df.dropna(subset=['VALOR'])
            df['MES_REF'] = nombre_mes
            return df[['MES_REF', 'GASTOS', 'VALOR']]
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def buscar_y_cargar_archivos():
    """Busca archivos en el repo que coincidan con los meses"""
    meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
             "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    lista_dfs = []
    meses_encontrados = []
    
    # Listar todos los archivos que hay en la carpeta actual de GitHub
    archivos_en_repo = os.listdir('.') 
    
    for mes in meses:
        # Buscar un archivo que CONTENGA el nombre del mes y termine en .xlsx o .csv
        archivo_target = None
        for f in archivos_en_repo:
            if mes in f.upper() and (f.endswith('.xlsx') or f.endswith('.csv')):
                archivo_target = f
                break
        
        if archivo_target:
            try:
                if archivo_target.endswith('.xlsx'):
                    df = pd.read_excel(archivo_target, engine='openpyxl')
                else:
                    df = pd.read_csv(archivo_target)
                
                df_limpio = limpiar_datos(df, mes)
                if not df_limpio.empty:
                    lista_dfs.append(df_limpio)
                    meses_encontrados.append(mes)
            except:
                continue

    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True), meses_encontrados
    return pd.DataFrame(), []

# --- LÓGICA DE INTERFAZ ---
df_total, lista_meses = buscar_y_cargar_archivos()

if not df_total.empty:
    st.sidebar.success(f"✅ Se cargaron {len(lista_meses)} meses automáticamente.")
    
    tabs = st.tabs(["🏠 Resumen"] + [f"📅 {m}" for m in lista_meses])

    with tabs[0]:
        st.metric("Total Gastado 2026", f"${df_total['VALOR'].sum():,.0f}")
        resumen = df_total.groupby('MES_REF', sort=False)['VALOR'].sum().reset_index()
        fig = px.bar(resumen, x='MES_REF', y='VALOR', title="Gastos por Mes", color_discrete_sequence=['#3366ff'])
        st.plotly_chart(fig, use_container_width=True)

    for i, mes in enumerate(lista_meses):
        with tabs[i+1]:
            df_mes = df_total[df_total['MES_REF'] == mes]
            col1, col2 = st.columns([2, 1])
            with col1:
                st.dataframe(df_mes[['GASTOS', 'VALOR']], use_container_width=True)
            with col2:
                fig_pie = px.pie(df_mes, values='VALOR', names='GASTOS', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.error("❌ No se encontraron archivos de gastos en el repositorio.")
    st.write("Archivos detectados en tu GitHub actualmente:")
    st.code(os.listdir('.')) # Esto te dirá qué nombres está viendo Python
