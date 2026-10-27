-- Correlation between age and balance (Pearson)
SELECT ROUND(corr(age, balance), 4)     AS corr_age_balance,
       ROUND(AVG(age), 1)               AS avg_age,
       ROUND(AVG(balance), 1)           AS avg_balance
FROM banking_data.client_info;
