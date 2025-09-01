# Importação das bibliotecas
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import re
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

display_order = [
    "AAO", "PSA1", "PSA2", "AO", "PNA", "NAO", "DMI/IOD", "IOSD",
    "NINO12", "NINO3", "NINO34", "NINO4", "SOI", "TNA", "TSA", "SASAI",
    "SSTRG2", "SAODI", "SASDI", "ONI", "QBO", "PDO", "AMO", "MJO"
]

# Mapeamento rótulos -> nomes reais nos dados
alias = {
    "NINO12": "NIN12",
    "NINO3":  "NIN03",
    "NINO34": "NIN34",
    "NINO4":  "NIN04",
    "DNI/IOD": "DMI/IOD",
    "MJO": "MJO"
}

# Diretório da pasta do projeto
base_path = Path(__file__).resolve().parent

@st.cache_data
def load_datasets():
    dir_dataset = base_path / "dataset"
    datasets = []
    for dataset_path in dir_dataset.glob("*.txt"):
        df = pd.read_csv(dataset_path, sep="\t")
        var = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        datasets.append((var, df))
    return datasets

@st.cache_data
def get_list_dataset_and_vars():
    datasets = load_datasets()
    vars_sorted = sorted(var for var, _ in datasets)
    return datasets, vars_sorted

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
            <b>Teleconnection Index Online Tool:</b> This is an interactive tool that compiles more than 15 teleconnection indices, updated monthly.
            All indices are calculated using the same database and climatological period (1991–2020). Atmospheric variables are obtained from the ERA5 reanalysis,
            provided by the European Centre for Medium-Range Weather Forecasts (ECMWF), while sea surface temperature (SST) data come from the Extended Reconstructed
            Sea Surface Temperature (ERSST) version 5 database. Since the tool works with gridded data, the monthly climatology is first calculated for each grid point,
            followed by the computation of the monthly anomaly at each grid point. The regional mean anomaly is then obtained by averaging the anomalies over the
            selected area of interest. No trend removal is applied to the data.  ONI and indices for low-frequency variability (QBO, PDO and AMO) are obtained from
            external sources. We also highlight that the MJO is a daily index, so it is displayed separately from the other indices. For each index,
            you will find an interactive button that provides the plotted time series, the data in ASCII format, and a description of the methodology used in the 
            alculation of the index. If you use this tool, please cite the following article: [insert article reference here]<br>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(horizontal_bar, True)
            
        st.markdown("""
            **Developers:**
            1. Natan Nogueira - natanchisostomo@gmail.com - Universidade Federal de Itajubá  
            2. Michelle Simões Reboita - reboita@unifei.edu.br - Universidade Federal de Itajubá
            3. Anita Drumond - anita.drumond@pq.itv.org - Instituto Tecnológico Vale 
            4. Geovane Carlos Miguel - geovanecarlos.miguel@gmail.com - Universidade Federal de Itajubá
        """)
        st.markdown(horizontal_bar, True)

        # ======================
        # TABELA ESTILO IMAGEM
        # ======================

        last_values = {}
        last_date = None  # guardará a MAIOR data entre todos os índices

        for var, data in list_dataset:
            df_temp = data.copy()
            df_temp.columns = ["time", "value"]
            df_temp["time"] = pd.to_datetime(df_temp["time"], errors='coerce')
            df_temp.dropna(subset=["time"], inplace=True)
            df_temp.sort_values("time", inplace=True)

            if not df_temp.empty:
                last_row = df_temp.iloc[-1]
                val = last_row["value"]
                last_values[var] = "-" if pd.isna(val) else round(val, 2)
                # mantém a maior data observada
                if last_date is None or last_row["time"] > last_date:
                    last_date = last_row["time"]
            else:
                last_values[var] = "-"

        def get_from_last_values(label: str):
            """Retorna o valor usando o rótulo desejado, respeitando alias e case-insensitive."""
            key = alias.get(label, label)
            if key in last_values:
                return last_values[key]
            for k in last_values.keys():
                if k.casefold() == key.casefold():
                    return last_values[k]
            return "-"

        # quebra em 3 linhas com 8 colunas cada, mantendo a ordem fixa
        rows = [display_order[i:i + 8] for i in range(0, len(display_order), 8)]

        formatted_date = last_date.strftime("%B %Y") if last_date else "Last month"

        # bloco HTML
        html = f"""
        <div style="background-color:#e3e2e2ff; padding:20px; border-radius:10px; color:black; font-family:monospace; text-align:center;">
            <h4 style="color:black; margin-bottom:25px;">Last update: {formatted_date}</h4>
        """

        for row in rows:
            html += "<table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>"
            # cabeçalho
            html += "<tr>" + "".join(
                f"<th style='padding:6px; font-size:16px; color:black;'>{label}</th>" for label in row
            ) + "</tr>"

            # valores
            html += "<tr>"
            for label in row:
                val = get_from_last_values(label)
                if val == "-":
                    color = "black"
                    display_val = "-"
                else:
                    color = "red" if val > 0 else "blue" if val < 0 else "black"
                    display_val = f"{val:.2f}"
                html += f"<td style='padding:6px; font-size:16px; font-weight:bold; color:{color};'>{display_val}</td>"
            html += "</tr></table>"

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

    if __name__ == "__main__":
        introducao()

with tab2:
    def plot_indices():
        st.markdown("<h2 style='font-size:24px; color:black;'>📈 Time series of indices</h2>", unsafe_allow_html=True)
        st.sidebar.image("https://github.com/geovanecarlos/APP-INDEX/blob/main/logo-app-tool.png?raw=true", use_container_width=True)

        # Selectbox usando a mesma ordem da tabela
        indice_escolhido_label = st.sidebar.selectbox("Select index:", display_order)
        indice_escolhido = alias.get(indice_escolhido_label, indice_escolhido_label)

        metodologia_excel = base_path / "Metodologias.xlsx"
        df_metodologias = pd.read_excel(metodologia_excel)
        df_metodologias["Index_normalizado"] = df_metodologias["Index"].astype(str).str.strip().str.lower()

        def corrigir_simbolo_grau(texto):
            return re.sub(r'(?<=\d)o(?=[A-Za-z-])', '°', texto)

        index_name_normalizado = indice_escolhido.strip().lower()
        linha = df_metodologias[df_metodologias["Index_normalizado"] == index_name_normalizado]

        # Caso especial para MJO
        if indice_escolhido_label == "MJO":
            amplitude_path = base_path / "dataset" / "amplitude_mjo.txt"
            fase_path = base_path / "dataset" / "fase_mjo.txt"
            if amplitude_path.exists() and fase_path.exists():
                df_amp = pd.read_csv(amplitude_path, sep="\t")
                df_fase = pd.read_csv(fase_path, sep="\t")

                # Gráfico 1: Amplitude
                df_amp.columns = ["time", "amplitude"]
                df_amp["time"] = pd.to_datetime(df_amp["time"], errors='coerce')
                df_amp.dropna(subset=["time"], inplace=True)
                df_amp.sort_values("time", inplace=True)

                fig_amp = go.Figure([
                    go.Scatter(x=df_amp["time"], y=df_amp["amplitude"], mode="lines", line=dict(color="purple"))
                ])
                fig_amp.update_layout(
                    title="MJO Amplitude (Daily)",
                    showlegend=False,
                    height=350,
                    xaxis=dict(
                        title=dict(text="Date", font=dict(color="black")),
                        tickfont=dict(color="black"),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    yaxis=dict(
                        title=dict(text="Amplitude", font=dict(color="black")),
                        tickfont=dict(color="black")
                    )
                )
                fig_amp.update_traces(hovertemplate="Date: %{x|%d %b %Y}<br>Amplitude: %{y:.2f}")

                # Gráfico 2: Fase
                df_fase.columns = ["time", "phase"]
                df_fase["time"] = pd.to_datetime(df_fase["time"], errors='coerce')
                df_fase.dropna(subset=["time"], inplace=True)
                df_fase.sort_values("time", inplace=True)

                fig_fase = go.Figure([
                    go.Scatter(x=df_fase["time"], y=df_fase["phase"], mode="lines", line=dict(color="orange"))
                ])
                fig_fase.update_layout(
                    title="MJO Phase (Daily)",
                    showlegend=False,
                    height=350,
                    xaxis=dict(
                        title=dict(text="Date", font=dict(color="black")),
                        tickfont=dict(color="black"),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    yaxis=dict(
                        title=dict(text="Phase", font=dict(color="black")),
                        tickfont=dict(color="black")
                    )
                )
                fig_fase.update_traces(hovertemplate="Date: %{x|%d %b %Y}<br>Phase: %{y}")

                st.plotly_chart(fig_amp, use_container_width=True)
                st.plotly_chart(fig_fase, use_container_width=True)

                # -----------------------------
                # Botão para download dos dados
                # -----------------------------
                st.markdown("<h2 style='font-size:24px; color:black;'>📥 Download data</h2>", unsafe_allow_html=True)
                file_format = st.selectbox("Choose file format:", options=["CSV (.csv)", "Text (.txt)"], key="mjo_download_format")
                base_filename_amp = "MJO_amplitude_data"
                base_filename_fase = "MJO_phase_data"

                if file_format == "CSV (.csv)":
                    data_to_download_amp = df_amp.to_csv(index=False).encode("utf-8")
                    data_to_download_fase = df_fase.to_csv(index=False).encode("utf-8")
                    mime_type = "text/csv"
                    file_name_amp = f"{base_filename_amp}.csv"
                    file_name_fase = f"{base_filename_fase}.csv"
                else:
                    data_to_download_amp = df_amp.to_csv(index=False, sep="\t").encode("utf-8")
                    data_to_download_fase = df_fase.to_csv(index=False, sep="\t").encode("utf-8")
                    mime_type = "text/plain"
                    file_name_amp = f"{base_filename_amp}.txt"
                    file_name_fase = f"{base_filename_fase}.txt"

                st.download_button(
                    label="⬇️ Download amplitude file",
                    data=data_to_download_amp,
                    file_name=file_name_amp,
                    mime=mime_type,
                    help="Click to download the MJO amplitude data in the chosen format."
                )
                st.download_button(
                    label="⬇️ Download phase file",
                    data=data_to_download_fase,
                    file_name=file_name_fase,
                    mime=mime_type,
                    help="Click to download the MJO phase data in the chosen format."
                )

                # -----------------------------
                # Explicar metodologia
                # -----------------------------
                st.markdown("<h2 style='font-size:24px; color:black;'>🛠️ Methodology</h2>", unsafe_allow_html=True)
                if not linha.empty:
                    metodologia_texto = linha["Methodology"].values[0]
                    acesso = linha["Access"].values[0]
                    referencia = linha["Reference"].values[0]
                    metodologia_texto_corrigido = corrigir_simbolo_grau(metodologia_texto)

                    st.markdown(f"<p style='text-align: justify;'> {metodologia_texto_corrigido}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: justify;'><strong>🔗 Access:</strong> {acesso}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: justify;'><strong>📚 Reference:</strong> {referencia}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"⏳ Methodology for the **{indice_escolhido}** index under development.")

            else:
                st.warning("MJO data files not found.")

        else:
            # Filtra o DataFrame correspondente ao índice selecionado
            df = next((data.copy() for var, data in list_dataset if var == indice_escolhido), None)
            if df is not None:
                df.columns = ["time", "value"]
                df["time"] = pd.to_datetime(df["time"], errors='coerce')
                df.dropna(subset=["time"], inplace=True)
                df.sort_values("time", inplace=True)

                # Separar positivos e negativos
                df_pos = df.copy()
                df_neg = df.copy()
                df_pos["value"] = df_pos["value"].clip(lower=0)
                df_neg["value"] = df_neg["value"].clip(upper=0)

                # Plotagem utilizando o Plotly
                fig = go.Figure([
                    go.Bar(x=df_pos["time"], y=df_pos["value"], marker_color="red", name="Positive"),
                    go.Bar(x=df_neg["time"], y=df_neg["value"], marker_color="blue", name="Negative")
                ])

                full_index_name = linha["Name_Index"].values[0] if not linha.empty else indice_escolhido
                title_axis_y = indice_escolhido

                fig.update_layout(
                    title=f"{full_index_name} ({indice_escolhido}) - Monthly",
                    showlegend=False,
                    bargap=0,
                    height=500,
                    xaxis=dict(
                        title=dict(text="Date", font=dict(color="black")),
                        tickfont=dict(color="black"),
                        rangeselector=dict(
                            font=dict(color="black"),
                            buttons=[
                                dict(step="all", label="All"),
                                dict(count=30, label="30 years", step="year", stepmode="backward"),
                                dict(count=20, label="20 years", step="year", stepmode="backward"),
                                dict(count=10, label="10 years", step="year", stepmode="backward"),
                                dict(count=5, label="5 years", step="year", stepmode="backward"),
                                dict(count=1, label="1 year", step="year", stepmode="backward")
                            ]
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    yaxis=dict(
                        title=dict(text=title_axis_y, font=dict(color="black")),
                        tickfont=dict(color="black")
                    )
                )

                fig.update_traces(hovertemplate="Date: %{x|%b %Y}<br>Value: %{y:.2f}")
                st.plotly_chart(fig, use_container_width=True)

            # -----------------------------
            # Botão para download dos dados
            # -----------------------------
            st.markdown("<h2 style='font-size:24px; color:black;'>📥 Download data</h2>", unsafe_allow_html=True)

            file_format = st.selectbox("Choose file format:", options=["CSV (.csv)", "Text (.txt)"], key="other_download_format")
            base_filename = f"{indice_escolhido}_indice data"

            if file_format == "CSV (.csv)":
                data_to_download = df.to_csv(index=False).encode("utf-8")
                mime_type = "text/csv"
                file_name = f"{base_filename}.csv"
            else:
                data_to_download = df.to_csv(index=False, sep="\t").encode("utf-8")
                mime_type = "text/plain"
                file_name = f"{base_filename}.txt"

            st.download_button(
                label="⬇️ Download file",
                data=data_to_download,
                file_name=file_name,
                mime=mime_type,
                help="Click to download the selected indice data in the chosen format."
            )

            # -----------------------------
            # Explicar metodologia
            # -----------------------------
            st.markdown("<h2 style='font-size:24px; color:black;'>🛠️ Methodology</h2>", unsafe_allow_html=True)

            if not linha.empty:
                metodologia_texto = linha["Methodology"].values[0]
                acesso = linha["Access"].values[0]
                referencia = linha["Reference"].values[0]
                metodologia_texto_corrigido = corrigir_simbolo_grau(metodologia_texto)

                st.markdown(f"<p style='text-align: justify;'> {metodologia_texto_corrigido}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: justify;'><strong>🔗 Access:</strong> {acesso}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: justify;'><strong>📚 Reference:</strong> {referencia}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"⏳ Methodology for the **{indice_escolhido}** index under development.")
                
    if __name__ == "__main__":
        plot_indices()