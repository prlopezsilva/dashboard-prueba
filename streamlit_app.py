import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# set_page_config debe ser siempre la PRIMERA instrucción de Streamlit.
# layout='wide' usa todo el ancho del navegador en vez del contenedor central.
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Cargamos el dataset "tips" que viene incluido en Seaborn.
# Es un dataset clásico con datos de propinas en un restaurante.
tips = sns.load_dataset("tips")

# ============================================================
# SIDEBAR: Todos los widgets dentro de st.sidebar se renderizan
# en el panel lateral izquierdo. Esto permite separar los
# controles (filtros, parámetros) del contenido principal.
# ============================================================
st.sidebar.header('Barra lateral dip 2026')

# st.sidebar.multiselect crea un selector múltiple.
# Usamos .cat.categories para obtener las categorías únicas.
# El parámetro "default" define qué opciones vienen marcadas.
st.sidebar.subheader('Filtros globales')
days = st.sidebar.multiselect('Día', tips['day'].cat.categories.tolist(), default=tips['day'].cat.categories.tolist())
sex_filter = st.sidebar.multiselect('Sexo', tips['sex'].cat.categories.tolist(), default=tips['sex'].cat.categories.tolist())
smoker_filter = st.sidebar.multiselect('Fumador', tips['smoker'].cat.categories.tolist(), default=tips['smoker'].cat.categories.tolist())
time_filter = st.sidebar.multiselect('Momento', tips['time'].cat.categories.tolist(), default=tips['time'].cat.categories.tolist())

# slider devuelve un valor numérico que el usuario ajusta arrastrando.
# Parámetros: etiqueta, mínimo, máximo, valor inicial.
st.sidebar.subheader('Histograma')
hist_bins = st.sidebar.slider('Número de bins', 5, 30, 12)

# selectbox devuelve UNA sola opción de la lista.
st.sidebar.subheader('Scatter plot')
scatter_hue = st.sidebar.selectbox('Color por', ['sex', 'smoker', 'day', 'time'])

st.sidebar.markdown('''
---
Dashboard tutorial · Dataset **Tips** (Seaborn)
''')
# # ###################### ESTE CODIGO SOLO SIRVE PARA ESTE EJEMPLO ######################
# # ###################### NO SIRVE PARA OTROS DATASETS ##################################
# # ============================================================
# # Añadimos una columna 'date' sintética que respeta el día de
# # la semana de cada fila. Estrategia: para cada día (Thur, Fri,
# # Sat, Sun) buscamos su primera ocurrencia desde una fecha base
# # y avanzamos una semana cada vez que reaparece ese día.
# # ============================================================
day_num = {'Thur': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}  # lunes=0 … domingo=6
start = pd.Timestamp('2023-01-01')                    # domingo

offset = (tips['day'].astype(str).map(day_num) - start.dayofweek) % 7  # días hasta la 1ª ocurrencia
week   = tips.groupby('day').cumcount()                                # 0,1,2… por cada día
tips['date'] = start + pd.to_timedelta(offset + week * 7, unit='D')
# ============================================================
# FILTRADO: Aplicamos los filtros del sidebar al DataFrame.
# Cada vez que el usuario cambia un filtro, Streamlit re-ejecuta
# todo el script automáticamente con los nuevos valores.
# ============================================================
df = tips[
    (tips['day'].isin(days)) &
    (tips['sex'].isin(sex_filter)) &
    (tips['smoker'].isin(smoker_filter)) &
    (tips['time'].isin(time_filter))
]

# df = tips.copy()  # Sin filtros para mostrar todo el dataset

# ============================================================
# MÉTRICAS: st.metric muestra un valor destacado con un delta
# opcional (flecha verde/roja). st.columns divide el ancho
# en N columnas para colocar elementos lado a lado.
# ============================================================
st.markdown('### Métricas generales')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(df)}")
col2.metric("Cuenta promedio", f"${df['total_bill'].mean():.2f}")
col3.metric("Propina promedio", f"${df['tip'].mean():.2f}")
col4.metric("% Propina", f"{(df['tip'].sum() / df['total_bill'].sum() * 100):.1f}%")

# ============================================================
# COLUMNAS CON PESO: st.columns((7, 3)) crea dos columnas
# donde la primera ocupa 70% y la segunda 30% del ancho.
# ============================================================
c1, c2 = st.columns((7, 4))

# Para mostrar gráficos de Matplotlib/Seaborn en Streamlit,
# creamos la figura con plt.subplots() y la pasamos a st.pyplot(fig).
with c1:
    st.markdown('### Scatter: Cuenta vs Propina')
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df, x='total_bill', y='tip', alpha=0.7, ax=ax, hue=scatter_hue)
    ax.set(xlabel='Total de la cuenta ($)', ylabel='Propina ($)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    st.pyplot(fig)

# Donut chart: es un pie chart con un círculo blanco al centro.
with c2:
    st.markdown('### Composición por día')
    day_counts = df['day'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    ax2.pie(day_counts, labels=day_counts.index, autopct='%1.0f%%', startangle=90, pctdistance=0.75)
    # centre = plt.Circle((0, 0), 0.50, fc='white')
    # ax2.add_artist(centre)
    ax2.set_aspect('equal')
    fig2.tight_layout()
    st.pyplot(fig2)

# ============================================================
# "with c3:" es equivalente a escribir dentro de esa columna.
# Todo lo que va dentro del bloque with se renderiza ahí.
# ============================================================
c3, c4 = st.columns(2)

with c3:
    st.markdown('### Box plot: Cuenta por día')
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.boxplot(x='day', y='total_bill', data=df, ax=ax3)
    ax3.set(xlabel='Día', ylabel='Total de la cuenta ($)')
    fig3.tight_layout()
    st.pyplot(fig3)

# inner='quartile' dibuja líneas en Q1, mediana y Q3 dentro del violín.
with c4:
    st.markdown('### Violin plot: Cuenta por día')
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.violinplot(x='day', y='total_bill', data=df, inner='quartile', ax=ax4)
    ax4.set(xlabel='Día', ylabel='Total de la cuenta ($)')
    fig4.tight_layout()
    st.pyplot(fig4)

c5, c6 = st.columns(2)

# kde=True superpone una curva de densidad sobre el histograma.
# El número de bins viene del slider del sidebar.
with c5:
    st.markdown('### Histograma: Total de la cuenta')
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    sns.histplot(data=df, x='total_bill', kde=True, color='steelblue', alpha=0.6, ax=ax5, bins=hist_bins)
    ax5.set(xlabel='Total de la cuenta ($)', ylabel='Frecuencia')
    fig5.tight_layout()
    st.pyplot(fig5)

# countplot cuenta automáticamente las observaciones por categoría.
# hue='sex' divide cada barra por sexo.
with c6:
    st.markdown('### Count plot: Visitas por día')
    fig6, ax6 = plt.subplots(figsize=(8, 4))
    sns.countplot(x='day', hue='sex', data=df, ax=ax6)
    ax6.set(xlabel='Día', ylabel='Conteo')
    ax6.legend(title='Sexo')
    fig6.tight_layout()
    st.pyplot(fig6)

c7, c8 = st.columns(2)

# estimator=sum cambia el comportamiento por defecto de barplot
# (que es la media) para mostrar la suma total por categoría.
with c7:
    st.markdown('### Bar plot: Ventas totales por día')
    fig7, ax7 = plt.subplots(figsize=(8, 4))
    sns.barplot(x='day', y='total_bill', data=df, estimator=sum, ax=ax7, errorbar=None)
    ax7.set(xlabel='Día', ylabel='Total vendido ($)')
    fig7.tight_layout()
    st.pyplot(fig7)


# ##########################################################################################

# Line plot: promedio mensual de propina y cuenta total.
with c8:
    st.markdown('### Line plot: Promedios mensuales')
    df_month = df.copy()
    df_month = df_month.sort_values('date')
    df_month['month'] = df_month['date'].dt.to_period('M').dt.to_timestamp()
    monthly = df_month.groupby('month')[['tip', 'total_bill']].mean().reset_index()
    fig8, ax8 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=monthly, x='month', y='total_bill', label='Cuenta promedio', marker='o', ax=ax8)
    sns.lineplot(data=monthly, x='month', y='tip', label='Propina promedio', marker='o', ax=ax8)
    ax8.set(xlabel='Mes', ylabel='Monto promedio ($)')
    ax8.legend()
    fig8.autofmt_xdate()
    fig8.tight_layout()
    st.pyplot(fig8)
