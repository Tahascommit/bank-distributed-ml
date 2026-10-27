-- Top 5 jobs by average balance, and the % of clients in each that subscribed to a term deposit
SELECT job,
       COUNT(*)                                                        AS clients,
       ROUND(AVG(balance), 2)                                          AS avg_balance,
       ROUND(100 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS subscribed_pct
FROM banking_data.client_info
GROUP BY job
ORDER BY avg_balance DESC
LIMIT 5;
