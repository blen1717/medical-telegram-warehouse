
  
    
    

    create  table
      "warehouse"."main"."fct_messages__dbt_tmp"
  
    as (
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
FROM "warehouse"."main"."stg_telegram_messages" s
LEFT JOIN "warehouse"."main"."dim_channels" d_ch ON s.channel_name = d_ch.channel_name
LEFT JOIN "warehouse"."main"."dim_dates" d_dt ON DATE(s.message_date) = d_dt.full_date
    );
  
  