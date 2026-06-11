
Step 2

1. AVG() calculates the arithmetic mean of all values, while PERCENTILE_CONT(0.5) calculates the median value. Median is more honest for skewed data because it is less affected by extreme outliers.

2. We needed window functions in Q5 because ORDER BY ... DESC LIMIT 20 can only return the top 20 customers, but it cannot generate rankings or compare each row with the previous one. Window functions such as RANK() and LAG() allow us to assign rankings and calculate the gap between customers without collapsing the result set.

Q6 identifies customers whose monthly spending increased significantly compared to the previous month. The query uses a chain of three CTEs to first calculate monthly customer spending, then compare each month with the previous one using the LAG() window function, and finally calculate the percentage growth. This helps detect customers with strong upward purchasing trends.


Step 3

1. When would you choose orders (referenced) over orders_embedded ?
1. I would use the referenced orders collection when I need a more normalized design and when order items may be queried or maintained separately from orders.

2. When would you choose orders_embedded over orders ?
2. I would use the embedded orders collection when orders and their items are almost always retrieved together, because it makes queries simpler and often faster.

## Side-by-side: SQL vs. MongoDB

### Q1 — Monthly revenue trend

| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | ~8             | ~15     |
| Wall time (ms)  | 84             | 492     |
| Subjective ease | ★★★★★          | ★★★☆☆   |

**My take:**
PostgreSQL's `date_trunc('month', order_date)` is a single expression, while MongoDB requires `$year` and `$month` separately. SQL is more concise, but MongoDB's aggregation pipeline makes each processing step explicit.

---

### Q2 — Top 10 products by revenue

| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | ~10            | ~35     |
| Wall time (ms)  | 486            | 2319    |
| Subjective ease | ★★★★★          | ★★☆☆☆   |

**My take:**
SQL expresses this query naturally using `JOIN`, `GROUP BY`, and aggregate functions. MongoDB requires `$unwind`, `$group`, `$lookup`, `$project`, and `$sort`. The MongoDB solution is more verbose but demonstrates how aggregation pipelines can replace relational joins.

---

### Q3 — Average and median order value by status

| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | ~8             | ~20     |
| Wall time (ms)  | 359            | 490     |
| Subjective ease | ★★★★☆          | ★★★★☆   |

**My take:**
This query translates well between the two systems. PostgreSQL uses `AVG()` and `PERCENTILE_CONT()`, while MongoDB uses `$avg` and `$median`. The logic is very similar in both databases.

---

### Q4 — Dormant customers

| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | ~10            | ~35     |
| Wall time (ms)  | 96             | 1112    |
| Subjective ease | ★★★★☆          | ★★★☆☆   |

**My take:**
SQL handles this with `MAX()`, `GROUP BY`, and `HAVING`. MongoDB requires several aggregation stages, including `$group`, `$dateDiff`, `$match`, and `$lookup`. The result is equivalent, but the SQL version is shorter and easier to read.

---

### Q5 — Top customers by lifetime spend

| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | ~15            | ~45     |
| Wall time (ms)  | 100            | 2664    |
| Subjective ease | ★★★★★          | ★★☆☆☆   |

**My take:**
This was the most advanced query in the lab. PostgreSQL's `RANK()` and `LAG()` window functions are concise and expressive. MongoDB achieves the same result using `$setWindowFields`, `$rank`, and `$shift`, but the syntax is considerably more verbose.

---

### Summary

For analytical workloads, PostgreSQL was generally more concise and faster on this dataset. The SQL queries were shorter, easier to read, and consistently executed faster than their MongoDB equivalents. MongoDB required longer aggregation pipelines, especially when joins, ranking, or window-style calculations were involved. However, MongoDB handled embedded documents naturally and provided flexible aggregation capabilities. I would choose SQL for reporting, analytics, and structured business data, MongoDB for document-oriented data models, and both together when an application needs transactional consistency as well as flexible document storage.
