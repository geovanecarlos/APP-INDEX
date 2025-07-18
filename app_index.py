# Importação das bibliotecas
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import time
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

# Configuração do Layout do APP
def layouts():
    st.set_page_config(
        page_title="Teleconnection Index Online Tool",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

if __name__ == "__main__":
    layouts()

# Diretório da pasta do projeto
base_path = Path(__file__).resolve().parent

# Limpa o cache do Streamlit
st.cache_data.clear()
st.cache_resource.clear()
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
    list_var.sort()
    return list_dataset, list_var

list_dataset, list_var = get_list_dataset_and_vars()

# Função para plotagem das páginas do APP
tab1, tab2 = st.tabs(["Home", "Indices"])

with tab1:
    def introducao():
        # CSS personalizado com gradiente azul
        title_html = """
            <h1 style='
                text-align: center;
                background: linear-gradient(to right, #001f3f, #00bfff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.2em;
                font-weight: bold;
                font-family: 'Poppins', sans-serif;
                margin-bottom: 2px;
            '>
                Teleconnection Index Online Tool
            </h1>
        """

        # Renderiza o título com gradiente no app           
        st.markdown(title_html, unsafe_allow_html=True)
        horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #ff9793;'><br>"    
        st.markdown(
            """
            <div style='text-align: justify'>
            <b>Teleconnection Index Online Tool:</b> This is an interactive tool that compiles more than 15 teleconnection indices, updated monthly. All indices are calculated using the same database and climatological period (1991–2020). Atmospheric variables are obtained from the ERA5 reanalysis (Hersbach et al., 2020), provided by the European Centre for Medium-Range Weather Forecasts (ECMWF), while sea surface temperature (SST) data come from the Extended Reconstructed Sea Surface Temperature (ERSST) version 5 database.
            Since the tool works with gridded data, the monthly climatology is first calculated for each grid point, followed by the computation of the monthly anomaly at each grid point. The regional mean anomaly is then obtained by averaging the anomalies over the selected area of interest. No trend removal is applied to the data.
            For each index, you will find an interactive button that provides the plotted time series, the data in ASCII format, and a description of the methodology used in the calculation of the index.
            If you use this tool, please cite the following article: [insert article reference here].<br>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(horizontal_bar, True)
            
        st.markdown("""
            **Developers:**
            1. Natan Nogueira - natanchisostomo@gmail.com - Universidade Federal de Itajubá  
            2. Michelle Simões Reboita - reboita@unifei.edu.br - Universidade Federal de Itajubá
            3. Anita Drumond - anita.drumondou@gmail.com - Instituto Tecnológico Vale 
            4. Geovane Carlos Miguel - geovanecarlos.miguel@gmail.com - Universidade Federal de Itajubá
        """)
        st.markdown(horizontal_bar, True)

        # ======================
        # TABELA ESTILO IMAGEM
        # ======================

        last_values = {}
        last_date = None

        for var, data in list_dataset:
            df_temp = data.copy()
            df_temp.columns = ["time", "value"]
            df_temp["time"] = pd.to_datetime(df_temp["time"], errors='coerce')
            df_temp.dropna(subset=["time"], inplace=True)
            df_temp.sort_values("time", inplace=True)
            if not df_temp.empty:
                last_row = df_temp.iloc[-1]
                val = last_row["value"]
                if pd.isna(val):
                    last_values[var] = "-"
                else:
                    last_values[var] = round(val, 2)
                last_date = last_row["time"]
            else:
                last_values[var] = "-"

        # Ordena os índices alfabeticamente (ou ajuste a ordem manualmente se desejar)
        ordered_keys = sorted(last_values.keys())
        formatted_date = last_date.strftime("%B %Y") if last_date else "Last month"

        # Quebrar os índices em 3 linhas
        chunk_size = (len(ordered_keys) + 2) // 3  # divide em 3 linhas aproximadamente iguais
        chunks = [ordered_keys[i:i + chunk_size] for i in range(0, len(ordered_keys), chunk_size)]

        # Add cores de fundo na tela
        html = f"""
        <div style="background-color:#e3e2e2ff; padding:20px; border-radius:10px; color:black; font-family:monospace; text-align:center;">
            <h4 style="color:black; margin-bottom:25px;">Last update: {formatted_date}</h4>
        """

        for chunk in chunks:
            html += "<table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>"
            html += "<tr>"
            for key in chunk:
                html += f"<th style='padding:6px; font-size:16px; color:black;'>{key}</th>"
            html += "</tr><tr>"
            for key in chunk:
                val = last_values[key]
                if val == "-":
                    color = "black"
                    display_val = "-"
                else:
                    color = "red" if val > 0 else "blue" if val < 0 else "white"
                    display_val = f"{val:.2f}"
                html += f"<td style='padding:6px; font-size:16px; font-weight:bold; color:{color};'>{display_val}</td>"
            html += "</tr></table>"

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

    if __name__ == "__main__":
        introducao()

with tab2:
    def plot_indices():

        st.markdown("<h2 style='font-size:24px; color:black;'>📈 Time series of indices</h2>",
                    unsafe_allow_html=True
                    )

        st.sidebar.image("https://github.com/geovanecarlos/APP-INDEX/blob/main/logo-app-tool.png?raw=true",
                         use_container_width=True
                         )

        index_name = st.sidebar.selectbox("Select index:", list_var)

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

            # PLoagem utilizando o Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_pos["time"], y=df_pos["value"],
                                 marker_color="red", name="Positive"))
            fig.add_trace(go.Bar(x=df_neg["time"], y=df_neg["value"],
                                 marker_color="blue", name="Negative"))

            fig.update_layout(
                title=f"{index_name} - Monthly",
                showlegend=False,
                bargap=0,
                height=500,
                xaxis=dict(
                    title=dict(
                        text="Date",
                        font=dict(color="black")
                    ),
                    tickfont=dict(color="black"),
                    rangeselector=dict(
                        font=dict(color="black"),  # <- AQUI adiciona a cor preta aos botões
                        buttons=list([
                            dict(step="all", label="All"),
                            dict(count=30, label="30 years", step="year", stepmode="backward"),
                            dict(count=20, label="20 years", step="year", stepmode="backward"),
                            dict(count=10, label="10 years", step="year", stepmode="backward"),
                            dict(count=5, label="5 years", step="year", stepmode="backward"),
                            dict(count=1, label="1 year", step="year", stepmode="backward")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                yaxis=dict(
                    title=dict(
                        text=index_name,
                        font=dict(color="black")
                    ),
                    tickfont=dict(color="black")
                )
            )

            fig.update_traces(hovertemplate="Date: %{x|%b %Y}<br>Value: %{y:.2f}")
            st.plotly_chart(fig, use_container_width=True)

        # -----------------------------
        # Botão para download dos dados
        # -----------------------------
        st.markdown("<h2 style='font-size:24px; color:black;'>📥 Download data</h2>",unsafe_allow_html=True)

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
    
        # -----------------------------
        # Explicar metodologia
        # -----------------------------
        st.markdown("<h2 style='font-size:24px; color:black;'>🛠️ Methodology</h2>",unsafe_allow_html=True)
        st.markdown("""⏳ In development ...""")

    if __name__ == "__main__":
        plot_indices()
        
