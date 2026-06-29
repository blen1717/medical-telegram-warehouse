
  
    
    

    create  table
      "warehouse"."main"."dim_dates__dbt_tmp"
  
    as (
      WITH date_series AS (
    SELECT DISTINCT DATE(message_date) AS full_date
    FROM "warehouse"."main"."stg_telegram_messages"
)
SELECT
    CAST(strftime(full_date, '%Y%m%d') AS INT) AS date_key,
    full_date,
    EXTRACT(DOW FROM full_date) AS day_of_week,
    strftime(full_date, '%A') AS day_name,
    EXTRACT(WEEK FROM full_date) AS week_of_year,
    EXTRACT(MONTH FROM full_date) AS month,
    strftime(full_date, '%B') AS month_name,
    EXTRACT(QUARTER FROM full_date) AS quarter,
    EXTRACT(YEAR FROM full_date) AS year,
    CASE WHEN EXTRACT(DOW FROM full_date) IN (0,6) THEN 1 ELSE 0 END AS is_weekend
FROM date_series
    );
  
  