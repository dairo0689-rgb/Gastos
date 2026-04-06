import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gastos 2026", layout="wide", page_icon="📊")

def limpiar_datos(df, mes_nombre):
    """Limpia las filas vacías y extrae GASTOS y VALOR"""
    if df.empty:
        return pd.DataFrame()
    
    # Renombrar columnas si es necesario y limpiar espacios
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Quedarnos solo con lo importante
    if 'GASTOS' in df.columns and 'VALOR' in df.columns:
        df = df.dropna(subset=['GASTOS', 'VALOR'])
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
        df = df.dropna(subset=['VALOR'])
        df['Mes'] = mes_nombre
        return df[['Mes', 'GASTOS', 'VALOR', 'FECHA', 'ESTADO']]
    return pd.DataFrame()

@st.cache_data
def cargar_archivos_locales():
    meses = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    lista_dfs = []
    
    for mes in meses:
        # Probamos el nombre exacto que subiste
        filename = f"Gastos2026.xlsx - {mes}.csv"
        
        if os.path.exists(filename):
            try:
                temp_df = pd.read_csv(filename)
                df_limpio = limpiar_datos(temp_df, mes)
                if not df_limpio.empty:
                    lista_dfs.append(df_limpio)
            except Exception as e:
                st.warning(f"No se pudo leer {mes}: {e}")
                
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("📊 Control de Gastos 2026")

df_total = cargar_archivos_locales()

if not df_total.empty:
    meses_detectados = df_total['Mes'].unique().tolist()
    tabs = st.tabs(["🏠 Resumen Anual"] + [f"📅 {m}" for m in meses_detectados])

    # PESTAÑA RESUMEN
    with tabs[0]:
        resumen = df_total.groupby('Mes', sort=False)['VALOR'].sum().reset_index()
        st.metric("Total Gastado Año", f"${df_total['VALOR'].sum():,.0f}")
        
        fig = px.bar(resumen, x='Mes', y='VALOR', color='VALOR', 
                     title="Comparativa de Gastos Mensuales",
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    # PESTAÑAS POR MES
    for i, mes in enumerate(meses_detectados):
        with tabs[i+1]:
            df_mes = df_total[df_total['Mes'] == mes]
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.subheader(f"Lista de Gastos - {mes}")
                st.dataframe(df_mes.drop(columns=['Mes']), use_container_width=True)
            
            with col_right:
                st.subheader("Distribución")
                fig_pie = px.pie(df_mes, values='VALOR', names='GASTOS', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.success(f"Total {mes}: **${df_mes['VALOR'].sum():,.0f}**")
else:
    st.error("⚠️ No se encontraron los archivos CSV.")
    st.info("""
    **Para solucionar esto:**
    1. Asegúrate de que los archivos `.csv` estén en la misma carpeta que este código.
    2. Los nombres deben ser exactamente: `Gastos2026.xlsx - ENERO.csv`, etc.
    """)
