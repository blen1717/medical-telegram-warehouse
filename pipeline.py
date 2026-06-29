
import os
import subprocess
from dagster import op, job, schedule, RunRequest

PROJECT_ROOT = "/content/drive/MyDrive/medical_telegram_warehouse"

@op
def scrape_data(context):
    context.log.info("Running scraper...")
    subprocess.run(["python", f"{PROJECT_ROOT}/src/telegram_scraper.py", "--demo", "--path", "data", "--limit", "20"], check=True)
    return "scraped"

@op
def load_data(context, scraped_data):
    context.log.info("Data is accessible via DuckDB views. Received: " + scraped_data)
    return "loaded"

@op
def run_dbt(context, loaded_data):
    context.log.info("Running dbt...")
    subprocess.run(["dbt", "run", "--profiles-dir", f"{PROJECT_ROOT}/medical_warehouse", "--project-dir", f"{PROJECT_ROOT}/medical_warehouse"], check=True)
    return "dbt_done"

@op
def run_yolo(context, dbt_done):
    context.log.info("Running YOLO...")
    # Ensure the script exists
    script_path = f"{PROJECT_ROOT}/scripts/run_yolo.py"
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    subprocess.run(["python", script_path], check=True)
    return "yolo_done"

@job
def full_pipeline():
    scraped = scrape_data()
    loaded = load_data(scraped)
    dbt_result = run_dbt(loaded)
    yolo_result = run_yolo(dbt_result)

@schedule(cron_schedule="0 2 * * *", job=full_pipeline, execution_timezone="UTC")
def daily_schedule(context):
    return RunRequest(run_key=None)
