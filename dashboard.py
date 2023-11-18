### TERMONORTE - PROYECTO DE INTELIGENCIA ARTIFICIAL ###
#
# Archivo base para webapp Prototipo
# Dashboard Comercial: Graficas de energía
# Lider funcional: Daniel Amaya
#
# Desarrollado por:
# HEPTAGON GenAI | AIML
# Carlos Gorricho
# cel: +57 314 771 0660
# email: cgorricho@heptagongroup.co
#

### IMPORTAR DEPENDENCIAS ###
import streamlit as st        # web development
import numpy as np            # np mean, np random 
import pandas as pd           # read csv, df manipulation
import plotly.express as px   # interactive charts
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker    # Para crear sepradores en el eje X
import seaborn as sns         # seaborn graphing library
import regex                  # regular expresions para limpiar texto

from pydataxm import *          # Importa la libreria que fue instalada con pip install pydataxm o tambien desde GitHub

import datetime as dt           # Permite trabajar con fechas 

import warnings                 # Módulo para manejo de advertencias
warnings.filterwarnings('ignore')

import time                     # módulo tiempo para generar esperas en las llamadas a la API
from datetime import datetime, date   # para implmentar el cronómetro
from openpyxl import load_workbook, Workbook # para salvar DataFrames a Excel


### IMPORTA Y PREPARA DATOS ###
# define fechas
fecha_inicial = dt.date(2023, 6, 1)
fecha_final = date.today()

# instancia de objeto
objetoAPI = pydataxm.ReadDB()     # Construir la clase que contiene los métodos de pydataxm

## Precio de bolsa
df_precio_bolsa = objetoAPI.request_data("PrecBolsNaci", 
                                         "Sistema", 
                                         fecha_inicial, 
                                         fecha_final)            #Consulta de la variabl     precio de bolsa nacional por sistema 

df_precio_bolsa = df_precio_bolsa.drop(columns=['Id', 'Values_code'])  #Eliminación de columnas innecesarias para los cálculos requeridos

df_precio_bolsa = df_precio_bolsa.set_index('Date')                               #Uso de la columna de 'Date' como índice

# resumen anual de precio de bolsa
df_precio_agregado = df_precio_bolsa.aggregate(['mean', 'max', 'min'], axis=1)
df_precio_agregado = df_precio_agregado.rename(columns={'mean': 'Precio_Prom',
                                                        'max': 'Precio_Max',
                                                        'min': 'Precio_Min'})



## Precio de escasez
df_precio_escasez = objetoAPI.request_data("PrecEsca", 
                                         "Sistema", 
                                         fecha_inicial, 
                                         fecha_final)            #Consulta de la variabl     precio de bolsa nacional por sistema

df_precio_escasez = df_precio_escasez.set_index('Date')      #Uso de la columna de 'Date' como índice
df_precio_escasez = df_precio_escasez.drop('Id', axis=1)


## Precio marginal de escasez
df_precio_marg_escasez = objetoAPI.request_data("PrecEscaMarg", 
                                         "Sistema", 
                                         fecha_inicial, 
                                         fecha_final)            #Consulta de la variabl     precio de bolsa nacional por sistema

df_precio_marg_escasez = df_precio_marg_escasez.set_index('Date')      #Uso de la columna de 'Date' como índice
df_precio_marg_escasez = df_precio_marg_escasez.drop('Id', axis=1)



### DEFINICION DE LA PAGINA ###

# Configuración de la página
st.set_page_config(
    page_title = 'TERMONORTE',
    # page_icon = '🏭',
    layout = 'wide'
)

# barra lateral
st.sidebar.image("logo_TN_small.png")
with st.sidebar:
    mes_inicio, mes_final = st.select_slider(
       'Seleccione el rango de meses',
       options=['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
       value=('Ene', 'Feb'))

st.sidebar.write(f'Mes inicial: {mes_inicio}')
st.sidebar.write(f'Mes final: {mes_final}')


# crea layout para el encabezado
col1, col2 = st.columns([1, 5])

with col1:
   st.image("logo_TN_small.png")

with col2:
   st.header('Informe Comercial')


# pestañas para el reporte
tab1, tab2, tab3, tab4 = st.tabs(
   ["Informe Glenfarne (USD/MWh)", 
    "Energia (COP/kWh)", 
    "Energia (USD/MWh)",
    "Datos",
    ])

# crea datos aleatorios
data = np.random.randn(10, 1)


### DEFINE ESTRUCTURA DE CADA PESTAÑA

## TAB 1 
with tab1:
   # diseño de la página
   placeholder_body = st.empty()
   placeholder_footer = st.empty()

   with placeholder_body.container():
      # crea el entorno de graficado
      fig, ax = plt.subplots(figsize=(10,7))

      # título del gráfico
      ax.set_title('Precio de Bolsa diario (max y min horarios)\n', fontsize=18)

      # gráfica de área
      ax.fill_between(df_precio_agregado.index, 
                  df_precio_agregado['Precio_Prom'], 
                  color='#E3E3E3',
                  label='Precio promedio',
                  )

      # gráfica de precio mínimo
      ax.plot(df_precio_agregado.index,
            df_precio_agregado['Precio_Min'],
            label='Precio Mínimo',
            )

      # gráfica de precio máximo
      ax.plot(df_precio_agregado.index,
            df_precio_agregado['Precio_Max'],
            'y-.',
            label='Precio Máximo',
            )

      # gráfica de precio de escasez
      ax.plot(df_precio_escasez.index,
            df_precio_escasez['Value'],
            'g-',
            label='Precio Escasez',
            )

      # gráfica de precio marginal de escasez
      ax.plot(df_precio_marg_escasez.index,
            df_precio_marg_escasez['Value'],
            'g--',
            label='Precio Marginal Escasez',
            )

      ax.legend()
      ax.set_ylabel('COP / kWh')

      # define frecuencia de los marcadores del eje x
      loc = plticker.MultipleLocator(base=3.0) # this locator puts ticks at regular intervals
      ax.xaxis.set_major_locator(loc)
      ax.tick_params(axis='x', labelrotation = 90)
      ax.set_xlim(df_precio_marg_escasez.index.date.min(), df_precio_marg_escasez.index.date.max())

      st.pyplot(fig)

   with placeholder_footer.container():
      st.divider()
      st.markdown('### Desarrollado por HEPTAGON')
      st.markdown('#### Carlos Gorricho')
      st.markdown('#### cgorricho@heptagongroup.co')
      st.markdown('#### cel +57 314 771 0660')
    
 
with tab2:
   st.header("")
   st.line_chart(data)

with tab3:
   st.header("")
   st.line_chart(data)

with tab4:
   st.header("Datos tomados de archivo de XM API")
   st.write(df_precio_agregado)
   



