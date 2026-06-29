
  
    
    

    create  table
      "warehouse"."main"."fct_image_detections__dbt_tmp"
  
    as (
      SELECT
    y.message_id,
    f.channel_key,
    f.date_key,
    y.image_category,
    y.has_person,
    y.has_product,
    y.detected_classes
FROM raw.yolo_detections y
JOIN "warehouse"."main"."fct_messages" f ON y.message_id = f.message_id
    );
  
  