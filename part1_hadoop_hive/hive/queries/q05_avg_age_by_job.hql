-- Aggregation: average age per job category
SELECT job,
       COUNT(*)           AS clients,
       ROUND(AVG(age), 1) AS avg_age
FROM banking_data.client_info
GROUP BY job
ORDER BY avg_age DESC;
