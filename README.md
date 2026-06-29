
# Medical Telegram Warehouse

End-to-end data pipeline for Telegram medical channels, using dbt for transformation, Dagster for orchestration, and YOLOv8 for data enrichment.

## Tasks Completed
- ✅ Task 1: Data scraping and data lake (JSONs, images, CSV, logs)
- ✅ Task 2: dbt transformations with star schema
- ✅ Task 3: YOLO image enrichment
- ✅ Task 4: FastAPI analytical endpoints
- ✅ Task 5: Dagster pipeline orchestration

## How to Run
1. Install dependencies: pip install -r requirements.txt
2. Run scraper: python src/telegram_scraper.py --demo --path data --limit 20
3. Run dbt: cd medical_warehouse && dbt run && dbt test
4. Start API: uvicorn api.main:app --host 0.0.0.0 --port 8000
5. Run Dagster: dagster job execute -f pipeline.py -j full_pipeline

## License
MIT
