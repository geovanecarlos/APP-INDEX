# Importação das bibliotecas
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from io import BytesIO
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
        if len(dataset.columns) > 1:
            var = dataset.columns[1]
        else:
            var = dataset.columns[0]
        list_dataset.append((var, dataset))
    return list_dataset

def get_list_dataset_and_vars():
    list_dataset = load_datasets()
    list_var = [var for var, _ in list_dataset]
    return list_dataset, list_var

list_dataset, list_var = get_list_dataset_and_vars()

# Função para plotagem das páginas do APP
tab1, tab2 = st.tabs(["About", "Indices"])

with tab1:
    def introducao():
        st.subheader('Online Tool for Teleconnection Indices')
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
        st.markdown(
            "<h2 style='font-size:24px; color:#333;'>Indices - Time Series</h2>",
            unsafe_allow_html=True
        )
        index_name = st.sidebar.selectbox("Select indice:", list_var)

        # Filtra o DataFrame correspondente ao índice selecionado
        df = None
        for var, data in list_dataset:
            if var == index_name:
                df = data.copy()
                df.columns = ["time", "value"]
                break

        if df is not None and {"time", "value"}.issubset(df.columns):
            df["time"] = pd.to_datetime(df["time"], errors='coerce')
            df.dropna(subset=["time"], inplace=True)
            df.sort_values("time", inplace=True)

            df_plot = df.copy()

            # Separar positivos e negativos
            df_pos = df_plot.copy()
            df_neg = df_plot.copy()
            df_pos["value"] = df_pos["value"].clip(lower=0)
            df_neg["value"] = df_neg["value"].clip(upper=0)

            # Gráfico Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_pos["time"], y=df_pos["value"],
                                 marker_color="red", name="Positive"))
            fig.add_trace(go.Bar(x=df_neg["time"], y=df_neg["value"],
                                 marker_color="blue", name="Negative"))

            fig.update_layout(
                title=f"{index_name} - Monthly",
                xaxis_title="Date",
                yaxis_title=index_name,
                showlegend=False,
                bargap=0,
                height=500,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(step="all", label="All"),
                            dict(count=30, label="30 years", step="year", stepmode="backward"),
                            dict(count=10, label="10 years", step="year", stepmode="backward"),
                            dict(count=5, label="5 years", step="year", stepmode="backward"),
                            dict(count=1, label="1 year", step="year", stepmode="backward")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )

            fig.update_traces(hovertemplate="Data: %{x|%b %Y}<br>Valor: %{y:.2f}")
            st.plotly_chart(fig, use_container_width=True)

        # -----------------------------
        # Botão para download dos dados (VERSÃO CORRIGIDA)
        # -----------------------------
        st.markdown("<h2 style='font-size:24px; color:#333;'>📥 Download data</h2>",unsafe_allow_html=True)

        file_format = st.selectbox(
            "Choose file format:",
            options=["CSV (.csv)", "Text (.txt)"]
        )

        base_filename = f"{index_name}_indice data"

        # Initialize variable to avoid UnboundLocalError
        data_to_download = None
        mime_type = ""
        file_name = ""

        if file_format == "CSV (.csv)":
            data_to_download = df_plot.to_csv(index=False).encode("utf-8")
            mime_type = "text/csv"
            file_name = f"{base_filename}.csv"

        elif file_format == "Text (.txt)":
            data_to_download = df_plot.to_csv(index=False, sep="\t").encode("utf-8")
            mime_type = "text/plain"
            file_name = f"{base_filename}.txt"

        # Verify if data was prepared before showing the button
        if data_to_download is not None:
            st.download_button(
                label="⬇️ Download file",
                data=data_to_download,
                file_name=file_name,
                mime=mime_type,
                help="Click to download the selected indice data in the chosen format."
            )
        else:
            st.warning("Could not prepare data for download.")

    if __name__ == "__main__":
        plot_graficos()
