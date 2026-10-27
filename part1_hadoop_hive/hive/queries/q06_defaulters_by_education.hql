-- Aggregation: number of clients in credit default per education level
SELECT education,
       COUNT(*) AS clients_in_default
FROM banking_data.client_info
WHERE `default` = 'yes'
GROUP BY education
ORDER BY clients_in_default DESC;
