
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  WITH today AS (
    SELECT date_key FROM dim_dates WHERE full_date = CURRENT_DATE
)
SELECT *
FROM "warehouse"."main"."fct_messages"
WHERE date_key > (SELECT date_key FROM today)
  
  
      
    ) dbt_internal_test