import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gastos 2026", layout="wide")

st.title("📊 Mi Panel de Gastos 2026")

def limpiar_datos_flex(df, origen):
    """Limpia el contenido buscando específicamente las columnas GASTOS y VALOR"""
    try:
        # 1. Limpiar nombres de columnas (quitar espacios y a MAYÚSCULAS)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 2. Verificar que existan las columnas necesarias
        if 'GASTOS' in df.columns and 'VALOR' in df.columns:
            # 3. Solo nos interesan las filas que tengan un nombre de gasto
            df = df.dropna(subset=['GASTOS'])
            
            # 4. Convertir VALOR a número (limpiando posibles errores)
            df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')
            
            # 5. Quitar filas donde el valor sea 0 o esté vacío
            df = df[df['VALOR'] > 0]
            
            if not df.empty:
                df['MES'] = origen
                return df[['MES', 'GASTOS', 'VALOR']]
    except:
        pass
    return pd.DataFrame()

@st.cache_data
def cargar_todo():
    archivos = os.listdir('.')
    meses_orden = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                   "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    
    lista_final = []
    
    for mes in meses_orden:
        # Buscar cualquier archivo que contenga el nombre del mes (ej: "Gastos2026.xlsx - ENERO.csv")
        archivo_target = next((f for f in archivos if mes in f.upper()), None)
        
        if archivo_target:
            try:
                # Intentar leerlo de ambas formas (CSV o Excel) por seguridad
                if archivo_target.lower().endswith('.csv'):
                    temp_df = pd.read_csv(archivo_target)
                else:
                    temp_df = pd.read_excel(archivo_target, engine='openpyxl')
                
                df_limpio = limpiar_datos_flex(temp_df, mes)
                if not df_limpio.empty:
                    lista_final.append(df_limpio)
            except:
                continue
                
    return pd.concat(lista_final, ignore_index=True) if lista_final else pd.DataFrame()

# --- INTERFAZ ---
df_total = cargar_todo()

if not df_total.empty:
    meses_encontrados = df_total['MES'].unique().tolist()
    
    # Barra lateral con información
    st.sidebar.success(f"✅ Se cargaron {len(meses_encontrados)} meses.")
    st.sidebar.write("Archivos detectados:", meses_encontrados)

    # Pestañas
    tabs = st.tabs(["🏠 Resumen Anual"] + [f"📅 {m}" for m in meses_encontrados])

    with tabs[0]:
        total_total = df_total['VALOR'].sum()
        st.metric("Gasto Total Acumulado", f"${total_total:,.0f}")
        
        # Gráfica de barras por mes
        resumen = df_total.groupby('MES', sort=False)['VALOR'].sum().reset_index()
        fig = px.bar(resumen, x='MES', y='VALOR', text_auto='.2s',
                     title="Evolución de Gastos Mensuales",
                     color_continuous_scale='Blues', color='VALOR')
        st.plotly_chart(fig, use_container_width=True)

    # Pestañas individuales
    for i, mes in enumerate(meses_encontrados):
        with tabs[i+1]:
            df_mes = df_total[df_total['MES'] == mes]
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"### Detalle de Gastos - {mes}")
                st.dataframe(df_mes[['GASTOS', 'VALOR']], use_container_width=True)
            with c2:
                st.write("### Porcentaje")
                fig_pie = px.pie(df_mes, values='VALOR', names='GASTOS', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            st.success(f"Total del mes: **${df_mes['VALOR'].sum():,.0f}**")

else:
    st.error("❌ No se pudieron extraer datos de los archivos.")
    st.info("Revisa que tus archivos tengan una columna llamada 'GASTOS' y otra 'VALOR'.")
    st.write("Archivos que el sistema ve en tu GitHub:")
    st.code(os.listdir('.'))


