"""Pipeline lengkap analisis data ekonomi Asia Tenggara.

Tahapan: Data Gathering, Data Assessing, Data Cleaning, EDA,
Random Forest Regression, dan kesimpulan otomatis.

Sumber MySQL dibaca langsung melalui JOIN antar tabel countries, gdp,
population, dan unemployment. File ini tidak menggunakan view
`economic_combined`.
"""

import os
from typing import Optional

import mysql.connector
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# -----------------------------------------------------------------------------
# KONFIGURASI
# -----------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3308")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "database": os.getenv("MYSQL_DATABASE", "economic_db"),
    "allow_no_password": True,
}

COUNTRY_MAP = {
    "IDN": "Indonesia",
    "MYS": "Malaysia",
    "SGP": "Singapore",
    "THA": "Thailand",
    "PHL": "Philippines",
    "VNM": "Vietnam",
}

INDICATORS = {
    "gdp": "NY.GDP.MKTP.CD",
    "population": "SP.POP.TOTL",
    "unemployment": "SL.UEM.TOTL.ZS",
}

NUMERIC_COLUMNS = ["gdp", "population", "unemployment_rate"]


# -----------------------------------------------------------------------------
# 1. DATA GATHERING
# -----------------------------------------------------------------------------
def connect_mysql(db_config: Optional[dict] = None):
    """Buka koneksi MySQL; mencoba port dan password yang dikonfigurasi."""
    cfg = {**DB_CONFIG, **(db_config or {})}
    ports_to_try = [int(cfg.get("port", 3308))]
    if 3306 not in ports_to_try:
        ports_to_try.append(3306)

    passwords_to_try = [cfg.get("password", "root")]
    if cfg.get("allow_no_password", True) and "" not in passwords_to_try:
        passwords_to_try.append("")

    errors = []
    for port in ports_to_try:
        for password in passwords_to_try:
            try:
                conn = mysql.connector.connect(
                    host=cfg["host"],
                    port=port,
                    user=cfg["user"],
                    password=password,
                    database=cfg["database"],
                    connection_timeout=5,
                )
                return conn, port
            except mysql.connector.Error as exc:
                errors.append(f"port {port}: {exc}")

    raise ConnectionError(
        "Gagal terhubung ke MySQL. Pemeriksaan: " + " | ".join(errors)
    )


def gather_data_from_mysql(db_config: Optional[dict] = None):
    """Ambil data dengan JOIN tabel fisik; tidak membaca economic_combined."""
    connection, active_port = connect_mysql(db_config)
    try:
        query = """
            SELECT
                g.country_code,
                g.year,
                g.gdp,
                p.population,
                u.unemployment_rate
            FROM gdp AS g
            LEFT JOIN population AS p
                ON p.country_id = g.country_id
               AND p.year = g.year
            LEFT JOIN unemployment AS u
                ON u.country_id = g.country_id
               AND u.year = g.year
            ORDER BY g.year, g.country_code
        """
        df = pd.read_sql_query(query, connection)
    finally:
        connection.close()

    return df, f"MySQL Database (127.0.0.1:{active_port})"


def gather_data_from_world_bank() -> pd.DataFrame:
    """Ambil data langsung dari World Bank API jika MySQL tidak tersedia."""
    countries_param = ";".join(COUNTRY_MAP.keys())
    data_dict = {}
    session = requests.Session()

    for name, indicator_code in INDICATORS.items():
        url = (
            f"https://api.worldbank.org/v2/country/{countries_param}/"
            f"indicator/{indicator_code}?format=json&per_page=20000"
        )
        response = session.get(url, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            continue

        for item in payload[1]:
            country_code = item.get("countryiso3code")
            year_value = item.get("date")
            if not country_code or not year_value:
                continue
            try:
                key = (country_code, int(year_value))
                row = data_dict.setdefault(
                    key,
                    {"country_code": country_code, "year": int(year_value)},
                )
                column = "unemployment_rate" if name == "unemployment" else name
                value = item.get("value")
                row[column] = float(value) if value is not None else np.nan
            except (TypeError, ValueError):
                continue

    df = pd.DataFrame(list(data_dict.values()))
    for column in ["gdp", "population", "unemployment_rate"]:
        if column not in df.columns:
            df[column] = np.nan
    if not df.empty:
        df = df.sort_values(["year", "country_code"]).reset_index(drop=True)
    return df


def gather_data(db_config: Optional[dict] = None, allow_api_fallback: bool = True):
    """Tahap 1: baca MySQL, dengan fallback API bila diizinkan."""
    try:
        df, source = gather_data_from_mysql(db_config)
        if df.empty:
            raise ValueError("Database MySQL tidak mengembalikan data.")
        return df, source
    except Exception as exc:
        if not allow_api_fallback:
            raise
        print(f"[Gathering Warning] MySQL gagal ({exc}); mencoba World Bank API.")
        df = gather_data_from_world_bank()
        if df.empty:
            raise ValueError("World Bank API tidak mengembalikan data.")
        return df, "World Bank API (Direct Fallback)"


# -----------------------------------------------------------------------------
# 2. DATA ASSESSING
# -----------------------------------------------------------------------------
def assess_data(df: pd.DataFrame) -> dict:
    """Periksa missing values, duplikasi, tipe data, dan rentang tahun."""
    total_rows = len(df)
    missing_counts = df.isnull().sum()
    denominator = total_rows if total_rows else 1
    missing_pct = (missing_counts / denominator * 100).round(2)
    missing_df = pd.DataFrame(
        {"Missing Values": missing_counts, "Percentage (%)": missing_pct}
    )
    duplicate_rows = int(df.duplicated().sum())
    duplicate_country_year = (
        int(df.duplicated(subset=["country_code", "year"]).sum())
        if {"country_code", "year"}.issubset(df.columns)
        else 0
    )
    min_year = int(df["year"].min()) if total_rows and "year" in df else None
    max_year = int(df["year"].max()) if total_rows and "year" in df else None
    countries = sorted(df["country_code"].dropna().unique().tolist()) if "country_code" in df else []

    issues = []
    if duplicate_rows or duplicate_country_year:
        issues.append(
            f"Ditemukan {duplicate_country_year} duplikasi berdasarkan (country_code, year)."
        )
    for column, count in missing_counts.items():
        if count:
            issues.append(f"Kolom '{column}' memiliki {count} nilai hilang ({missing_pct[column]}%).")
    if not issues:
        issues.append("Tidak ditemukan anomali kritis pada struktur dataset.")

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missing_summary": missing_df,
        "duplicate_rows": duplicate_rows,
        "duplicate_country_year": duplicate_country_year,
        "year_range": (min_year, max_year),
        "countries": countries,
        "issues": issues,
    }


# -----------------------------------------------------------------------------
# 3. DATA CLEANING
# -----------------------------------------------------------------------------
def clean_data(df: pd.DataFrame):
    """Bersihkan duplikasi, tipe data, nama negara, dan nilai hilang."""
    clean_log = []
    cleaned_df = df.copy()

    required = ["country_code", "year", "gdp", "population", "unemployment_rate"]
    for column in required:
        if column not in cleaned_df.columns:
            cleaned_df[column] = np.nan

    initial_len = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates(subset=["country_code", "year"]).reset_index(drop=True)
    duplicates_removed = initial_len - len(cleaned_df)
    if duplicates_removed:
        clean_log.append(f"Menghapus {duplicates_removed} baris duplikat.")

    cleaned_df["country"] = cleaned_df["country_code"].map(COUNTRY_MAP).fillna(cleaned_df["country_code"])
    clean_log.append("Menambahkan nama negara lengkap dari kode ISO.")

    cleaned_df["year"] = pd.to_numeric(cleaned_df["year"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors="coerce")
    cleaned_df = cleaned_df.dropna(subset=["country_code", "year"])
    cleaned_df["year"] = cleaned_df["year"].astype(int)
    cleaned_df = cleaned_df.sort_values(["country_code", "year"]).reset_index(drop=True)

    # Interpolasi hanya dalam masing-masing negara agar tidak mencampur negara.
    for column in NUMERIC_COLUMNS:
        cleaned_df[column] = cleaned_df.groupby("country_code", sort=False)[column].transform(
            lambda series: series.interpolate(method="linear", limit_direction="both")
        )

    before_gdp_drop = len(cleaned_df)
    cleaned_df = cleaned_df.dropna(subset=["gdp"]).reset_index(drop=True)
    dropped_gdp = before_gdp_drop - len(cleaned_df)
    if dropped_gdp:
        clean_log.append(f"Menghapus {dropped_gdp} baris tanpa nilai GDP setelah imputasi.")

    # Jangan mengubah populasi kosong menjadi nol karena itu akan menyesatkan model.
    clean_log.append("Interpolasi linear per negara dan standarisasi tipe data dilakukan.")
    return cleaned_df, clean_log


# -----------------------------------------------------------------------------
# 4. EXPLORATORY DATA ANALYSIS
# -----------------------------------------------------------------------------
def perform_eda(df: pd.DataFrame) -> dict:
    """Hitung statistik deskriptif, korelasi, dan ringkasan per negara."""
    numeric = df[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")
    stats_summary = numeric.describe()
    corr_matrix = numeric.corr()
    corr_pop_gdp = float(corr_matrix.loc["population", "gdp"]) if pd.notna(corr_matrix.loc["population", "gdp"]) else 0.0
    corr_unemp_gdp = float(corr_matrix.loc["unemployment_rate", "gdp"]) if pd.notna(corr_matrix.loc["unemployment_rate", "gdp"]) else 0.0

    country_summary = df.groupby("country").agg(
        gdp_mean=("gdp", "mean"),
        gdp_max=("gdp", "max"),
        gdp_min=("gdp", "min"),
        population_mean=("population", "mean"),
        population_max=("population", "max"),
        unemployment_mean=("unemployment_rate", "mean"),
        unemployment_min=("unemployment_rate", "min"),
        unemployment_max=("unemployment_rate", "max"),
    ).round(2)

    latest_year = int(df["year"].max())
    latest_data = df.loc[df["year"] == latest_year].sort_values("gdp", ascending=False).reset_index(drop=True)
    country_averages = df.groupby(["country_code", "country"], as_index=False).agg(
        gdp=("gdp", "mean"),
        population=("population", "mean"),
        unemployment_rate=("unemployment_rate", "mean"),
    )

    return {
        "stats_summary": stats_summary,
        "corr_matrix": corr_matrix,
        "corr_pop_gdp": corr_pop_gdp,
        "corr_unemp_gdp": corr_unemp_gdp,
        "country_summary": country_summary,
        "latest_year": latest_year,
        "latest_data": latest_data,
        "country_averages": country_averages,
    }


# -----------------------------------------------------------------------------
# 5. PEMODELAN MACHINE LEARNING
# -----------------------------------------------------------------------------
def train_model(df: pd.DataFrame) -> dict:
    """Latih Random Forest dengan pemisahan berdasarkan tiga tahun terakhir."""
    model_df = df[["country_code", "country", "year", "population", "unemployment_rate", "gdp"]].copy()
    model_df = model_df.dropna(subset=["gdp", "population", "unemployment_rate", "year"])
    model_df = model_df.sort_values(["year", "country_code"]).reset_index(drop=True)
    if len(model_df) < 4 or model_df["year"].nunique() < 2:
        raise ValueError("Data tidak cukup untuk melatih dan menguji model Random Forest.")

    years = sorted(model_df["year"].unique())
    test_years = years[-3:] if len(years) >= 5 else years[-1:]
    train_mask = ~model_df["year"].isin(test_years)
    test_mask = model_df["year"].isin(test_years)
    train_df = model_df.loc[train_mask].copy()
    test_df = model_df.loc[test_mask].copy()
    if train_df.empty or test_df.empty:
        split_idx = max(1, int(len(model_df) * 0.8))
        split_idx = min(split_idx, len(model_df) - 1)
        train_df, test_df = model_df.iloc[:split_idx].copy(), model_df.iloc[split_idx:].copy()

    feature_cols = ["year", "population", "unemployment_rate", "country_code"]
    X_all = pd.get_dummies(model_df[feature_cols], columns=["country_code"], dtype=int)
    y_all = model_df["gdp"]
    X_train = X_all.loc[train_df.index]
    y_train = y_all.loc[train_df.index]
    X_test = X_all.loc[test_df.index]
    y_test = y_all.loc[test_df.index]

    model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, predictions))
    mse = float(mean_squared_error(y_test, predictions))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, predictions)) if len(y_test) >= 2 else float("nan")

    feature_importance_df = pd.DataFrame({
        "Feature": X_train.columns,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=False).reset_index(drop=True)

    results_df = test_df[["country", "country_code", "year", "gdp"]].copy()
    results_df["predicted_gdp"] = predictions
    results_df["Actual_GDP_Trillion"] = (results_df["gdp"] / 1e12).round(3)
    results_df["Predicted_GDP_Trillion"] = (results_df["predicted_gdp"] / 1e12).round(3)
    results_df["Error_Trillion"] = (
        results_df["Predicted_GDP_Trillion"] - results_df["Actual_GDP_Trillion"]
    ).round(3)

    return {
        "model": model,
        "train_df": train_df,
        "test_df": test_df,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "feature_importance": feature_importance_df,
        "prediction_results": results_df,
        "train_years": (int(train_df["year"].min()), int(train_df["year"].max())),
        "test_years": (int(test_df["year"].min()), int(test_df["year"].max())),
    }


# -----------------------------------------------------------------------------
# 6. KESIMPULAN OTOMATIS
# -----------------------------------------------------------------------------
def generate_conclusions(eda_results: dict, model_results: dict, assess_report: dict) -> list:
    """Buat lima insight dari data EDA dan evaluasi model."""
    corr_pop = eda_results["corr_pop_gdp"]
    corr_unemp = eda_results["corr_unemp_gdp"]
    r2_val = model_results["r2"]
    mae_b = model_results["mae"] / 1e9
    top_feature = model_results["feature_importance"].iloc[0]

    if corr_pop >= 0.7:
        population_text = "terdapat hubungan positif kuat antara populasi dan GDP pada data yang dianalisis."
    elif corr_pop >= 0.3:
        population_text = "terdapat hubungan positif moderat antara populasi dan GDP pada data yang dianalisis."
    elif corr_pop > 0:
        population_text = "hubungan positif populasi dan GDP relatif lemah pada data yang dianalisis."
    else:
        population_text = "hubungan populasi dan GDP tidak positif pada data yang dianalisis."

    if corr_unemp <= -0.3:
        unemployment_text = "tingkat pengangguran memiliki hubungan negatif moderat hingga kuat dengan GDP."
    elif corr_unemp < 0:
        unemployment_text = "tingkat pengangguran memiliki hubungan negatif lemah dengan GDP."
    elif corr_unemp < 0.3:
        unemployment_text = "hubungan linear tingkat pengangguran dengan GDP relatif lemah atau mendekati nol."
    else:
        unemployment_text = "terdapat hubungan positif antara tingkat pengangguran dan GDP pada data yang dianalisis."

    r2_text = f"R² model sebesar {r2_val:.3f}" if np.isfinite(r2_val) else "R² tidak dapat dihitung secara andal karena data uji terlalu sedikit"
    return [
        {
            "category": "Integritas & Pemrosesan Data",
            "icon": "📦",
            "summary": "Data Pipeline Siap Analisis",
            "detail": (
                f"Data awal berisi {assess_report['total_rows']} baris. Data diperiksa, dibersihkan, "
                "dan nilai numerik yang hilang ditangani melalui interpolasi per negara bila memungkinkan."
            ),
        },
        {
            "category": "Hubungan Populasi & GDP",
            "icon": "👥",
            "summary": f"Korelasi Populasi: {corr_pop:.3f}",
            "detail": f"Korelasi Pearson populasi dengan GDP adalah {corr_pop:.3f}; {population_text} Korelasi bukan bukti sebab-akibat.",
        },
        {
            "category": "Hubungan Pengangguran & GDP",
            "icon": "📉",
            "summary": f"Korelasi Pengangguran: {corr_unemp:.3f}",
            "detail": f"Korelasi Pearson tingkat pengangguran dengan GDP adalah {corr_unemp:.3f}; {unemployment_text} Korelasi bukan bukti sebab-akibat.",
        },
        {
            "category": "Kinerja Pemodelan Machine Learning",
            "icon": "🤖",
            "summary": f"Skor R²: {r2_val:.3f}" if np.isfinite(r2_val) else "Skor R² tidak tersedia",
            "detail": f"Random Forest menghasilkan {r2_text} dengan MAE sekitar US${mae_b:.2f} miliar. Evaluasi menggunakan pemisahan data berdasarkan tahun.",
        },
        {
            "category": "Fitur Paling Berpengaruh",
            "icon": "⭐",
            "summary": f"Prediktor Utama: {top_feature['Feature']}",
            "detail": f"Fitur '{top_feature['Feature']}' memiliki feature importance {top_feature['Importance'] * 100:.1f}% pada model yang dilatih.",
        },
    ]


# -----------------------------------------------------------------------------
# PIPELINE UTAMA — API DIPERTAHANKAN UNTUK app.py
# -----------------------------------------------------------------------------
def run_full_pipeline(db_config: Optional[dict] = None, allow_api_fallback: bool = True) -> dict:
    """Jalankan seluruh enam tahap dan kembalikan struktur untuk dashboard."""
    raw_df, source = gather_data(db_config, allow_api_fallback)
    assessment = assess_data(raw_df)
    cleaned_df, clean_log = clean_data(raw_df)
    if cleaned_df.empty:
        raise ValueError("Dataset kosong setelah tahap Data Cleaning.")
    eda_results = perform_eda(cleaned_df)
    model_results = train_model(cleaned_df)
    conclusions = generate_conclusions(eda_results, model_results, assessment)

    return {
        "source": source,
        "raw_data": raw_df,
        "assessment_report": assessment,
        "cleaned_data": cleaned_df,
        "clean_log": clean_log,
        "eda_results": eda_results,
        "model_results": model_results,
        "conclusions": conclusions,
    }


# -----------------------------------------------------------------------------
# EKSEKUSI CLI LANGSUNG
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("MENJALANKAN PIPELINE ANALISIS DATA EKONOMI DARI PROCESS.PY")
    print("Sumber MySQL: JOIN langsung tanpa economic_combined")
    print("=" * 70)
    results = run_full_pipeline()
    print(f"\n[1] Data Gathering : Sumber: {results['source']}, Total Baris: {len(results['raw_data'])}")
    print(f"[2] Data Assessing : {len(results['assessment_report']['issues'])} temuan/kondisi diperiksa.")
    print(f"[3] Data Cleaning  : {len(results['clean_log'])} aksi pembersihan dilakukan.")
    print(f"[4] EDA            : Korelasi Pop-GDP = {results['eda_results']['corr_pop_gdp']:.3f}, Unemp-GDP = {results['eda_results']['corr_unemp_gdp']:.3f}")
    print(f"[5] Pemodelan      : R2 = {results['model_results']['r2']:.3f}, MAE = ${results['model_results']['mae'] / 1e9:.2f} B")
    print(f"[6] Kesimpulan     : {len(results['conclusions'])} poin kesimpulan dihasilkan.")
    print("\nPipeline Berhasil Dijalankan!")
