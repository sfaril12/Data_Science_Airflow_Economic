
from pathlib import Path

path = Path(
    r"C:\Users\safar\airflow-economic\dags\etl_economic_to_mysql.py"
)

source = path.read_text(encoding="utf-8")

start_marker = '        sql="""'
end_marker = '        """,'

start = source.find(start_marker, source.find('task_id="create_tables"'))

if start == -1:
    raise SystemExit("Blok SQL create_tables tidak ditemukan.")

end = source.find(end_marker, start)

if end == -1:
    raise SystemExit("Akhir blok SQL create_tables tidak ditemukan.")

end += len(end_marker)

new_sql = '''        sql="""
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
        """,'''

updated = source[:start] + new_sql + source[end:]

compile(updated, str(path), "exec")
path.write_text(updated, encoding="utf-8")

print("Blok create_tables berhasil diperbarui.")
print("Jadwal manual dan task ETL lainnya tetap dipertahankan.")
