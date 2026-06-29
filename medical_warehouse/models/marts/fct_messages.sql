
SELECT
    s.message_key,
    s.message_id,
    d_ch.channel_key,
    d_dt.date_key,
    s.message_text,
    s.message_length,
    s.views AS view_count,
    s.forwards AS forward_count,
    s.has_image_flag AS has_image
FROM {{ ref('stg_telegram_messages') }} s
LEFT JOIN {{ ref('dim_channels') }} d_ch ON s.channel_name = d_ch.channel_name
LEFT JOIN {{ ref('dim_dates') }} d_dt ON DATE(s.message_date) = d_dt.full_date
