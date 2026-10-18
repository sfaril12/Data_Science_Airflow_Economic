

from pathlib import Path

path = Path(r"C:\Users\safar\airflow-economic\dags\etl_economic_to_mysql.py")
source = path.read_text(encoding="utf-8")
updated = source

old_transform = '''                (
                    country_code,
                    year,
                    value
                )'''

new_transform = '''                (
                    country_code,
                    year,
                    value,
                    country_code
                )'''

old_gdp = '''        gdp_sql = """
            INSERT INTO gdp
            (
                country_code,
                year,
                gdp
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                gdp = VALUES(gdp);
        """'''

new_gdp = '''        gdp_sql = """
            INSERT INTO gdp
                (country_code, year, gdp, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                gdp = VALUES(gdp),
                country_id = VALUES(country_id);
        """'''

old_population = '''        population_sql = """
            INSERT INTO population
            (
                country_code,
                year,
                population
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                population = VALUES(population);
        """'''

new_population = '''        population_sql = """
            INSERT INTO population
                (country_code, year, population, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                population = VALUES(population),
                country_id = VALUES(country_id);
        """'''

old_unemployment = '''        unemployment_sql = """
            INSERT INTO unemployment
            (
                country_code,
                year,
                unemployment_rate
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                unemployment_rate = VALUES(unemployment_rate);
        """'''

new_unemployment = '''        unemployment_sql = """
            INSERT INTO unemployment
                (country_code, year, unemployment_rate, country_id)
            SELECT %s, %s, %s, country_id
            FROM countries
            WHERE country_code = %s
            ON DUPLICATE KEY UPDATE
                unemployment_rate = VALUES(unemployment_rate),
                country_id = VALUES(country_id);
        """'''

replacements = [
    (old_transform, new_transform, "Transform tuple"),
    (old_gdp, new_gdp, "GDP SQL"),
    (old_population, new_population, "Population SQL"),
    (old_unemployment, new_unemployment, "Unemployment SQL"),
]

for old, new, label in replacements:
    count = updated.count(old)
    if count != 1:
        raise SystemExit(
            f"GAGAL: bagian {label} ditemukan {count} kali. "
            "File asli tidak diubah."
        )
    updated = updated.replace(old, new, 1)

# Pastikan jadwal DAG tetap manual.
if "schedule=None" not in updated:
    raise SystemExit("GAGAL: schedule=None tidak ditemukan.")

compile(updated, str(path), "exec")
path.write_text(updated, encoding="utf-8")
print("BERHASIL: kode ETL diperbarui dan lolos pemeriksaan sintaks.")
