import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Import modul pipeline dari process.py
from process import run_full_pipeline, DB_CONFIG


# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================

st.set_page_config(
    page_title="Economic Intelligence & ML Dashboard",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 15px 20px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-source {
        background-color: #0284c7;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        display: inline-block;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# PIPELINE EXECUTION (CACHED)
# ==============================================================================

@st.cache_data(ttl=300)
def load_and_process_pipeline():
    """Menjalankan full pipeline dari process.py dengan caching Streamlit."""
    return run_full_pipeline(db_config=DB_CONFIG, allow_api_fallback=True)


try:
    with st.spinner("Memuat dan memproses data pipeline (Data Gathering -> Kesimpulan)..."):
        pipeline_output = load_and_process_pipeline()
except Exception as e:
    st.error("Terjadi kegagalan saat menjalankan pipeline:")
    st.exception(e)
    st.stop()


# Ekstraksi hasil tahapan
source_info = pipeline_output["source"]
raw_df = pipeline_output["raw_data"]
assessment = pipeline_output["assessment_report"]
df_cleaned = pipeline_output["cleaned_data"]
clean_logs = pipeline_output["clean_log"]
eda_data = pipeline_output["eda_results"]
model_res = pipeline_output["model_results"]
conclusions = pipeline_output["conclusions"]


# ==============================================================================
# SIDEBAR CONTROLS & FILTERS
# ==============================================================================

with st.sidebar:
    st.title("⚙️ Pengaturan Dashboard")
    st.caption("Eksplorasi Data & Prediksi Ekonomi")
    
    # Filter Negara
    available_countries = sorted(df_cleaned["country"].unique())
    selected_countries = st.multiselect(
        "Pilih Negara:",
        options=available_countries,
        default=available_countries
    )

    # Filter Tahun
    min_year = int(df_cleaned["year"].min())
    max_year = int(df_cleaned["year"].max())
    selected_year_range = st.slider(
        "Rentang Tahun:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    st.markdown("---")
    st.markdown("### ℹ️ Sumber Pipeline")
    st.info(f"**Sumber Data Saat Ini:**\n{source_info}")

    if st.button("🔄 Segarkan Data Pipeline", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Dibuat menggunakan Apache Airflow, MySQL, Python & Streamlit")


# Filter Dataset Berdasarkan Sidebar untuk Visualisasi EDA
filtered_df = df_cleaned[
    (df_cleaned["country"].isin(selected_countries)) &
    (df_cleaned["year"].between(selected_year_range[0], selected_year_range[1]))
].copy()


# ==============================================================================
# HEADER UTAMA
# ==============================================================================

st.title("🌏 Southeast Asia Economic Intelligence Dashboard")
st.markdown(
    f"<span class='badge-source'>📡 Data Source: {source_info}</span>",
    unsafe_allow_html=True
)
st.write(
    "Aplikasi visualisasi analitik terintegrasi untuk indikator makroekonomi "
    "(GDP, Populasi, Tingkat Pengangguran) dan Machine Learning berbasis data World Bank & MySQL."
)


# ==============================================================================
# METRIC CARDS OVERVIEW
# ==============================================================================

latest_year = eda_data["latest_year"]
latest_df = eda_data["latest_data"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Negara Dianalisis", f"{len(selected_countries)} Negara")
with c2:
    st.metric("Rentang Tahun", f"{selected_year_range[0]} – {selected_year_range[1]}")
with c3:
    st.metric("Total Observasi", f"{len(filtered_df):,} Record")
with c4:
    if not latest_df.empty:
        top_gdp_country = latest_df.iloc[0]["country"]
        top_gdp_val = latest_df.iloc[0]["gdp"] / 1e12
        st.metric(f"GDP Tertinggi ({latest_year})", f"${top_gdp_val:.2f} T", top_gdp_country)
    else:
        st.metric("GDP Tertinggi", "N/A")


# ==============================================================================
# TABS INTERAKTIF TAHAPAN ANALISIS
# ==============================================================================

tab_eda, tab_model, tab_pipeline, tab_conclusion = st.tabs([
    "📊 Visualisasi & EDA (5 Diagram)",
    "🤖 Pemodelan Machine Learning",
    "📋 Pipeline (Gathering, Assessing, Cleaning)",
    "💡 Kesimpulan & Insight"
])


# ------------------------------------------------------------------------------
# TAB 1: VISUALISASI & EDA (5 DIAGRAM UTAMA)
# ------------------------------------------------------------------------------
with tab_eda:
    st.subheader("📈 Analisis Eksplorasi Data (EDA) & Visualisasi")
    st.write(
        "Berikut adalah visualisasi komprehensif untuk memahami tren historis, korelasi antar indikator, "
        "serta komparasi ekonomi antar negara di Asia Tenggara."
    )

    if filtered_df.empty:
        st.warning("Tidak ada data yang sesuai dengan kombinasi filter di sidebar.")
    else:
        # DIAGRAM 1: LINE CHART TREN GDP PER NEGARA
        st.markdown("### 1️⃣ Tren Pertumbuhan GDP per Negara dari Tahun ke Tahun")
        fig_gdp_trend = px.line(
            filtered_df,
            x="year",
            y="gdp",
            color="country",
            markers=True,
            labels={"year": "Tahun", "gdp": "GDP (USD)", "country": "Negara"},
            template="plotly_dark"
        )
        fig_gdp_trend.update_yaxes(tickformat=".2s")
        fig_gdp_trend.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_gdp_trend, use_container_width=True)

        col_left, col_right = st.columns(2)

        # DIAGRAM 2: SCATTER PLOT POPULASI VS GDP
        with col_left:
            st.markdown("### 2️⃣ Hubungan Populasi vs GDP")
            fig_pop_gdp = px.scatter(
                filtered_df,
                x="population",
                y="gdp",
                color="country",
                hover_data=["year"],
                labels={"population": "Populasi Penduduk", "gdp": "GDP (USD)", "country": "Negara"},
                template="plotly_dark"
            )
            fig_pop_gdp.update_xaxes(tickformat=".2s")
            fig_pop_gdp.update_yaxes(tickformat=".2s")
            fig_pop_gdp.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pop_gdp, use_container_width=True)
            st.caption(f"📌 **Korelasi Pearson Populasi - GDP:** `{eda_data['corr_pop_gdp']:.3f}` (Hubungan Positif Signifikan)")

        # DIAGRAM 3: SCATTER BUBBLE TINGKAT PENGANGGURAN VS GDP
        with col_right:
            st.markdown("### 3️⃣ Hubungan Tingkat Pengangguran vs GDP")
            fig_unemp_gdp = px.scatter(
                filtered_df,
                x="unemployment_rate",
                y="gdp",
                color="country",
                size="population",
                hover_data=["year"],
                labels={
                    "unemployment_rate": "Tingkat Pengangguran (%)",
                    "gdp": "GDP (USD)",
                    "country": "Negara",
                    "population": "Populasi"
                },
                template="plotly_dark"
            )
            fig_unemp_gdp.update_yaxes(tickformat=".2s")
            fig_unemp_gdp.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_unemp_gdp, use_container_width=True)
            st.caption(f"📌 **Korelasi Pearson Pengangguran - GDP:** `{eda_data['corr_unemp_gdp']:.3f}` (Ukuran bubble = Populasi)")

        # DIAGRAM 4: BAR CHART KOMPARASI RATA-RATA GDP & PENGANGGURAN
        st.markdown("### 4️⃣ Perbandingan Rata-rata GDP Antar Negara")
        avg_df = filtered_df.groupby("country").agg({
            "gdp": lambda x: x.mean() / 1e12,
            "unemployment_rate": "mean"
        }).reset_index()
        avg_df.columns = ["country", "avg_gdp_trillion", "avg_unemployment"]
        avg_df = avg_df.sort_values(by="avg_gdp_trillion", ascending=False)

        fig_bar_compare = px.bar(
            avg_df,
            x="country",
            y="avg_gdp_trillion",
            color="country",
            text_auto=".2f",
            labels={"country": "Negara", "avg_gdp_trillion": "Rata-rata GDP (Trillion USD)"},
            template="plotly_dark"
        )
        fig_bar_compare.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_bar_compare, use_container_width=True)

        # DIAGRAM 5: EVALUASI AKTUAL VS PREDIKSI GDP (MACHINE LEARNING)
        st.markdown("### 5️⃣ Evaluasi Model Prediksi: Aktual vs Prediksi GDP")
        st.write(
            "Scatter plot pengujian model Random Forest pada data testing (Out-of-Time Validation). "
            "Titik yang mendekati garis putus-putus diagonal ($y = x$) mencerminkan akurasi prediksi yang tinggi."
        )

        res_df = model_res["prediction_results"]
        fig_actual_pred = px.scatter(
            res_df,
            x="Actual_GDP_Trillion",
            y="Predicted_GDP_Trillion",
            color="country",
            hover_data=["year", "Error_Trillion"],
            labels={
                "Actual_GDP_Trillion": "Aktual GDP (Trillion USD)",
                "Predicted_GDP_Trillion": "Prediksi GDP (Trillion USD)",
                "country": "Negara"
            },
            template="plotly_dark"
        )

        min_val = min(res_df["Actual_GDP_Trillion"].min(), res_df["Predicted_GDP_Trillion"].min())
        max_val = max(res_df["Actual_GDP_Trillion"].max(), res_df["Predicted_GDP_Trillion"].max())

        fig_actual_pred.add_shape(
            type="line",
            x0=min_val,
            y0=min_val,
            x1=max_val,
            y1=max_val,
            line=dict(color="#f43f5e", dash="dash", width=2)
        )
        fig_actual_pred.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_actual_pred, use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 2: PEMODELAN MACHINE LEARNING
# ------------------------------------------------------------------------------
with tab_model:
    st.subheader("🤖 Hasil Pemodelan Machine Learning (Random Forest)")
    st.write(
        "Model memprediksi **GDP** dengan prediktor: **Tahun, Populasi, Tingkat Pengangguran, dan Negara (One-Hot Encoded)**. "
        "Menggunakan skema **Time-Based Splitting** untuk mencegah data leakage pada deret waktu."
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Skor R² (Determinasi)", f"{model_res['r2']:.3f}", "Kemampuan Penjelasan Model")
    with m2:
        st.metric("MAE", f"${model_res['mae'] / 1e9:.2f} B", "Rata-rata Selisih Absolut")
    with m3:
        st.metric("RMSE", f"${model_res['rmse'] / 1e9:.2f} B", "Penalti Error Kuadrat")
    with m4:
        st.metric("Tahun Uji (Testing)", f"{model_res['test_years'][0]}–{model_res['test_years'][1]}")

    st.markdown("---")

    col_m_left, col_m_right = st.columns([1, 1])

    with col_m_left:
        st.markdown("#### ⭐ Feature Importance")
        feat_df = model_res["feature_importance"].copy()
        feat_df["Importance (%)"] = (feat_df["Importance"] * 100).round(2)
        
        fig_feat = px.bar(
            feat_df.head(6),
            x="Importance (%)",
            y="Feature",
            orientation="h",
            text_auto=".1f",
            template="plotly_dark",
            color="Importance (%)",
            color_continuous_scale="Blues"
        )
        fig_feat.update_layout(
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_feat, use_container_width=True)

    with col_m_right:
        st.markdown("#### 📋 Tabel Hasil Prediksi Data Uji")
        display_pred_df = model_res["prediction_results"][[
            "country", "year", "Actual_GDP_Trillion", "Predicted_GDP_Trillion", "Error_Trillion"
        ]].copy()
        display_pred_df.columns = ["Negara", "Tahun", "Aktual (Trillion $)", "Prediksi (Trillion $)", "Error (Trillion $)"]
        st.dataframe(
            display_pred_df,
            use_container_width=True,
            hide_index=True
        )


# ------------------------------------------------------------------------------
# TAB 3: PIPELINE (GATHERING, ASSESSING, CLEANING)
# ------------------------------------------------------------------------------
with tab_pipeline:
    st.subheader("📋 Rincian Tahapan Pemrosesan Data (process.py)")

    col_g, col_a, col_c = st.columns(3)
    with col_g:
        st.markdown("### 1. Data Gathering")
        st.write(f"**Sumber Data:** `{source_info}`")
        st.write(f"**Jumlah Baris Raw:** `{assessment['total_rows']:,}` baris")
        st.write(f"**Kolom:** `{', '.join(assessment['columns'])}`")
        st.success("✔ Data berhasil diekstraksi ke memori.")

    with col_a:
        st.markdown("### 2. Data Assessing")
        st.write(f"**Duplikasi Baris:** `{assessment['duplicate_rows']}` baris")
        st.write(f"**Duplikasi (Negara, Tahun):** `{assessment['duplicate_country_year']}` baris")
        st.write("**Temuan Audit Kualitas:**")
        for iss in assessment["issues"]:
            st.markdown(f"- {iss}")

    with col_c:
        st.markdown("### 3. Data Cleaning")
        st.write("**Tindakan Pembersihan:**")
        for log_item in clean_logs:
            st.markdown(f"- {log_item}")
        st.write(f"**Baris Setelah Bersih:** `{len(df_cleaned):,}` baris")
        st.success("✔ Dataset bersih & siap dimodelkan.")

    st.markdown("---")
    st.markdown("#### 🔍 Preview Dataset Bersih")
    preview_df = df_cleaned.copy()
    preview_df["GDP (Trillion USD)"] = (preview_df["gdp"] / 1e12).round(3)
    preview_df["Population"] = preview_df["population"].apply(lambda x: f"{int(x):,}")
    preview_df["Unemployment Rate (%)"] = preview_df["unemployment_rate"].round(2)
    st.dataframe(
        preview_df[["country", "country_code", "year", "GDP (Trillion USD)", "Population", "Unemployment Rate (%)"]],
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------------------------
# TAB 4: KESIMPULAN & INSIGHT
# ------------------------------------------------------------------------------
with tab_conclusion:
    st.subheader("💡 Kesimpulan Analitis & Temuan Kunci")
    st.write(
        "Rangkuman kesimpulan komprehensif yang dihasilkan secara otomatis dari tahapan "
        "Data Gathering, Assessing, Cleaning, EDA, dan Pemodelan Machine Learning:"
    )

    for item in conclusions:
        with st.container():
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>{item['icon']} {item['category']} — <span style="color: #38bdf8;">{item['summary']}</span></h4>
                    <p style="color: #cbd5e1; font-size: 15px; margin-bottom: 0;">{item['detail']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


# ==============================================================================
# FOOTER
# ==============================================================================

st.divider()
st.caption(
    "Data Source: World Bank API | Pipeline Orchestration: Apache Airflow & MySQL | "
    "Data Science: process.py | Dashboard: Streamlit & Plotly"
)