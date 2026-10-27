-- Impact of the previous campaign outcome on this campaign: subscription rate per poutcome
SELECT poutcome,
       COUNT(*)                                                        AS clients,
       SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
       ROUND(100 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS subscription_rate_pct
FROM banking_data.client_info
GROUP BY poutcome
ORDER BY subscription_rate_pct DESC;
