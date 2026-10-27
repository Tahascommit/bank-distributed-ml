-- The month with the most contacts, and the campaign success rate in that month
SELECT `month`,
       COUNT(*)                                                        AS contacts,
       SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
       ROUND(100 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
FROM banking_data.client_info
GROUP BY `month`
ORDER BY contacts DESC
LIMIT 1;
