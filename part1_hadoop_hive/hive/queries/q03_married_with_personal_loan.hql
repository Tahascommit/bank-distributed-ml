-- Filtering: all clients who are married and have a personal loan
SELECT *
FROM banking_data.client_info
WHERE marital = 'married'
  AND loan = 'yes';
