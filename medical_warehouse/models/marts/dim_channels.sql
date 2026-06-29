
WITH channel_stats AS (
    SELECT
        channel_name,
        COUNT(*) AS total_posts,
        AVG(views) AS avg_views,
        MIN(message_date) AS first_post_date,
        MAX(message_date) AS last_post_date,
        CASE
            WHEN LOWER(channel_name) LIKE '%chemed%' THEN 'Medical'
            WHEN LOWER(channel_name) LIKE '%lobelia%' THEN 'Cosmetics'
            WHEN LOWER(channel_name) LIKE '%tikvah%' THEN 'Pharmaceutical'
            ELSE 'Other'
        END AS channel_type
    FROM {{ ref('stg_telegram_messages') }}
    GROUP BY channel_name
)
SELECT
    ROW_NUMBER() OVER (ORDER BY channel_name) AS channel_key,
    channel_name,
    channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
FROM channel_stats
