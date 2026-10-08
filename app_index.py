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
    "AAO", "PSA1", "PSA2", "AO", "PNA", "NAO", "DMI/IOD", "IOSD", "RONI",
    "NINO12", "NINO3", "NINO34", "NINO4", "SOI", "TNA", "TSA", "SASAI",
    "SSTRG2", "SAODI", "SASDI", "SAD", "SWSA","ONI", "QBO", "PDO", "AMO", "MJO"
]

display_order_tab = [
    "AAO", "PSA1", "PSA2", "AO", "PNA", "NAO", "DMI/IOD", "IOSD", "RONI",
    "NINO12", "NINO3", "NINO34", "NINO4", "SOI", "TNA", "TSA", "SASAI",
    "SSTRG2", "SAODI", "SASDI", "SAD", "SWSA","ONI", "QBO", "PDO", "AMO"
]

display_order_tab_mjo = ["Amplitude MJO", "Phase MJO"]

# Mapeamento rótulos -> nomes reais nos dados
alias = {
    "NINO12": "NIN12",
    "NINO3":  "NIN03",
    "NINO34": "NIN34",
    "NINO4":  "NIN04",
    "DNI/IOD": "DMI/IOD",
    "Amplitude MJO": "Amplitude MJO/RMM",
    "Phase MJO": "Fase MJO/RMM"
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

        st.markdown(title_html, unsafe_allow_html=True)
        horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #ff9793;'><br>"
        st.markdown(
            """
            <div style='text-align: justify'>
            <b>Teleconnection Index Online Tool:</b> This is an interactive tool that compiles more than 15 teleconnection indices, 
            updated monthly. All indices are calculated using the same database and climatological period (1991–2020). 
            Atmospheric variables are obtained from the ERA5 reanalysis, provided by the European Centre for Medium-Range Weather Forecasts (ECMWF), 
            while sea surface temperature (SST) data come from the Extended Reconstructed Sea Surface Temperature (ERSST) version 5 database. 
            Since the tool works with gridded data, the monthly climatology is first calculated for each grid point, followed by the 
            computation of the monthly anomaly at each grid point. The regional mean anomaly is then obtained by averaging the anomalies 
            over the selected area of interest. No trend removal is applied to the data. ONI and indices for low-frequency variability (QBO, PDO and AMO)
            are obtained from external sources. We also highlight that the MJO is a daily index, so it is displayed separately from the other indices. 
            For each index, you will find an interactive button that provides the plotted time series, the data in ASCII format, and a description of the
            methodology used in the calculation of the index. If you use this tool, please cite the following article:
            <p><em>Drumond, A.; Nogueira, N. C. O; Reboita, M. S.; Miguel, G. C. (2025). Teleconnection Indices: an updated version for the current climate.</em></p>
           
           Access: https://www.clivar.org/documents/exchanges-84
            
            <b>How to know if a mode is in its active phase?</b><br>
        
            We suggest that the user download the index time series, compute the monthly standard deviation for the month of interest,
            and then check whether the index shown on the website is above or below ±1 standard deviation. If this condition is met,
            the mode is considered to be in its active phase.
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
        # TABELA DE RESUMO DOS INDICES
        # ======================

        last_values = {}
        last_date = None
        last_date_mjo = None

        latest_date_non_mjo = None
        for var, data in list_dataset:
            if "MJO" in var.upper():
                continue
            df_temp = data.copy()
            df_temp.columns = ["time", "value"]
            df_temp["time"] = pd.to_datetime(df_temp["time"], errors='coerce')
            df_temp.dropna(subset=["time"], inplace=True)
            if not df_temp.empty:
                #print(f"{var}: max = {df_temp['time'].max()}") #QUEBRADO AQUI
                max_date = df_temp["time"].max()
                if latest_date_non_mjo is None or max_date > latest_date_non_mjo:
                    latest_date_non_mjo = max_date

        for var, data in list_dataset:
            df_temp = data.copy()
            df_temp.columns = ["time", "value"]
            df_temp["time"] = pd.to_datetime(df_temp["time"], errors='coerce')
            df_temp.dropna(subset=["time"], inplace=True)
            df_temp.sort_values("time", inplace=True)

            if not df_temp.empty:
                last_row = df_temp.iloc[-1]
                val = last_row["value"]

                if "MJO" in var.upper():
                    last_values[var] = "-" if pd.isna(val) else round(val, 2)
                    if last_date_mjo is None or last_row["time"] > last_date_mjo:
                        last_date_mjo = last_row["time"]
                else:
                    if latest_date_non_mjo is not None:
                        if (last_row["time"].year == latest_date_non_mjo.year and
                            last_row["time"].month == latest_date_non_mjo.month):
                            last_values[var] = "-" if pd.isna(val) else round(val, 2)
                        else:
                            last_values[var] = "-"
                    else:
                        last_values[var] = "-" if pd.isna(val) else round(val, 2)
            else:
                last_values[var] = "-"

        # ✅ CORRIGIDO: last_date agora é sempre a data mais recente dos não-MJO
        last_date = latest_date_non_mjo
        def get_from_last_values(label: str):
            key = alias.get(label, label)
            if key in last_values:
                return last_values[key]
            for k in last_values.keys():
                if k.casefold() == key.casefold():
                    return last_values[k]
            return "-"

        # ✅ CORRIGIDO: return "-" agora está FORA do loop
        def get_from_last_values_mjo(label: str):
            key = alias.get(label, label)
            if key in last_values:
                return last_values[key]
            for k in last_values.keys():
                if k.casefold() == key.casefold():
                    return last_values[k]
            return "-"

        rows = [display_order_tab[i:i + 9] for i in range(0, len(display_order_tab), 9)]
        rows_mjo = [display_order_tab_mjo[i:i + 2] for i in range(0, len(display_order_tab_mjo), 2)]

        formatted_date = last_date.strftime("%B %Y") if last_date else "Last month"
        formatted_date_mjo = last_date_mjo.strftime("%B %dth, %Y") if last_date_mjo else "Last month"

        html = f"""
        <div style="background-color:#e3e2e2ff; padding:20px; border-radius:10px; color:black; font-family:monospace; text-align:center;">
            <h4 style="color:black; margin-bottom:25px;">Indices for {formatted_date}</h4>
        """

        for row in rows:
            html += "<table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>"
            html += "<tr>" + "".join(
                f"<th style='padding:6px; font-size:16px; color:black;'>{label}</th>" for label in row
            ) + "<tr>"

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

        html_mjo = f"""
        <div style="background-color:#e3e2e2ff; padding:20px; border-radius:10px; color:black; font-family:monospace; text-align:center;">
            <h4 style="color:black; margin-bottom:25px;">Indices for {formatted_date_mjo}</h4>
        """

        for row_mjo in rows_mjo:
            html_mjo += "<table style='width:100%; border-collapse:collapse; margin-bottom:20px;'>"
            html_mjo += "<tr>" + "".join(
                f"<th style='padding:6px; font-size:16px; color:black;'>{label_mjo}</th>" for label_mjo in row_mjo
            ) + "</tr>"

            html_mjo += "<tr>"
            for label_mjo in row_mjo:
                val_mjo = get_from_last_values_mjo(label_mjo)
                if val_mjo == "-":
                    color = "black"
                    display_val_mjo = "-"
                else:
                    color = "red" if val_mjo > 0 else "blue" if val_mjo < 0 else "black"
                    display_val_mjo = f"{val_mjo:.2f}"
                html_mjo += f"<td style='padding:6px; font-size:16px; font-weight:bold; color:{color};'>{display_val_mjo}</td>"
            html_mjo += "<tr></tr>"

        html_mjo += "</div>"

        st.markdown(html, unsafe_allow_html=True)
        st.markdown(html_mjo, unsafe_allow_html=True)

    # ✅ CORRIGIDO: chamada direta (sem if __name__)
    introducao()


with tab2:
    def plot_indices():
        st.markdown("<h2 style='font-size:24px; color:black;'>📈 Time series of indices</h2>", unsafe_allow_html=True)
        st.sidebar.image("https://github.com/geovanecarlos/APP-INDEX/blob/main/logo-app-tool.png?raw=true", use_container_width=True)

        indice_escolhido_label = st.sidebar.selectbox("Select index:", display_order)
        indice_escolhido = alias.get(indice_escolhido_label, indice_escolhido_label)

        # ======================
        # BOTÃO DO ATLAS
        # ======================
        st.sidebar.markdown("<p style='margin-bottom: 0px; margin-top: 10px; color: black; font-weight: normal;'>Atlas</p>", unsafe_allow_html=True)
        st.sidebar.markdown(
            f'<a href="https://meteorologia.unifei.edu.br/tiot-atlas/" target="_blank" style="text-decoration: none;">'
            f'<div style="background-color:#001f3f; color:white; padding:8px 24px; '
            f'border:none; border-radius:4px; cursor:pointer; font-size:16px; text-align:center; margin-top: -10px;">'
            f'🌍 Access Atlas</div></a>',
            unsafe_allow_html=True
        )

        @st.cache_data
        def load_metodologias(path):
            df = pd.read_excel(path)
            df["Index_normalizado"] = df["Index"].astype(str).str.strip().str.lower()
            return df

        metodologia_excel = base_path / "Metodologias.xlsx"
        df_metodologias = load_metodologias(metodologia_excel)

        def corrigir_simbolo_grau(texto):
            return re.sub(r'(?<=\d)o(?=[A-Za-z-])', '°', texto)

        index_name_normalizado = indice_escolhido.strip().lower()
        linha = df_metodologias[df_metodologias["Index_normalizado"] == index_name_normalizado]

        @st.cache_data
        def get_dataset_dict(list_dataset):
            return {var: data for var, data in list_dataset}

        dataset_dict = get_dataset_dict(list_dataset)

        # ✅ Função auxiliar para renderizar o bloco de download (evita duplicação)
        def render_download_block(df_filtered, base_filename, key_suffix=""):
            col_format, _ = st.columns([1, 6])   # caixa ocupa 1/4 da largura
            with col_format:
                file_format = st.selectbox(
                    "Choose file format:",
                    options=["CSV (.csv)", "Text (.txt)"],
                    key=f"other_download_format{key_suffix}"
                )
            if file_format == "CSV (.csv)":
                data_to_download = df_filtered.to_csv(index=False).encode("utf-8")
                mime_type = "text/csv"
                file_name = f"{base_filename}.csv"
            else:
                data_to_download = df_filtered.to_csv(index=False, sep="\t").encode("utf-8")
                mime_type = "text/plain; charset=utf-8"
                file_name = f"{base_filename}.txt"

            st.download_button(
                label="⬇️ Download file",
                data=data_to_download,
                file_name=file_name,
                mime=mime_type,
                help="Click to download the selected indice data in the chosen format."
            )

        # ✅ Função auxiliar para renderizar o seletor de datas
        def render_date_selector(df_ref, key_suffix=""):
            st.markdown("**Select date range:**")
            date_range_option = st.radio(
                "Select date range",
                options=["All data", "Custom range"],
                horizontal=True,
                key=f"date_range_option{key_suffix}",
                label_visibility="collapsed"
            )

            if date_range_option == "Custom range":
                col_start, col_end, _ = st.columns([1, 1, 9])

                # ✅ Garante que a coluna é datetime antes de pegar min/max
                time_series = pd.to_datetime(df_ref["time"], errors="coerce").dropna()
                data_min = time_series.min().date()
                data_max = time_series.max().date()

                with col_start:
                    start_date = st.date_input(
                        "Start date:",
                        value=data_min,                  
                        min_value=data_min,            
                        max_value=data_max,             
                        key=f"start_date_download{key_suffix}"
                    )

                with col_end:
                    end_date = st.date_input(
                        "End date:",
                        value=data_max,                 
                        min_value=data_min,              
                        max_value=data_max,             
                        key=f"end_date_download{key_suffix}"
                    )

                end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                return date_range_option, pd.Timestamp(start_date), end_ts
            return date_range_option, None, None

        # ============================================================
        # CASO ESPECIAL: MJO
        # ============================================================
        if indice_escolhido_label == "MJO":
            amplitude_path = base_path / "dataset" / "amplitude_mjo.txt"
            fase_path = base_path / "dataset" / "fase_mjo.txt"
            if amplitude_path.exists() and fase_path.exists():
                df_amp = pd.read_csv(amplitude_path, sep="\t", names=["time", "amplitude"], header=0)
                df_fase = pd.read_csv(fase_path, sep="\t", names=["time", "phase"], header=0)

                for df_ in [df_amp, df_fase]:
                    df_["time"] = pd.to_datetime(df_["time"], errors='coerce')
                    df_.dropna(subset=["time"], inplace=True)
                    df_.sort_values("time", inplace=True)

                # ---------------- FIGURA AMPLITUDE ----------------
                fig_amp = go.Figure([
                    go.Bar(x=df_amp["time"], y=df_amp["amplitude"], marker_color="red", name="Amplitude")
                ])
                fig_amp.update_layout(
                    title="MJO Amplitude (Daily)",
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
                                dict(count=1, label="1 year", step="year", stepmode="backward"),
                                dict(count=6, label="6 months", step="month", stepmode="backward"),
                                dict(count=3, label="3 months", step="month", stepmode="backward"),
                                dict(count=1, label="1 month", step="month", stepmode="backward")
                            ]
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    yaxis=dict(
                        title=dict(text="Amplitude", font=dict(color="black")),
                        tickfont=dict(color="black")
                    )
                )
                fig_amp.update_traces(hovertemplate="Date: %{x|%b-%d-%Y}<br>Amplitude: %{y:.2f}")

                # ---------------- FIGURA FASE ----------------
                fig_fase = go.Figure([
                    go.Bar(x=df_fase["time"], y=df_fase["phase"], marker_color="blue", name="Phase")
                ])
                fig_fase.update_layout(
                    title="MJO Phase (Daily)",
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
                                dict(count=1, label="1 year", step="year", stepmode="backward"),
                                dict(count=6, label="6 months", step="month", stepmode="backward"),
                                dict(count=3, label="3 months", step="month", stepmode="backward"),
                                dict(count=1, label="1 month", step="month", stepmode="backward")
                            ]
                        ),
                        rangeslider=dict(visible=True),
                        type="date"
                    ),
                    yaxis=dict(
                        title=dict(text="Phase", font=dict(color="black")),
                        tickfont=dict(color="black")
                    )
                )
                fig_fase.update_traces(hovertemplate="Date: %{x|%b-%d-%Y}<br>Phase: %{y}")

                st.plotly_chart(fig_amp, use_container_width=True)
                st.plotly_chart(fig_fase, use_container_width=True)

                # -----------------------------
                # Download dos dados (MJO)
                # -----------------------------
                st.markdown("<h2 style='font-size:24px; color:black;'>📥 Download data</h2>", unsafe_allow_html=True)

                # ✅ CORRIGIDO: usa df_amp como referência de datas (antes usava `df` inexistente)
                date_range_option, start_ts, end_ts = render_date_selector(df_amp, key_suffix="_mjo")

                if date_range_option == "Custom range":
                    df_amp_filtered = df_amp[
                        (df_amp["time"] >= start_ts) & (df_amp["time"] <= end_ts)
                    ]
                    df_fase_filtered = df_fase[
                        (df_fase["time"] >= start_ts) & (df_fase["time"] <= end_ts)
                    ]
                else:
                    df_amp_filtered = df_amp
                    df_fase_filtered = df_fase

                # Junta amplitude + fase em um único DataFrame
                df_filtered = pd.merge(
                    df_amp_filtered, df_fase_filtered,
                    on="time", how="outer"
                ).sort_values("time")

                base_filename = f"{indice_escolhido}_indice data"
                render_download_block(df_filtered, base_filename, key_suffix="_mjo")

                # -----------------------------
                # Metodologia
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

        # ============================================================
        # CASO GERAL: demais índices
        # ============================================================
        else:
            df = dataset_dict.get(indice_escolhido)
            if df is not None:
                df = df.copy()
                df.columns = ["time", "value"]
                df["time"] = pd.to_datetime(df["time"], errors='coerce')
                df.dropna(subset=["time"], inplace=True)
                df.sort_values("time", inplace=True)

                df_pos = df.copy()
                df_neg = df.copy()
                df_pos["value"] = df_pos["value"].clip(lower=0)
                df_neg["value"] = df_neg["value"].clip(upper=0)

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
            # Download dos dados (não-MJO)
            # -----------------------------
            st.markdown("<h2 style='font-size:24px; color:black;'>📥 Download data</h2>", unsafe_allow_html=True)

            # ✅ CORRIGIDO: usa a função auxiliar (label_visibility + colunas lado a lado + filtro correto)
            date_range_option, start_ts, end_ts = render_date_selector(df, key_suffix="_general")

            if date_range_option == "Custom range":
                df_filtered = df[
                    (df["time"] >= start_ts) & (df["time"] <= end_ts)
                ]
            else:
                df_filtered = df

            base_filename = f"{indice_escolhido}_indice data"
            render_download_block(df_filtered, base_filename, key_suffix="_general")

            # -----------------------------
            # Metodologia
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

    # ✅ CORRIGIDO: chamada direta (sem if __name__)
    plot_indices()