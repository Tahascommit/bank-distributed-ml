-- Trend in the number of clients contacted.
-- The dataset has no year column (only day and month), so a real year-over-year comparison
-- is not possible. Instead: contacts per calendar month and the change versus the previous month.
WITH monthly AS (
  SELECT `month`,
         CASE `month` WHEN 'jan' THEN 1 WHEN 'feb' THEN 2 WHEN 'mar' THEN 3 WHEN 'apr' THEN 4
                      WHEN 'may' THEN 5 WHEN 'jun' THEN 6 WHEN 'jul' THEN 7 WHEN 'aug' THEN 8
                      WHEN 'sep' THEN 9 WHEN 'oct' THEN 10 WHEN 'nov' THEN 11 ELSE 12 END AS month_no,
         COUNT(*) AS clients_contacted
  FROM banking_data.client_info
  GROUP BY `month`
)
SELECT `month`,
       clients_contacted,
       clients_contacted - LAG(clients_contacted) OVER (ORDER BY month_no) AS change_vs_prev_month,
       ROUND(100 * clients_contacted / SUM(clients_contacted) OVER (), 1)  AS share_of_contacts_pct
FROM monthly
ORDER BY month_no;
