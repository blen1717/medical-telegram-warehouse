
  
  create view "warehouse"."main"."stg_telegram_messages__dbt_tmp" as (
    SELECT
    CONCAT(channel_name, '_', message_id) AS message_key,
    message_id,
    channel_name,
    channel_title,
    message_date::TIMESTAMP AS message_date,
    message_text,
    has_media,
    image_path,
    views::INT AS views,
    forwards::INT AS forwards,
    LENGTH(message_text) AS message_length,
    CASE WHEN has_media THEN 1 ELSE 0 END AS has_image_flag,
    NOW() AS loaded_at
FROM telegram_messages
WHERE message_text IS NOT NULL AND TRIM(message_text) != ''
  );
