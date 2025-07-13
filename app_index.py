# Importação das bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# Configuração do Layout do APP
def layouts():
    st.set_page_config(
    page_title="Online Tool for Teleconnection Indices",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
    
if __name__ == "__main__":
    layouts()

# Diretório da pasta do projeto
base_path = Path(__file__).resolve().parent

@st.cache_data
def load_datasets():
    dir_dataset = base_path / "dataset"
    list_dataset = []
    for dataset_path in dir_dataset.glob("*.txt"):
        dataset = pd.read_csv(dataset_path, sep="\t")
        # Coleta os nomes dos índices (ex: NINO3, NINO4, NINO12)
        if len(dataset.columns) > 1:
            var = dataset.columns[1]
        else:
            var = dataset.columns[0]
        # Adiciona à lista como uma tupla (nome da variável, DataFrame)
        list_dataset.append((var, dataset))
    return list_dataset

def get_list_dataset_and_vars():
    list_dataset = load_datasets()
    # Cria uma lista apenas com os nomes das variáveis dos datasets
    list_var = [var for var, _ in list_dataset]
    return list_dataset, list_var

list_dataset, list_var = get_list_dataset_and_vars()


# Função para plotagem das páginas do APP
tab1, tab2 = st.tabs(["About", "Indices"])

with tab1:
    def introducao():
        st.subheader('Online Tool for Teleconnection Indices')
        st.markdown("<h3 style='font-size: 1.2em;'>Introduction:</h3>", unsafe_allow_html=True)
        horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #ff9793;'><br>"    
        st.markdown(
            """
            <div style='text-align: justify'>
            <b>Online Tool for Teleconnection Indices:</b> This is an interactive tool that compiles more than 15 teleconnection indices, updated monthly. All indices are calculated using the same database and climatological period (1991–2020). Atmospheric variables are obtained from the ERA5 reanalysis (Hersbach et al., 2020), provided by the European Centre for Medium-Range Weather Forecasts (ECMWF), while sea surface temperature (SST) data come from the Extended Reconstructed Sea Surface Temperature (ERSST) version 5 database.
            Since the tool works with gridded data, the monthly climatology is first calculated for each grid point, followed by the computation of the monthly anomaly at each grid point. The regional mean anomaly is then obtained by averaging the anomalies over the selected area of interest. No trend removal is applied to the data.
            For each index, you will find an interactive button that provides the plotted time series, the data in ASCII format, and a description of the methodology used in the calculation of the index.
            If you use this tool, please cite the following article: [insert article reference here].<br>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(horizontal_bar, True)
            
        st.markdown("""
                        **Developers:**
                        1. Anita Drumond - anita.drumondou@gmail.com - Instituto Tecnológico Vale
                        2. Natan Nogueira - natanchisostomo@gmail.com - Universidade Federal de Itajubá
                        3. Michelle Simões Reboita - reboita@unifei.edu.br - Universidade Federal de Itajubá
                        4. Geovane Carlos Miguel - geovanecarlos.miguel@gmail.com - Universidade Federal de Itajubá
                        """)
        st.markdown(horizontal_bar, True)
                        
    if __name__ == "__main__":
        introducao()

with tab2:
    def plot_graficos():
        st.title("Índices - Série Temporal")
        index_name = st.sidebar.selectbox("Selecione o índice:", list_var )

        # Filtra o DataFrame correspondente ao índice selecionado
        df = None
        for var, data in list_dataset:
            if var == index_name:
                df = data.copy()
                df.columns = ["time", "value"]
                break

        if df is not None and {"time", "value"}.issubset(df.columns):
            # Separa valores positivos e negativos
            df_pos = df.copy()
            df_neg = df.copy()
            df_pos["value"] = df_pos["value"].clip(lower=0)
            df_neg["value"] = df_neg["value"].clip(upper=0)

            fig = go.Figure([
                go.Bar(x=df_pos["time"], y=df_pos["value"], marker_color='red', name='Positivo'),
                go.Bar(x=df_neg["time"], y=df_neg["value"], marker_color='blue', name='Negativo')
            ])
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

    # Exibindo os gráficos no Streamlit
    if __name__ == "__main__":
        plot_graficos()