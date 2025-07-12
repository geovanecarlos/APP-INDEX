# Importação das bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

#@st.cache_data

# Diretório da pasta do projeto
base_path = Path(__file__).resolve().parent
def load_index(name):
    df = pd.read_csv(base_path / f'dataset/{name}.txt', sep="\t", parse_dates=["time"])
    return df

# Caminho da pasta
dir_dataset = base_path / "dataset"

# Lista para armazenar os DataFrames
list_dataset = []

# Loop pelos dados txt no diretório
for dataset in dir_dataset.glob("*.txt"):
    dataset = pd.read_csv(dataset, sep="\t")
    # Guarda as informações das variáveis (ex: NINO3, NINO4, NINO12)
    if len(dataset.columns) > 1:
        var = dataset.columns[1]
    else:
        var = dataset.columns[0]
    
    # Adiciona à lista como uma tupla (nome da variável, DataFrame)
    list_dataset.append((var, dataset))
list_var = []
# Exemplo: acessar o nome da variável e o DataFrame
for var, df in list_dataset:
    list_var.append(var)

#list_dataset[0][0]  # Acessa o nome da variável do segundo DataFrame
#len(list_dataset)

st.title(" Índices - Série Temporal")
print(list_var)
index_name = st.sidebar.selectbox("Selecione o índice:", list_var )

# Filtra o DataFrame correspondente ao índice selecionado
df = None
for var, data in list_dataset:
    if var == index_name:
        df = data
        df.columns = ["time", "value"]
        break
print(df)

if df is not None:
    # Garante que as colunas estejam corretas
    if "time" in df.columns and "value" in df.columns:
        # Cria duas séries: valores positivos e negativos
        df_pos = df.copy()
        df_pos["value"] = df_pos["value"].apply(lambda x: x if x > 0 else 0)
        df_neg = df.copy()
        df_neg["value"] = df_neg["value"].apply(lambda x: x if x < 0 else 0)

        # Cria o gráfico com barras positivas (vermelho) e negativas (azul)
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_pos["time"], y=df_pos["value"],
            marker_color='red', name='Positivo'
        ))
        fig.add_trace(go.Bar(
            x=df_neg["time"], y=df_neg["value"],
            marker_color='blue', name='Negativo'
        ))

        fig.update_layout(
            title=f"{index_name} (mensal desde 1980)",
            xaxis_title="Data",
            yaxis_title=index_name,
            showlegend=False,
            bargap=0,
        )
        fig.update_traces(hovertemplate="Data: %{x|%b %Y}<br>Valor: %{y:.2f}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("O DataFrame não possui as colunas esperadas: 'time' e 'value'.")
else:
    st.warning("Índice não encontrado nos dados.")