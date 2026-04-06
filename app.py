import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

st.set_page_config(page_title="Gastos 2026", layout="wide")

st.title("📊 Mi Panel de Gastos 2026")

def limpiar_datos(df, nombre_archivo):
    """Limpia el contenido del Excel"""
    try:
        # Poner columnas en mayúsculas para evitar errores de escritura
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        if 'GASTOS' in df.columns and 'VALOR' in df.columns:
            df = df.dropna(subset=['GASTOS', 'VALOR'])
            df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
            df = df.dropna(subset=['VALOR'])
            # Extraer el mes del nombre del archivo (ej: de 'Gastos-ENERO.xlsx' saca 'ENERO')
            df['MES_REF'] = nombre_archivo.split(' - ')[-1].replace('.xlsx', '').upper()
            return df[['MES_REF', 'GASTOS', 'VALOR']]
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def cargar_archivos_dinamicos():
    """Busca TODOS los archivos .xlsx en el repositorio"""
    # Esta línea busca cualquier archivo .xlsx en la carpeta principal
    archivos_excel = glob.glob("*.xlsx")
    
    lista_dfs = []
    
    for archivo in archivos_excel:
        try:
            # Intentar leer el archivo
            df_temp = pd.read_excel(archivo, engine='openpyxl')
            df_limpio = limpiar_datos(df_temp, archivo)
            if not df_limpio.empty:
                lista_dfs.append(df_limpio)
        except:
            continue
            
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- INTERFAZ ---
df_total = cargar_archivos_dinamicos()

if not df_total.empty:
    # Ordenar meses cronológicamente para las pestañas
    orden_meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    meses_presentes = [m for m in orden_meses if m in df_total['MES_REF'].unique()]
    
    st.sidebar.success(f"✅ Se encontraron {len(meses_presentes)} archivos Excel.")

    tabs = st.tabs(["🏠 Resumen"] + [f"📅 {m}" for m in meses_presentes])

    with tabs[0]:
        total = df_total['VALOR'].sum()
        st.metric("Gasto Total Acumulado", f"${total:,.0f}")
        
        resumen = df_total.groupby('MES_REF', sort=False)['VALOR'].sum().reindex(meses_presentes).reset_index()
        fig = px.line(resumen, x='MES_REF', y='VALOR', title="Evolución de Gastos", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    for i, mes in enumerate(meses_presentes):
        with tabs[i+1]:
            df_mes = df_total[df_total['MES_REF'] == mes]
            st.dataframe(df_mes[['GASTOS', 'VALOR']], use_container_width=True)
            st.info(f"Total {mes}: ${df_mes['VALOR'].sum():,.0f}")
else:
    st.error("No se detectaron archivos .xlsx en la carpeta actual.")
    st.write("Archivos que el sistema ve actualmente:")
    st.code(os.listdir('.'))

