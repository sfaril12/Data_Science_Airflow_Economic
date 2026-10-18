import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import pandas as pd

from process import run_full_pipeline

# Styling constants to match slide theme
BG_COLOR = "#111C35"        # Card background
PANEL_COLOR = "#0D162B"     # Plot inner area
TEXT_COLOR = "#F8FAFC"      # White
MUTED_COLOR = "#94A3B8"     # Cool gray
GRID_COLOR = "#1E2C4F"      # Border/Grid subtle

COUNTRY_COLORS = {
    "Indonesia": "#38BDF8",   # Cyan
    "Malaysia": "#FBBF24",    # Gold
    "Singapore": "#F43F5E",   # Coral
    "Thailand": "#10B981",    # Emerald
    "Philippines": "#A855F7", # Purple
    "Vietnam": "#FB923C"      # Orange
}

def setup_plot_style(ax, title, xlabel, ylabel):
    ax.set_facecolor(PANEL_COLOR)
    ax.set_title(title, fontsize=13, fontweight="bold", color=TEXT_COLOR, pad=12)
    ax.set_xlabel(xlabel, fontsize=10, fontweight="bold", color=MUTED_COLOR, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold", color=MUTED_COLOR, labelpad=8)
    ax.tick_params(colors=MUTED_COLOR, labelsize=9)
    ax.grid(True, linestyle="--", alpha=0.35, color=GRID_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1.2)

def generate_all_charts(output_dir="dashboard/charts"):
    os.makedirs(output_dir, exist_ok=True)
    print("Menjalankan pipeline untuk mengambil data...")
    pipe = run_full_pipeline()
    raw_df = pipe["raw_data"]
    df = pipe["cleaned_data"]
    model_res = pipe["model_results"]

    # -------------------------------------------------------------------------
    # A. DATA GATHERING: Volume Ingesti Data per Negara (Stacked/Grouped Bar)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "Data Gathering: Volume Ingesti Data per Negara", "Negara", "Jumlah Observasi (Tahun)")
    
    country_counts = df.groupby("country")["year"].count().reset_index()
    colors = [COUNTRY_COLORS.get(c, "#38BDF8") for c in country_counts["country"]]
    bars = ax.bar(country_counts["country"], country_counts["year"], color=colors, width=0.52, edgecolor=GRID_COLOR)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, f"{int(h)} Thn",
                ha="center", va="bottom", color=TEXT_COLOR, fontsize=8.5, fontweight="bold")
    ax.set_ylim(0, max(country_counts["year"]) + 12)
    plt.tight_layout()
    p_gather = os.path.join(output_dir, "diagram_gathering_ingestion.png")
    fig.savefig(p_gather, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {p_gather}")

    # -------------------------------------------------------------------------
    # B. DATA ASSESSING: Audit Kelengkapan & Missing Values Sebelum Cleaning
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "Data Assessing: Audit Kelengkapan vs Missing Values", "Indikator Ekonomi", "Persentase Data (%)")
    
    indicators = ["Population", "GDP Nominal", "Unemployment Rate"]
    # Hitung persentase completeness dari raw_df
    total_len = len(raw_df)
    pop_valid = (raw_df["population"].notnull().sum() / total_len) * 100 if "population" in raw_df.columns else 99.0
    gdp_valid = (raw_df["gdp"].notnull().sum() / total_len) * 100 if "gdp" in raw_df.columns else 95.0
    unemp_valid = (raw_df["unemployment_rate"].notnull().sum() / total_len) * 100 if "unemployment_rate" in raw_df.columns else 50.0

    valid_pcts = [pop_valid, gdp_valid, unemp_valid]
    missing_pcts = [100 - v for v in valid_pcts]

    x = np.arange(len(indicators))
    width = 0.45

    b1 = ax.bar(x, valid_pcts, width, label="Data Lengkap (Valid)", color="#10B981", edgecolor=GRID_COLOR)
    b2 = ax.bar(x, missing_pcts, width, bottom=valid_pcts, label="Nilai Hilang (Missing)", color="#F43F5E", edgecolor=GRID_COLOR)

    for i, v in enumerate(valid_pcts):
        ax.text(i, v / 2, f"{v:.1f}%", ha="center", va="center", color=TEXT_COLOR, fontsize=9, fontweight="bold")
        if missing_pcts[i] > 5:
            ax.text(i, v + missing_pcts[i] / 2, f"{missing_pcts[i]:.1f}%", ha="center", va="center", color=TEXT_COLOR, fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(indicators)
    ax.set_ylim(0, 115)
    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper right")
    plt.tight_layout()
    p_assess = os.path.join(output_dir, "diagram_assessing_missing.png")
    fig.savefig(p_assess, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {p_assess}")

    # -------------------------------------------------------------------------
    # C. DATA CLEANING: Before vs After Time-Series Imputation
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "Data Cleaning: Imputasi Deret Waktu (Before vs After)", "Tahun", "Unemployment Rate (%)")

    # Ambil contoh 1 negara (Indonesia)
    idn_clean = df[df["country"] == "Indonesia"].sort_values("year")
    idn_raw = raw_df[raw_df["country_code"] == "IDN"].sort_values("year") if "country_code" in raw_df.columns else idn_clean

    # Plot cleaned continuous line
    ax.plot(idn_clean["year"], idn_clean["unemployment_rate"], color="#38BDF8", linewidth=2.5,
            label="Sesudah Cleaning (Linear Interpolation)", zorder=2)
    # Plot raw points
    if "unemployment_rate" in idn_raw.columns:
        raw_valid = idn_raw.dropna(subset=["unemployment_rate"])
        ax.scatter(raw_valid["year"], raw_valid["unemployment_rate"], color="#FBBF24", s=45,
                   label="Data Raw Asli (Banyak Gap Kosong)", zorder=3, edgecolors="white", linewidth=0.5)

    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper left", fontsize=9)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f%%"))
    plt.tight_layout()
    p_clean = os.path.join(output_dir, "diagram_cleaning_imputation.png")
    fig.savefig(p_clean, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {p_clean}")

    # -------------------------------------------------------------------------
    # D. EDA: HEATMAP KORELASI PEARSON (ESTETIK)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    ax.set_facecolor(PANEL_COLOR)
    ax.set_title("Matriks Korelasi Pearson Antar Variabel Makroekonomi", fontsize=13, fontweight="bold", color=TEXT_COLOR, pad=12)

    corr_df = df[["year", "population", "unemployment_rate", "gdp"]].rename(columns={
        "year": "Tahun",
        "population": "Populasi",
        "unemployment_rate": "Pengangguran",
        "gdp": "GDP"
    }).corr()

    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(
        corr_df,
        annot=True,
        fmt=".3f",
        cmap="mako",
        cbar=True,
        square=True,
        ax=ax,
        linewidths=1.5,
        linecolor=BG_COLOR,
        annot_kws={"size": 11, "fontweight": "bold", "color": TEXT_COLOR}
    )
    ax.tick_params(colors=MUTED_COLOR, labelsize=10)
    plt.tight_layout()
    p_heat = os.path.join(output_dir, "diagram_eda_heatmap.png")
    fig.savefig(p_heat, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {p_heat}")

    # -------------------------------------------------------------------------
    # 1. DIAGRAM 1: Tren Pertumbuhan GDP per Negara (Line Chart)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "1. Tren Pertumbuhan GDP Antar Negara (USD)", "Tahun", "GDP (Triliun USD)")

    for country, group in df.groupby("country"):
        c_color = COUNTRY_COLORS.get(country, "#94A3B8")
        ax.plot(group["year"], group["gdp"] / 1e12, marker="o", markersize=3.5,
                linewidth=2, label=country, color=c_color)

    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8.5, loc="upper left")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.1f T"))
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "diagram_1_gdp_trend.png")
    fig.savefig(chart1_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart1_path}")

    # -------------------------------------------------------------------------
    # 2. DIAGRAM 2: Hubungan Populasi vs GDP (Scatter Plot)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "2. Hubungan Populasi vs GDP", "Populasi Penduduk (Juta Jiwa)", "GDP (Triliun USD)")

    for country, group in df.groupby("country"):
        c_color = COUNTRY_COLORS.get(country, "#94A3B8")
        ax.scatter(group["population"] / 1e6, group["gdp"] / 1e12,
                   color=c_color, label=country, alpha=0.8, s=40, edgecolors="none")

    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8.5, loc="upper left")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.1f T"))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f M"))
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "diagram_2_pop_vs_gdp.png")
    fig.savefig(chart2_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart2_path}")

    # -------------------------------------------------------------------------
    # 3. DIAGRAM 3: Tingkat Pengangguran vs GDP (Bubble Plot)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "3. Hubungan Pengangguran vs GDP (Ukuran: Populasi)", "Tingkat Pengangguran (%)", "GDP (Triliun USD)")

    for country, group in df.groupby("country"):
        c_color = COUNTRY_COLORS.get(country, "#94A3B8")
        sizes = (group["population"] / group["population"].max()) * 180 + 30
        ax.scatter(group["unemployment_rate"], group["gdp"] / 1e12,
                   color=c_color, label=country, alpha=0.7, s=sizes, edgecolors="white", linewidth=0.5)

    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8.5, loc="upper right")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.1f T"))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f%%"))
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "diagram_3_unemp_vs_gdp.png")
    fig.savefig(chart3_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart3_path}")

    # -------------------------------------------------------------------------
    # 4. DIAGRAM 4: Perbandingan Rata-rata GDP Antar Negara (Bar Chart)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "4. Perbandingan Rata-rata GDP ASEAN", "Negara", "Rata-rata GDP (Triliun USD)")

    avg_df = df.groupby("country")["gdp"].mean().reset_index()
    avg_df["gdp_trillion"] = avg_df["gdp"] / 1e12
    avg_df = avg_df.sort_values(by="gdp_trillion", ascending=False)

    colors = [COUNTRY_COLORS.get(c, "#38BDF8") for c in avg_df["country"]]
    bars = ax.bar(avg_df["country"], avg_df["gdp_trillion"], color=colors, width=0.55, edgecolor=GRID_COLOR)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.015, f"${h:.2f}T",
                ha="center", va="bottom", color=TEXT_COLOR, fontsize=8.5, fontweight="bold")

    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.1f T"))
    plt.tight_layout()
    chart4_path = os.path.join(output_dir, "diagram_4_gdp_comparison.png")
    fig.savefig(chart4_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart4_path}")

    # -------------------------------------------------------------------------
    # 5. DIAGRAM 5: Evaluasi ML Aktual vs Prediksi GDP (Scatter & Ideal Line)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "5. Evaluasi Random Forest: Aktual vs Prediksi GDP", "Aktual GDP (Triliun USD)", "Prediksi GDP (Triliun USD)")

    res_df = model_res["prediction_results"]
    for country, group in res_df.groupby("country"):
        c_color = COUNTRY_COLORS.get(country, "#94A3B8")
        ax.scatter(group["Actual_GDP_Trillion"], group["Predicted_GDP_Trillion"],
                   color=c_color, label=country, s=70, alpha=0.9, edgecolors="white", linewidth=0.7)

    # Ideal diagonal line y = x
    min_val = min(res_df["Actual_GDP_Trillion"].min(), res_df["Predicted_GDP_Trillion"].min())
    max_val = max(res_df["Actual_GDP_Trillion"].max(), res_df["Predicted_GDP_Trillion"].max())
    ax.plot([min_val, max_val], [min_val, max_val], color="#F43F5E", linestyle="--", linewidth=1.8, label="Ideal (y = x)")

    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8.5, loc="upper left")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("$%.2f T"))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("$%.2f T"))
    plt.tight_layout()
    chart5_path = os.path.join(output_dir, "diagram_5_model_actual_vs_pred.png")
    fig.savefig(chart5_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart5_path}")

    # -------------------------------------------------------------------------
    # 6. FEATURE IMPORTANCE (Bonus Chart)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=BG_COLOR, dpi=200)
    setup_plot_style(ax, "Feature Importance (Random Forest Regressor)", "Kepentingan Fitur (%)", "Fitur Prediktor")

    feat_df = model_res["feature_importance"].copy().head(5)
    feat_df["Pct"] = feat_df["Importance"] * 100
    feat_df = feat_df.sort_values(by="Pct", ascending=True)

    bars = ax.barh(feat_df["Feature"], feat_df["Pct"], color="#38BDF8", height=0.55, edgecolor=GRID_COLOR)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%",
                ha="left", va="center", color=TEXT_COLOR, fontsize=9, fontweight="bold")

    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f%%"))
    plt.tight_layout()
    chart6_path = os.path.join(output_dir, "diagram_6_feature_importance.png")
    fig.savefig(chart6_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Saved: {chart6_path}")

    print("Semua grafik visualisasi (termasuk Gathering, Assessing, Cleaning & Heatmap) berhasil digenerate!")

if __name__ == "__main__":
    generate_all_charts()
