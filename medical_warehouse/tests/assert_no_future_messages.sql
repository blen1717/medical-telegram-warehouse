
WITH today AS (
    SELECT date_key FROM dim_dates WHERE full_date = CURRENT_DATE
)
SELECT *
FROM {{ ref('fct_messages') }}
WHERE date_key > (SELECT date_key FROM today)
