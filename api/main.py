
from fastapi import FastAPI, HTTPException, Query
import duckdb
import os

DB_PATH = "/content/drive/MyDrive/medical_telegram_warehouse/warehouse.duckdb"

app = FastAPI(title="Medical Telegram Analytics API")

def get_db():
    return duckdb.connect(database=DB_PATH, read_only=True)

@app.get("/api/reports/top-products")
def top_products(limit: int = Query(10, ge=1, le=100)):
    conn = get_db()
    query = f"""
        WITH words AS (
            SELECT 
                LOWER(REGEXP_REPLACE(message_text, '[^a-zA-Z0-9 ]', ' ', 'g')) AS clean_text
            FROM fct_messages
        ),
        split AS (
            SELECT UNNEST(string_split(clean_text, ' ')) AS term
            FROM words
        )
        SELECT 
            term,
            COUNT(*) AS frequency
        FROM split
        WHERE LENGTH(term) > 3
          AND term NOT IN ('the','and','for','with','this','that','from','have','are','you','your','not','but','all','can','has','its','was','were','will','would','could','should')
        GROUP BY term
        ORDER BY frequency DESC
        LIMIT {limit}
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return [{"term": r[0], "frequency": r[1]} for r in results]

@app.get("/api/channels/{channel_name}/activity")
def channel_activity(channel_name: str):
    conn = get_db()
    query = f"""
        SELECT 
            d.full_date,
            COUNT(*) AS post_count,
            AVG(f.view_count) AS avg_views
        FROM fct_messages f
        JOIN dim_dates d ON f.date_key = d.date_key
        JOIN dim_channels c ON f.channel_key = c.channel_key
        WHERE c.channel_name = '{channel_name}'
        GROUP BY d.full_date
        ORDER BY d.full_date DESC
        LIMIT 30
    """
    results = conn.execute(query).fetchall()
    conn.close()
    if not results:
        raise HTTPException(404, "Channel not found")
    return [{"date": str(r[0]), "posts": r[1], "avg_views": float(r[2])} for r in results]

@app.get("/api/search/messages")
def search_messages(query: str, limit: int = Query(20, le=100)):
    conn = get_db()
    sql = f"""
        SELECT message_id, message_text, view_count, forward_count
        FROM fct_messages
        WHERE LOWER(message_text) LIKE LOWER('%{query}%')
        ORDER BY view_count DESC
        LIMIT {limit}
    """
    results = conn.execute(sql).fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "views": r[2], "forwards": r[3]} for r in results]

@app.get("/api/reports/visual-content")
def visual_content_stats():
    conn = get_db()
    query = """
        SELECT 
            c.channel_name,
            COUNT(f.message_id) AS total_posts,
            SUM(f.has_image) AS image_posts,
            ROUND(100.0 * SUM(f.has_image) / COUNT(f.message_id), 2) AS image_percentage
        FROM fct_messages f
        JOIN dim_channels c ON f.channel_key = c.channel_key
        GROUP BY c.channel_name
        ORDER BY image_percentage DESC
    """
    results = conn.execute(query).fetchall()
    conn.close()
    return [{"channel": r[0], "total": r[1], "images": r[2], "percentage": float(r[3])} for r in results]
