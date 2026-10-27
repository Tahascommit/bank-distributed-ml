-- Sorting: top 10 clients by balance, with job and marital status
SELECT job, marital, balance
FROM banking_data.client_info
ORDER BY balance DESC
LIMIT 10;
