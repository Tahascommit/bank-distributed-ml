-- Anomalies in the average yearly balance across education levels.
-- Per education level: spread of the balance, plus clients far above their group
-- (more than 3 standard deviations over the group mean) and clients with a negative balance.
WITH stats AS (
  SELECT education,
         COUNT(*)                                AS clients,
         ROUND(AVG(balance), 0)                  AS avg_balance,
         ROUND(percentile_approx(balance, 0.5), 0) AS median_balance,
         ROUND(STDDEV_POP(balance), 0)           AS std_balance,
         MIN(balance)                            AS min_balance,
         MAX(balance)                            AS max_balance
  FROM banking_data.client_info
  GROUP BY education
),
flags AS (
  SELECT c.education,
         SUM(CASE WHEN c.balance > s.avg_balance + 3 * s.std_balance THEN 1 ELSE 0 END) AS extreme_high,
         SUM(CASE WHEN c.balance < 0 THEN 1 ELSE 0 END)                                AS negative
  FROM banking_data.client_info c
  JOIN stats s ON c.education = s.education
  GROUP BY c.education
)
SELECT s.education, s.clients, s.avg_balance, s.median_balance, s.std_balance,
       s.min_balance, s.max_balance, f.extreme_high, f.negative
FROM stats s
JOIN flags f ON s.education = f.education
ORDER BY s.avg_balance DESC;
