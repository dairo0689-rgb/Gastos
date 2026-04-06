import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gastos 2026", layout="wide")

st.title("📊 Mi Panel de Gastos 2026")

def limpiar_y_procesar(df, nombre_mes):
    """Limpia las columnas y filtra filas vacías"""
    try:
        # Poner todas las columnas en mayúsculas y quitar espacios
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Verificar que existan las columnas GASTOS y VALOR
        if 'GASTOS' in df.columns and 'VALOR' in df.columns:
            # Eliminar filas donde GASTOS o VALOR estén vacíos
            df = df.dropna(subset=['GASTOS', 'VALOR'])
            # Convertir VALOR a número (maneja puntos, comas y símbolos)
            df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
            df = df.dropna(subset=['VALOR'])
            
            if not df.empty:
                df['MES_REF'] = nombre_mes
                return df[['MES_REF', 'GASTOS', 'VALOR']]
    except Exception as e:
        st.sidebar.error(f"Error procesando {nombre_mes}: {e}")
    return pd.DataFrame()

@st.cache_data
def cargar_datos_totales():
    archivos = os.listdir('.')
    lista_dfs = []
    
    # Lista de meses para buscar
    meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
             "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    for mes in meses:
        # Buscamos cualquier archivo que contenga el nombre del mes
        archivo_encontrado = next((f for f in archivos if mes in f.upper()), None)
        
        if archivo_encontrado:
            try:
                # DETECCIÓN HÍBRIDA: ¿Es CSV o Excel?
                if archivo_encontrado.lower().endswith('.csv'):
                    temp_df = pd.read_csv(archivo_encontrado)
                else:
                    temp_df = pd.read_excel(archivo_encontrado, engine='openpyxl')
                
                df_limpio = limpiar_y_procesar(temp_df, mes)
                if not df_limpio.empty:
                    lista_dfs.append(df_limpio)
            except:
                continue
                
    if lista_dfs:
        return pd.concat(lista_dfs, ignore_index=True)
    return pd.DataFrame()

# --- INTERFAZ ---
df_final = cargar_datos_totales()

if not df_final.empty:
    meses_ordenados = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                       "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    meses_en_datos = [m for m in meses_ordenados if m in df_final['MES_REF'].unique()]

    st.sidebar.success(f"✅ Se cargaron {len(meses_en_datos)} meses.")

    tabs = st.tabs(["🏠 Resumen"] + [f"📅 {m}" for m in meses_en_datos])

    with tabs[0]:
        st.metric("Total Gastado 2026", f"${df_final['VALOR'].sum():,.0f}")
        resumen = df_final.groupby('MES_REF', sort=False)['VALOR'].sum().reindex(meses_en_datos).reset_index()
        fig = px.bar(resumen, x='MES_REF', y='VALOR', title="Gastos Mensuales", color='VALOR')
        st.plotly_chart(fig, use_container_width=True)

    for i, mes in enumerate(meses_en_datos):
        with tabs[i+1]:
            datos_mes = df_final[df_final['MES_REF'] == mes]
            c1, c2 = st.columns([2, 1])
            with c1:
                st.dataframe(datos_mes[['GASTOS', 'VALOR']], use_container_width=True)
            with c2:
                fig_p = px.pie(datos_mes, values='VALOR', names='GASTOS')
                st.plotly_chart(fig_p, use_container_width=True)
else:
    st.error("No se encontraron datos. Verifica que tus archivos en GitHub tengan columnas llamadas 'GASTOS' y 'VALOR'.")
    st.write("Archivos que veo en tu carpeta:")
    st.code(os.listdir('.'))

