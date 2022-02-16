import pandas as pd
import numpy as np
import csv

import altair as alt
import streamlit as st

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

primaryColor="#F63366"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"


casos = pd.read_csv('../data/processed/casos_covid.csv')
casos['fecha'] = pd.to_datetime(casos['fecha'], format='%Y-%m-%d')
casos['anio_mes'] = casos['fecha'].dt.year.astype(str) + '-' + casos['fecha'].dt.month.astype(str).str.zfill(2)
#print(casos.head(3))

casos_ent = casos.groupby(by=['estado'], as_index=False).agg({'confirmados': 'sum',
                                                              'negativos': 'sum',
                                                              'casos': 'sum',
                                                              'defunciones': 'sum'})
#print(casos_ent.head(3))

casos_mes_ent = casos.groupby(by=['estado', 'anio_mes', 'ola'], as_index=False).agg({'confirmados': 'sum',
                                                                                     'negativos': 'sum',
                                                                                     'casos': 'sum',
                                                                                     'defunciones': 'sum'})
#print(casos_mes.head(3))

casos_mes_nac = casos_mes_ent.groupby(by=['anio_mes', 'ola'], as_index=False).agg({'confirmados': 'sum',
                                                                                   'negativos': 'sum',
                                                                                   'casos': 'sum',
                                                                                   'defunciones': 'sum'})

barra = alt.Chart(casos_ent).mark_bar().encode(
    x='estado',
    y='defunciones'
)


col1, col_int, col2 = st.columns([10, 1, 10])

with col1:
    st.markdown('### Casos totales por mes')
    
    radio_01 = st.radio('Seleccione: ', ('Confirmados', 'Negativos', 'Defunciones'))

    variable = None
    if radio_01 == 'Confirmados':
        variable = 'confirmados'
    elif radio_01 == 'Negativos':
        variable = 'negativos'
    elif radio_01 == 'Defunciones':
        variable = 'defunciones'
        
    grafica = alt.Chart(casos_mes_nac).mark_line().encode(
        x='anio_mes',
        y=variable
    )
    
    st.altair_chart(grafica, use_container_width=True)
    
    st.markdown('### Confirmados y negativos por mes')
    inicio, fin = st.select_slider('Seleccione periodo',
                    options=['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', 
              '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12',
              '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06', 
              '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12',
              '2022-01', '2022-02'],
                     value=('2020-01', '2022-02'))
    
    subset = casos_mes_nac.loc[(casos_mes_nac['anio_mes'] >= inicio) &
                               (casos_mes_nac['anio_mes'] <= fin)].copy()
    
    subset = pd.melt(subset, id_vars='anio_mes', value_vars=['confirmados', 'negativos'], 
                     var_name='test', value_name='conteo')
    
    grafica = alt.Chart(subset).mark_area().encode(x="anio_mes", y="conteo", color="test")
    
    st.altair_chart(grafica, use_container_width=True)
    
with col2:
    st.markdown('### Confirmados vs Defunciones por ola')
    
   
    options = st.multiselect('Seleccione olas:', ['Ola 1', 'Ola 2', 'Ola 3', 'Ola 4'], ['Ola 2', 'Ola 4'])
    
    seleccion = []
    
    if 'Ola 1' in options:
        seleccion.append('ola_1')
    if 'Ola 2' in options:
        seleccion.append('ola_2')
    if 'Ola 3' in options:
        seleccion.append('ola_3')
    if 'Ola 4' in options:
        seleccion.append('ola_4')
        
    subset = casos_mes_nac.loc[casos_mes_nac['ola'].isin(seleccion)]
    
    grafica = alt.Chart(subset).mark_circle(size=60).encode(
    x=alt.X('confirmados', title='Confirmados'),
    y=alt.Y('defunciones', title='Defunciones'),
    color=alt.Color('ola', title='Ola'),
    )
          
    st.altair_chart(grafica, use_container_width=True)
    
    st.markdown('### Defunciones por ola')
    grafica = alt.Chart(subset).mark_tick().encode(x='defunciones', y='ola')
    st.altair_chart(grafica, use_container_width=True)
    
    st.markdown('### Letalidad')
    letalidad = subset.groupby(by='ola', as_index=False).agg({'confirmados': 'sum', 'defunciones': 'sum'})
    letalidad['letalidad'] = letalidad['defunciones'] / letalidad['confirmados']

    grafica = alt.Chart(letalidad).mark_bar().encode(
        alt.X('letalidad:Q', axis=alt.Axis(format='.0%')),
        y='ola:N'
    )
    st.altair_chart(grafica, use_container_width=True)
    
    



