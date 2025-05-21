import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# import locale
# locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # o 'es_MX.UTF-8' según tu sistema

df = pd.read_csv('./data.csv')
print(df.describe())
print(df.info())
print(df.columns)
# --- CÓDIGO PARA dashboard_tarea_grupo_X.py --- 
# (Este bloque NO se ejecuta directamente en Jupyter)

##########################################################
# CONFIGURACIÓN DEL DASHBOARD
##########################################################
import streamlit as st
from datetime import date
# Configuración básica de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Configuración simple para los gráficos
sns.set_style("whitegrid")

##################################################
# CARGA DE DATOS
##################################################

# Función para cargar datos con cache para mejorar rendimiento
@st.cache_data
def cargar_datos():
    # Carga el archivo CSV con datos macroeconómicos
    df = pd.read_csv("./data.csv")
    return df

# Cargamos los datos
df = cargar_datos()

##############################################
# CONFIGURACIÓN DE LA BARRA LATERAL
##############################################

# Simplificamos la barra lateral con solo lo esencial
st.sidebar.header('Filtros del Dashboard')

# Fechas
start_date = st.date_input(
    label='Fecha de inicio',
    value=pd.to_datetime(df['Date'].min()),         # valor inicial
    min_value=pd.to_datetime(df['Date']).min(), # fecha mínima
    max_value=pd.to_datetime(df['Date']).max() # fecha máxima
)

st.write('Inicio seleccionado es:', start_date)

end_date = st.date_input(
    label='Fecha de fin',
    value=pd.to_datetime(df['Date']).max(),         # valor inicial
    min_value=pd.to_datetime(df['Date']).min(), # fecha mínima
    max_value=pd.to_datetime(df['Date']).max() # fecha máxima
)

st.write('Fin seleccionado es:', end_date)

# Selector de ciudad
cities = st.sidebar.multiselect(
    'Ciudades', 
    options=df['City'].unique(),
    default=df['City'].unique(),
    help="Selecciona las ciudades para visualizar"
)

# Selector de tipo cliente
customer_types = st.sidebar.multiselect(
    'Tipo cliente', 
    options=df['Customer type'].unique(),
    default=df['Customer type'].unique(),
    help="Selecciona los tipos de clientes para visualizar"
)

# Selector de genero
genders = st.sidebar.multiselect(
    'Generos', 
    options=df['Gender'].unique(),
    default=df['Gender'].unique(),
    help="Selecciona las generos para visualizar"
)

# Selector de producto
products = st.sidebar.multiselect(
    'Productos', 
    options=df['Product line'].unique(),
    default=df['Product line'].unique(),
    help="Selecciona las productos para visualizar"
)

# Selector de medio de pago
payments = st.sidebar.multiselect(
    'Medios de pago', 
    options=df['Payment'].unique(),
    default=df['Payment'].unique(),
    help="Selecciona las medios de pago para visualizar"
)

# ##################################################
# # FILTRADO DE DATOS
# ##################################################
# Filtramos los datos según el rango de años seleccionado
df_filtrado = df[
    (pd.to_datetime(df['Date']) >= pd.to_datetime(start_date)) & 
    (pd.to_datetime(df['Date']) <= pd.to_datetime(end_date)) &
    (df['City'].isin(cities)) &
    (df['Customer type'].isin(customer_types)) &
    (df['Gender'].isin(genders)) &
    (df['Product line'].isin(products)) &
    (df['Payment'].isin(payments))
]
df_filtrado['Date'] = pd.to_datetime(df_filtrado['Date'])
df_filtrado = df_filtrado.sort_values('Date')

# Título principal del dashboard
st.title('📊 Dashboard Ventas')
st.write(f"Datos filtrados desde {start_date} hasta {end_date}")

# #######################################################
# # SECCIÓN DE MÉTRICAS (PRIMERA FILA)
# #######################################################

# Mostramos métricas del último trimestre disponible
st.subheader("Métricas generales")

# Creamos tres columnas para las métricas principales
col1, col2, col3 = st.columns(3)

# Mostramos las métricas con formato adecuado
col1.metric("Total de ventas", "${0:0,.2f}".format(df_filtrado['Total'].sum()), help=f"Ventas totales en el periodo seleccionado")
col2.metric("Costos totales", "${0:0,.2f}".format(df_filtrado['cogs'].sum()), help=f"Costos totales en el periodo seleccionado")
col3.metric("Ganancias", "${0:0,.2f}".format(df_filtrado['gross income'].sum()), help=f"Ganancias totales en el periodo seleccionado")

sns.set_theme()                 # estilo coherente
plt.rcParams['figure.figsize'] = (8,5)
plt.rcParams['figure.dpi']     = 100
# df['Date'] = pd.to_datetime(df['Date'])

#########################################################
# SECCIÓN DE GRÁFICOS (SEGUNDA FILA)
#########################################################

# Sección: Analisis de ventas
st.subheader('Analisis de ventas')

# Dividimos la pantalla en dos columnas (proporción 7:3)
c1_f1, = st.columns(1)

# Columna 1: Gráfico de área para componentes del PIB
with c1_f1:
    # if componentes_pib:
    # Creamos un gráfico de área para mostrar la evolución temporal
    fig, ax = plt.subplots(figsize=(10, 4))
    df_filtrado['Date_str'] = pd.to_datetime(df_filtrado['Date']).dt.strftime('%d-%b')
    print(df_filtrado.head(10))
    sns.lineplot(data=df_filtrado.groupby('Date_str')['Total'].sum().reset_index(), x='Date_str', y='Total', ax=ax, sort=False)
    ax.set_title('Total de Ventas por Día')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Total de Ventas')
    ax.set_xticks(np.arange(0, 100, 5))
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Mostramos el gráfico en Streamlit
    st.pyplot(fig)
    # else:
    #     st.info("Selecciona al menos un componente del PIB")
c1_f1_1, c2_f1_1 = st.columns((4, 3))
# Columna 1: Gráfico de torta para distribución trimestral
with c1_f1_1:    
    # Creamos el gráfico de torta
    fig, ax = plt.subplots(figsize=(5, 4))

    sns.barplot(data=df, x='Branch', y='gross income', hue='Product line', ax=ax)
    ax.set_title('Composición del Ingreso Bruto por Sucursal y Línea de Producto')
    ax.set_xlabel('Sucursal')
    ax.set_ylabel('Ingreso Bruto')
    
    # Mostramos el gráfico en Streamlit
    st.pyplot(fig)
# Columna 2: Gráfico de torta para distribución trimestral
with c2_f1_1:    
    # Creamos el gráfico de torta
    fig, ax = plt.subplots(figsize=(5, 4))

    sns.barplot(data=df_filtrado, x='Product line', y='Total', ax = ax)
    ax.set_title('Total de Ventas por Línea de Producto')
    ax.set_xlabel('Línea de Producto')
    ax.set_ylabel('Total de Ventas')
    plt.xticks(rotation=45)
    
    # Mostramos el gráfico en Streamlit
    st.pyplot(fig)

# ###################################################
# # SECCIÓN DE ANÁLISIS ECONÓMICO (TERCERA FILA)
# ###################################################

# Sección: Análisis de Tendencias Económicas
st.subheader('Análisis clientes')
st.write('Visualización de tendencias relacionadas a clientes')

# Creamos una fila con dos gráficos: PIB y Variables Porcentuales
c1_f2, c2_f2, c3_f2 = st.columns(3)

# Diccionario para traducir nombres de variables
# nombres = {
#     'gdp': 'PIB', 
#     'unemp': 'Desempleo', 
#     'inflation': 'Inflación'
# }

# Columna 1: Gráfico exclusivo para el PIB
with c1_f2:
    # st.write("### Evolución del PIB")
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Distribución de la Calificación de Clientes
    sns.histplot(data=df_filtrado, x='Rating', bins=6, kde=True, ax=ax)
    ax.set_title('Distribución de Calificaciones de Clientes')
    ax.set_xlabel('Calificación')
    ax.set_ylabel('Frecuencia')
    
    # Mostramos el gráfico
    st.pyplot(fig)
    # st.write("*El gráfico muestra la evolución del PIB a lo largo del tiempo, permitiendo identificar ciclos económicos y tendencias de crecimiento.*")

# Columna 2: Gráfico para variables porcentuales (Desempleo e Inflación)
with c2_f2:
    # st.write("### Desempleo e Inflación")
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Colores para cada variable
    colores = {'unemp': '#ff7f0e', 'inflation': '#2ca02c'}
    
    # Comparación del Gasto por Tipo de Cliente
    sns.boxplot(data=df_filtrado, y='Total', x='Customer type', ax=ax)
    ax.set_title('Distribución del Gasto por Tipo de Cliente')
    ax.set_xlabel('Tipo de Cliente')
    ax.set_ylabel('Total de Ventas')
    
    # Mostramos el gráfico
    st.pyplot(fig)
    # st.write("*Comparación entre tasas de desempleo e inflación, útil para analizar posibles compensaciones en política económica.*")

# Columna 3: Métodos de Pago Preferidos
with c3_f2:
    # st.write("### Desempleo e Inflación")
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Métodos de Pago Preferidos
    ax = sns.countplot(data=df, x='Payment', ax=ax)
    ax.set_title('Métodos de Pago Preferidos')
    ax.set_xlabel('Método de Pago')
    ax.set_ylabel('Frecuencia')
    
    # Mostramos el gráfico
    st.pyplot(fig)
    # st.write("*Comparación entre tasas de desempleo e inflación, útil para analizar posibles compensaciones en política económica.*")

# ########################################################
# # SECCIÓN DE ANÁLISIS DE RELACIONES (CUARTA FILA)
# ########################################################
st.subheader('Analisis de correlación')
# st.write('Visualización de tendencias relacionadas a clientes')

# Nueva fila: Gráfico de dispersión (Inflación vs Desempleo) e Histograma
c1_f3, c2_f3 = st.columns(2)

# Gráfico de dispersión: Desempleo vs Inflación (Curva de Phillips)
with c1_f3:
    # st.write("### Relación Inflación-Desempleo")
    
    fig, ax = plt.subplots(figsize=(6, 3))
    
    sns.scatterplot(data=df, x='cogs', y='gross income', ax=ax)
    ax.set_title('Relación entre Costo y Ganancia Bruta')
    ax.set_xlabel('Costo de Bienes Vendidos')
    ax.set_ylabel('Ingreso Bruto')
    
    # Mostrar gráfico
    st.pyplot(fig)
    # st.write("*Explora la relación entre inflación y desempleo. La teoría de la Curva de Phillips sugiere una relación inversa entre ambas variables.*")

# Histograma de Inflación
with c2_f3:
    # st.write("### Distribución de la Inflación")
    
    fig, ax = plt.subplots(figsize=(6, 3))
    
    sns.heatmap(df[['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']].corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    ax.set_title('Mapa de Calor de Correlación Numérica')
    ax.set_xlabel('Variables')
    ax.set_ylabel('Variables')
    plt.xticks(rotation=45)
    
    # Mostrar gráfico
    st.pyplot(fig)
    # st.write("*Visualiza la distribución de las tasas de inflación en el período seleccionado, mostrando su frecuencia y dispersión.*")

# # Pie de página simple
# st.markdown("---")
# st.caption("Dashboard Macroeconómico Simple | Datos: USMacroG_v2.csv")

# # 1.  **Evolución de las Ventas Totales:**
# #     *   **Objetivo:** Mostrar cómo han variado las ventas totales (`Total`) a lo largo del tiempo (`Date`).
# # print(df.groupby('Date')['Total'].sum().reset_index())
# # ax = sns.lineplot(data=df.groupby('Date')['Total'].sum().reset_index(), x='Date', y='Total')
# # ax.set_title('Total de Ventas por Día')
# # ax.set_xlabel('Fecha')
# # ax.set_ylabel('Total de Ventas')
# # plt.xticks(rotation=45)


# # # 2.  **Ingresos por Línea de Producto:**
# # #     *   **Objetivo:** Comparar los ingresos (`Total`) generados por cada `Product line`.
# # ax = sns.barplot(data=df, x='Product line', y='Total')
# # ax.set_title('Total de Ventas por Línea de Producto')
# # ax.set_xlabel('Línea de Producto')
# # ax.set_ylabel('Total de Ventas')
# # plt.xticks(rotation=45)

# # # 3.  **Distribución de la Calificación de Clientes:**
# # #     *   **Objetivo:** Analizar la distribución de las calificaciones (`Rating`) de los clientes.
# # ax = sns.histplot(data=df, x='Rating', bins=10, kde=True)
# # ax.set_title('Distribución de Calificaciones de Clientes')
# # ax.set_xlabel('Calificación')
# # ax.set_ylabel('Frecuencia')

# # # 4.  **Comparación del Gasto por Tipo de Cliente:**
# # #     *   **Objetivo:** Comparar la distribución del gasto total (`Total`) entre clientes `Member` y `Normal`.
# # ax = sns.boxplot(data=df, y='Total', x='Customer type')
# # ax.set_title('Distribución del Gasto por Tipo de Cliente')
# # ax.set_xlabel('Tipo de Cliente')
# # ax.set_ylabel('Total de Ventas')

# # # 5.  **Relación entre Costo y Ganancia Bruta:**
# # #     *   **Objetivo:** Visualizar la relación entre el costo de bienes vendidos (`cogs`) y el ingreso bruto (`gross income`).
# # ax = sns.scatterplot(data=df, x='cogs', y='gross income')
# # ax.set_title('Relación entre Costo y Ganancia Bruta')
# # ax.set_xlabel('Costo de Bienes Vendidos')
# # ax.set_ylabel('Ingreso Bruto')

# # 6.  **Métodos de Pago Preferidos:**
# #     *   **Objetivo:** Identificar los métodos de pago (`Payment`) más frecuentes.
# # ax = sns.countplot(data=df, x='Payment')
# # ax.set_title('Métodos de Pago Preferidos')
# # ax.set_xlabel('Método de Pago')
# # ax.set_ylabel('Frecuencia')

# # # 7.  **Análisis de Correlación Numérica:**
# # #     *   **Objetivo:** Explorar relaciones lineales entre variables numéricas (`Unit price`, `Quantity`, `Tax 5%`, `Total`, `cogs`, `gross income`, `Rating`).
# # ax = sns.heatmap(df[['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']].corr(), annot=True, cmap='coolwarm', fmt='.2f')
# # ax.set_title('Mapa de Calor de Correlación Numérica')
# # ax.set_xlabel('Variables')
# # ax.set_ylabel('Variables')
# # plt.xticks(rotation=45)

# # 8.  **Composición del Ingreso Bruto por Sucursal y Línea de Producto:**
# #     *   **Objetivo:** Mostrar la contribución de cada `Product line` al `gross income` dentro de cada `Branch`.
# ax = sns.barplot(data=df, x='Branch', y='gross income', hue='Product line')
# ax.set_title('Composición del Ingreso Bruto por Sucursal y Línea de Producto')
# ax.set_xlabel('Sucursal')
# ax.set_ylabel('Ingreso Bruto')