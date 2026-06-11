
1. AVG() calculates the arithmetic mean of all values, while PERCENTILE_CONT(0.5) calculates the median value. Median is more honest for skewed data because it is less affected by extreme outliers.

2. We needed window functions in Q5 because ORDER BY ... DESC LIMIT 20 can only return the top 20 customers, but it cannot generate rankings or compare each row with the previous one. Window functions such as RANK() and LAG() allow us to assign rankings and calculate the gap between customers without collapsing the result set.

Q6 identifies customers whose monthly spending increased significantly compared to the previous month. The query uses a chain of three CTEs to first calculate monthly customer spending, then compare each month with the previous one using the LAG() window function, and finally calculate the percentage growth. This helps detect customers with strong upward purchasing trends.