-- Average contact duration for clients who subscribed vs those who did not
SELECT y                               AS subscribed,
       COUNT(*)                        AS clients,
       ROUND(AVG(duration), 1)         AS avg_duration_sec,
       ROUND(AVG(duration) / 60, 1)    AS avg_duration_min,
       ROUND(percentile_approx(duration, 0.5), 0) AS median_duration_sec
FROM banking_data.client_info
GROUP BY y;
