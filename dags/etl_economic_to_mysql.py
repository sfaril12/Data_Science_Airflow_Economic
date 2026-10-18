from datetime import datetime

import requests

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook


# =========================================================
# KONFIGURASI
# =========================================================

COUNTRIES = [
    "IDN",  # Indonesia
    "MYS",  # Malaysia
    "SGP",  # Singapore
    "THA",  # Thailand
    "PHL",  # Philippines
    "VNM",  # Vietnam
]

INDICATORS = {
    "gdp": "NY.GDP.MKTP.CD",
    "population": "SP.POP.TOTL",
    "unemployment": "SL.UEM.TOTL.ZS",
}


# =========================================================
# EXTRACT
# =========================================================

def extract_economic_data():

    extracted_data = {
        "gdp": [],
        "population": [],
        "unemployment": [],
    }

    # Gabungkan semua negara menjadi satu parameter
    # sehingga hanya membutuhkan 3 request API.
    countries = ";".join(COUNTRIES)

    session = requests.Session()

    for data_name, indicator in INDICATORS.items():

        url = (
            f"https://api.worldbank.org/v2/"
            f"country/{countries}/indicator/{indicator}"
            f"?format=json&per_page=500"
        )

        print("\n" + "=" * 60)
        print(f"MENGAMBIL DATA: {data_name.upper()}")
        print("=" * 60)

        print(f"URL: {url}")

        # Retry maksimal 3 kali
        for attempt in range(1, 4):

            try:

                print(
                    f"Percobaan {attempt}/3..."
                )

                response = session.get(
                    url,
                    timeout=(10, 60)
                )

                response.raise_for_status()

                data = response.json()

                # Pastikan response mempunyai data
                if len(data) <= 1 or not data[1]:

                    print(
                        f"Tidak ada data untuk {data_name}"
                    )

                    break

                records = data[1]

                print(
                    f"Berhasil mengambil "
                    f"{len(records)} records"
                )

                # Simpan data yang valid
                for record in records:

                    country_code = record.get(
                        "countryiso3code"
                    )

                    year = record.get(
                        "date"
                    )

                    value = record.get(
                        "value"
                    )

                    # Buang data yang tidak lengkap
                    if (
                        country_code
                        and year
                        and value is not None
                    ):

                        extracted_data[data_name].append(
                            {
                                "country_code": country_code,
                                "year": int(year),
                                "value": value,
                            }
                        )

                # Jika berhasil, keluar dari retry
                break

            except requests.RequestException as e:

                print(
                    f"Percobaan {attempt}/3 gagal:"
                )

                print(e)

                # Jika percobaan terakhir gagal,
                # hentikan task.
                if attempt == 3:
                    raise

    # =====================================================
    # HASIL EXTRACT
    # =====================================================

    print("\n")
    print("=" * 60)
    print("HASIL EXTRACT")
    print("=" * 60)

    for data_name, records in extracted_data.items():

        print(
            f"{data_name}: "
            f"{len(records)} records"
        )

    # Pastikan Extract menghasilkan data
    total_records = sum(
        len(records)
        for records in extracted_data.values()
    )

    if total_records == 0:

        raise ValueError(
            "Extract menghasilkan 0 records!"
        )

    return extracted_data


# =========================================================
# TRANSFORM
# =========================================================

def transform_economic_data(**context):

    # Ambil hasil Extract dari XCom
    extracted_data = context["ti"].xcom_pull(
        task_ids="extract_economic_data"
    )

    print("\n")
    print("=" * 60)
    print("DATA DARI EXTRACT")
    print("=" * 60)

    # Pastikan data Extract tersedia
    if extracted_data is None:

        raise ValueError(
            "Data dari extract_economic_data "
            "tidak ditemukan di XCom!"
        )

    # Tampilkan jumlah data yang diterima
    for data_name, records in extracted_data.items():

        print(
            f"{data_name}: "
            f"{len(records)} records"
        )

    # Struktur data hasil transformasi
    transformed_data = {
        "gdp": [],
        "population": [],
        "unemployment": [],
    }

    # =====================================================
    # PROSES TRANSFORMASI
    # =====================================================

    for data_name, records in extracted_data.items():

        for record in records:

            country_code = record["country_code"]

            year = int(
                record["year"]
            )

            value = record["value"]

            # Buang nilai kosong
            if value is None:
                continue

            # Transformasi tipe data
            if data_name == "population":

                value = int(value)

            else:

                value = float(value)

            # Bentuk tuple untuk INSERT MySQL
            transformed_data[data_name].append(
                (
                    country_code,
                    year,
                    value,
                    country_code
                )
            )

    # =====================================================
    # HASIL TRANSFORM
    # =====================================================

    print("\n")
    print("=" * 60)
    print("HASIL TRANSFORM")
    print("=" * 60)

    for data_name, records in transformed_data.items():

        print(
            f"{data_name}: "
            f"{len(records)} records"
        )

    # Pastikan Transform menghasilkan data
    total_records = sum(
        len(records)
        for records in transformed_data.values()
    )

    if total_records == 0:

        raise ValueError(
            "Transform menghasilkan 0 records!"
        )

    return transformed_data


# =========================================================
# LOAD
# =========================================================

def load_economic_data(**context):

    # Ambil hasil Transform dari XCom
    transformed_data = context["ti"].xcom_pull(
        task_ids="transform_economic_data"
    )

    print("\n")
    print("=" * 60)
    print("DATA DARI TRANSFORM")
    print("=" * 60)

    # Pastikan data Transform tersedia
    if transformed_data is None:

        raise ValueError(
            "Data dari transform_economic_data "
            "tidak ditemukan di XCom!"
        )

    print(
        f"GDP          : "
        f"{len(transformed_data['gdp'])} records"
    )

    print(
        f"Population   : "
        f"{len(transformed_data['population'])} records"
    )

    print(
        f"Unemployment : "
        f"{len(transformed_data['unemployment'])} records"
    )

    # =====================================================
    # KONEKSI MYSQL
    # =====================================================

    hook = MySqlHook(
        mysql_conn_id="mysql-economic"
    )

    connection = hook.get_conn()

    cursor = connection.cursor()

    try:

        # =================================================
        # LOAD GDP
        # =================================================

        gdp_sql = """
            INSERT INTO gdp
                (country_code, year, gdp, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                gdp = VALUES(gdp),
                country_id = VALUES(country_id);
        """

        cursor.executemany(
            gdp_sql,
            transformed_data["gdp"]
        )

        print(
            f"\nGDP berhasil diproses: "
            f"{len(transformed_data['gdp'])} records"
        )

        # =================================================
        # LOAD POPULATION
        # =================================================

        population_sql = """
            INSERT INTO population
                (country_code, year, population, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                population = VALUES(population),
                country_id = VALUES(country_id);
        """

        cursor.executemany(
            population_sql,
            transformed_data["population"]
        )

        print(
            f"Population berhasil diproses: "
            f"{len(transformed_data['population'])} records"
        )

        # =================================================
        # LOAD UNEMPLOYMENT
        # =================================================

        unemployment_sql = """
            INSERT INTO unemployment
                (country_code, year, unemployment_rate, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                unemployment_rate = VALUES(unemployment_rate),
                country_id = VALUES(country_id);
        """

        cursor.executemany(
            unemployment_sql,
            transformed_data["unemployment"]
        )

        print(
            f"Unemployment berhasil diproses: "
            f"{len(transformed_data['unemployment'])} records"
        )

        # =================================================
        # COMMIT
        # =================================================

        connection.commit()

        print("\n")
        print("=" * 60)
        print("HASIL LOAD")
        print("=" * 60)

        print(
            f"GDP          : "
            f"{len(transformed_data['gdp'])} records"
        )

        print(
            f"Population   : "
            f"{len(transformed_data['population'])} records"
        )

        print(
            f"Unemployment : "
            f"{len(transformed_data['unemployment'])} records"
        )

        print(
            "\nDATA BERHASIL DIMASUKKAN KE MYSQL!"
        )

    except Exception as e:

        # Jika terjadi error, batalkan transaksi
        connection.rollback()

        print(
            "\nLOAD GAGAL!"
        )

        print(e)

        raise

    finally:

        cursor.close()

        connection.close()


# =========================================================
# DAG
# =========================================================

with DAG(

    dag_id="etl_economic_to_mysql",

    start_date=datetime(
        2026,
        9,
        30
    ),

    schedule=None,

    catchup=False,

    tags=[
        "economic",
        "etl",
        "worldbank"
    ],

) as dag:

    # =====================================================
    # CREATE TABLES
    # =====================================================

    create_tables = SQLExecuteQueryOperator(

        task_id="create_tables",

        conn_id="mysql-economic",

        split_statements=True,

        sql="""
        CREATE TABLE IF NOT EXISTS countries (
            country_id INT AUTO_INCREMENT PRIMARY KEY,
            country_code VARCHAR(3) NOT NULL UNIQUE,
            country_name VARCHAR(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS gdp (
            id INT AUTO_INCREMENT PRIMARY KEY,
            country_code VARCHAR(3) NOT NULL,
            country_id INT NULL,
            year INT NOT NULL,
            gdp DOUBLE,
            UNIQUE KEY unique_country_year (country_code, year),
            CONSTRAINT fk_gdp_country
                FOREIGN KEY (country_id)
                REFERENCES countries(country_id)
        );

        CREATE TABLE IF NOT EXISTS population (
            id INT AUTO_INCREMENT PRIMARY KEY,
            country_code VARCHAR(3) NOT NULL,
            country_id INT NULL,
            year INT NOT NULL,
            population BIGINT,
            UNIQUE KEY unique_country_year (country_code, year),
            CONSTRAINT fk_population_country
                FOREIGN KEY (country_id)
                REFERENCES countries(country_id)
        );

        CREATE TABLE IF NOT EXISTS unemployment (
            id INT AUTO_INCREMENT PRIMARY KEY,
            country_code VARCHAR(3) NOT NULL,
            country_id INT NULL,
            year INT NOT NULL,
            unemployment_rate DOUBLE,
            UNIQUE KEY unique_country_year (country_code, year),
            CONSTRAINT fk_unemployment_country
                FOREIGN KEY (country_id)
                REFERENCES countries(country_id)
        );
        """,
    )


    # =====================================================
    # EXTRACT TASK
    # =====================================================

    extract_task = PythonOperator(

        task_id="extract_economic_data",

        python_callable=extract_economic_data,

    )


    # =====================================================
    # TRANSFORM TASK
    # =====================================================

    transform_task = PythonOperator(

        task_id="transform_economic_data",

        python_callable=transform_economic_data,

    )


    # =====================================================
    # LOAD TASK
    # =====================================================

    load_task = PythonOperator(

        task_id="load_economic_data",

        python_callable=load_economic_data,

    )


    # =====================================================
    # WORKFLOW
    # =====================================================

    create_tables >> extract_task >> transform_task >> load_task