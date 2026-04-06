import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Visualizador Gastos 2026", layout="wide")

st.title("📊 Mi Calculadora de Gastos 2026")
st.write("Sube tu archivo de Excel para analizar los meses.")

# El "File Uploader" permite que la app funcione en GitHub sin errores de "Archivo no encontrado"
uploaded_file = st.file_uploader("Elige tu archivo Gastos2026.xlsx", type="xlsx")

if uploaded_file is not None:
    # Leer todas las pestañas del Excel
    excel_data = pd.ExcelFile(uploaded_file)
    nombres_hojas = excel_data.sheet_names
    
    # Filtrar solo las hojas que son meses (omitir 'DEUDAS', 'SERVICIOS', etc. si quieres)
    meses_validos = [m for m in nombres_hojas if m not in ['DEUDAS', 'SERVICIOS', 'PORTADA']]
    
    lista_todos_los_gastos = []

    for mes in meses_validos:
        df_mes = pd.read_excel(uploaded_file, sheet_name=mes)
        
        # Limpieza rápida de columnas
        df_mes.columns = [str(c).strip().upper() for c in df_mes.columns]
        
        if 'GASTOS' in df_mes.columns and 'VALOR' in df_mes.columns:
            df_mes = df_mes.dropna(subset=['GASTOS', 'VALOR'])
            df_mes['VALOR'] = pd.to_numeric(df_mes['VALOR'], errors='coerce')
            df_mes = df_mes.dropna(subset=['VALOR'])
            df_mes['MES_ORIGEN'] = mes
            lista_todos_los_gastos.append(df_mes)

    if lista_todos_los_gastos:
        df_total = pd.concat(lista_todos_los_gastos, ignore_index=True)
        
        # Crear pestañas en la App
        tabs = st.tabs(["🏠 Resumen Anual"] + meses_validos)
        
        with tabs[0]:
            total_año = df_total['VALOR'].sum()
            st.metric("Total Gastado detectado", f"${total_año:,.0f}")
            fig = px.bar(df_total.groupby('MES_ORIGEN', sort=False)['VALOR'].sum().reset_index(), 
                         x='MES_ORIGEN', y='VALOR', title="Gastos por Mes")
            st.plotly_chart(fig, use_container_width=True)
            
        for i, mes in enumerate(meses_validos):
            with tabs[i+1]:
                datos_mes = df_total[df_total['MES_ORIGEN'] == mes]
                st.dataframe(datos_mes[['GASTOS', 'VALOR']], use_container_width=True)
                st.info(f"Total {mes}: ${datos_mes['VALOR'].sum():,.0f}")
    else:
        st.warning("No se encontraron columnas 'GASTOS' y 'VALOR' en las hojas del archivo.")
else:
    st.info("Esperando archivo... Por favor sube el .xlsx desde tu computadora.")
