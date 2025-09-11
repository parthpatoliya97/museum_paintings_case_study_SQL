## SQL PROJECT - Museum Paintings And Sales Analysis

![painting image](https://static.vecteezy.com/system/resources/previews/033/473/130/non_2x/modern-bright-drink-room-interiors-with-art-wallpaper-ai-generated-photo.jpg)

ER Diagram :-
![ER_Diagram](https://github.com/parthpatoliya97/museum_paintings_case_study_SQL/blob/main/ER%20Diagram.png?raw=true)

#### Key Relationships :-
- artist ↔ work: One-to-many (one artist can have many works)
- museum ↔ work: One-to-many (one museum can have many works)
- work ↔ image_link: One-to-one (each work has one set of image links)
- work ↔ subject: One-to-one (each work has one subject entry)
- museum ↔ museum_hours: One-to-many (one museum has multiple opening hours)
- work ↔ product_size: Many-to-many through junction table (works can have multiple sizes/prices)
- canvas_size ↔ product_size: Many-to-many through junction table

#### Dataset :-
[Kaggle Dataset Link](https://www.kaggle.com/datasets/mexwell/famous-paintings)

#### 1️. Fetch all the paintings which are not displayed in any museum
```sql
SELECT a.full_name,
       a.nationality,
       w.name AS painting_name
FROM artist a
LEFT JOIN work w ON a.artist_id = w.artist_id
LEFT JOIN museum m ON w.museum_id = m.museum_id
WHERE m.museum_id IS NULL;
```


#### Total count of such paintings
```sql
SELECT COUNT(*)
FROM work w
LEFT JOIN museum m ON w.museum_id = m.museum_id
WHERE m.museum_id IS NULL;
```

#### 2️. Are there museums without any paintings?
```sql
SELECT m.museum_id, m.name
FROM museum m
LEFT JOIN work w ON m.museum_id = w.museum_id
WHERE w.work_id IS NULL;
```

#### 3️. How many paintings have an asking price higher than their regular price?
```sql
SELECT COUNT(*)
FROM product_size
WHERE sale_price > regular_price;
```

#### 4️. Identify the paintings whose asking price is less than 50% of their regular price
```sql
WITH cte AS (
    SELECT w.name,
           p.sale_price,
           p.regular_price
    FROM product_size p
    JOIN work w ON p.work_id = w.work_id
)
SELECT *
FROM cte
WHERE sale_price < (regular_price / 2);
```

#### 5️. Which canvas size costs the most?
```sql
SELECT cs.label,
       p.regular_price
FROM canvas_size cs
JOIN product_size p ON cs.size_id = p.size_id
ORDER BY p.regular_price DESC
LIMIT 10;
```

#### 6️. Delete duplicate records from tables
- Work Table (check before deleting)
```sql
SELECT *
FROM (
    SELECT work_id,
           name,
           ROW_NUMBER() OVER (PARTITION BY name ORDER BY work_id) AS rn
    FROM work
) t
WHERE t.rn > 1;
```

- Delete duplicates from work
```sql
WITH duplicate_rows AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY name ORDER BY work_id) AS rn
    FROM work
)
DELETE FROM work
WHERE work_id IN (SELECT work_id FROM duplicate_rows WHERE rn > 1);
```

Product_Size Table
WITH duplicate_rows AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY work_id ORDER BY size_id) AS rn
    FROM product_size
)
DELETE FROM product_size
WHERE work_id IN (SELECT work_id FROM duplicate_rows WHERE rn > 1);

#### 7️. Identify museums with invalid city information
```sql
SELECT museum_id, name, city, country
FROM museum
WHERE city IS NULL
   OR city = ''
   OR city REGEXP '^[0-9]+$';
```

#### 8️. Fix invalid entries in Museum_Hours
- Find duplicate/invalid entries
```sql
SELECT museum_id, day, open, close, COUNT(*) AS cnt
FROM museum_hours
GROUP BY museum_id, day, open, close
HAVING COUNT(*) > 1;
```

- Fix misspelling
```sql
SET SQL_SAFE_UPDATES = 0;

UPDATE museum_hours
SET day = 'Thursday'
WHERE day = 'Thusday';

SET SQL_SAFE_UPDATES = 1;
```

#### 9️. Fetch the top 10 most famous painting subjects
```sql
SELECT s.subject,
       COUNT(*) AS subject_count
FROM work w
JOIN subject s ON w.work_id = s.work_id
JOIN museum m ON w.museum_id = m.museum_id
GROUP BY s.subject
ORDER BY subject_count DESC
LIMIT 10;
```

#### 10. Museums open on both Sunday and Monday
```sql
Using CTE
WITH cte1 AS (
    SELECT * FROM museum_hours WHERE day = 'Sunday'
),
cte2 AS (
    SELECT * FROM museum_hours WHERE day = 'Monday'
)
SELECT m.museum_id, m.name, m.city, m.country
FROM museum m
JOIN cte1 c1 ON m.museum_id = c1.museum_id
JOIN cte2 c2 ON m.museum_id = c2.museum_id;
```

- Direct Join
```sql
SELECT m.museum_id, m.name, m.city, m.country
FROM museum m
JOIN museum_hours h1 ON m.museum_id = h1.museum_id AND h1.day = 'Sunday'
JOIN museum_hours h2 ON m.museum_id = h2.museum_id AND h2.day = 'Monday';
```

#### 1️1️. How many museums are open every single day?
```sql
SELECT m.name,
       m.city,
       COUNT(DISTINCT mh.day) AS opening_day_total
FROM museum m
JOIN museum_hours mh ON m.museum_id = mh.museum_id
GROUP BY m.name, m.city
HAVING COUNT(DISTINCT mh.day) = 7;
```

#### 1️2️. Top 5 most popular museums (by number of paintings)
```sql
SELECT m.name,
       COUNT(DISTINCT w.name) AS painting_collection
FROM museum m
LEFT JOIN work w ON m.museum_id = w.museum_id
GROUP BY m.name
ORDER BY painting_collection DESC
LIMIT 5;
```

#### 1️3️. Top 5 most popular artists (by number of paintings)
```sql
SELECT a.full_name,
       COUNT(DISTINCT w.name) AS total_paintings
FROM artist a
LEFT JOIN work w ON a.artist_id = w.artist_id
GROUP BY a.full_name
ORDER BY total_paintings DESC
LIMIT 5;
```

#### 1️4️. Display the 3 least popular canvas sizes
```sql
WITH cte AS (
    SELECT cs.size_id,
           cs.label,
           COUNT(ps.size_id) AS total_count
    FROM canvas_size cs
    LEFT JOIN product_size ps ON cs.size_id = ps.size_id
    GROUP BY cs.size_id, cs.label
),
cte2 AS (
    SELECT *,
           DENSE_RANK() OVER (ORDER BY total_count) AS rnk
    FROM cte
)
SELECT size_id, label, total_count
FROM cte2
WHERE rnk <= 3;
```

#### 1️5️. Museum open for the longest duration in a day
```sql
WITH museum_open_hours AS (
    SELECT m.name,
           m.state,
           mh.day,
           TIMESTAMPDIFF(
               HOUR,
               STR_TO_DATE(mh.open, '%h:%i %p'),
               STR_TO_DATE(mh.close, '%h:%i %p')
           ) AS hours_open
    FROM museum m
    JOIN museum_hours mh ON m.museum_id = mh.museum_id
)
SELECT *
FROM museum_open_hours
WHERE hours_open = (SELECT MAX(hours_open) FROM museum_open_hours);
```

#### 1️6️. Museum with the most number of painting styles
```sql
SELECT m.name,
       COUNT(DISTINCT w.style) AS painting_styles
FROM museum m
LEFT JOIN work w ON m.museum_id = w.museum_id
GROUP BY m.name
ORDER BY painting_styles DESC
LIMIT 5;
```

#### 1️7️. Artists whose paintings are displayed in multiple countries
```sql
SELECT a.full_name,
       w.name,
       COUNT(DISTINCT m.country) AS country_count
FROM work w
JOIN artist a ON w.artist_id = a.artist_id
JOIN museum m ON w.museum_id = m.museum_id
GROUP BY a.full_name, w.name
HAVING COUNT(DISTINCT m.country) > 1;
```

#### 1️8️. Country and city with most museums
```sql
WITH cte AS (
    SELECT country, city, COUNT(*) AS museum_count
    FROM museum
    GROUP BY country, city
),
cte2 AS (
    SELECT *,
           DENSE_RANK() OVER (PARTITION BY country ORDER BY museum_count DESC) AS rnk
    FROM cte
)
SELECT country, city, museum_count
FROM cte2
WHERE rnk = 1;
```

#### 1️9️. Most and least expensive painting
```sql
WITH price_extremes AS (
    SELECT MAX(sale_price) AS max_price,
           MIN(sale_price) AS min_price
    FROM product_size
)
SELECT a.full_name AS artist_name,
       p.sale_price,
       w.name AS painting_name,
       m.name AS museum_name,
       m.city AS museum_city,
       cs.label AS canvas_label
FROM work w
JOIN product_size p ON w.work_id = p.work_id
JOIN museum m ON w.museum_id = m.museum_id
JOIN canvas_size cs ON p.size_id = cs.size_id
JOIN artist a ON w.artist_id = a.artist_id
JOIN price_extremes pe
  ON p.sale_price = pe.max_price OR p.sale_price = pe.min_price;
```

#### 2️0️. Country with the 5th highest number of paintings
```sql
WITH cte AS (
    SELECT m.country,
           COUNT(w.name) AS total_paintings
    FROM museum m
    JOIN work w ON m.museum_id = w.museum_id
    GROUP BY m.country
),
cte2 AS (
    SELECT *,
           DENSE_RANK() OVER (ORDER BY total_paintings DESC) AS rnk
    FROM cte
)
SELECT country, total_paintings
FROM cte2
WHERE rnk = 5;
```

#### 2️1️. Three most popular & least popular painting styles
```sql
WITH style_counts AS (
    SELECT w.style, COUNT(*) AS styles_count
    FROM work w
    WHERE w.style IS NOT NULL
    GROUP BY w.style
)
-- Top 3 (Most Popular)
(SELECT style, styles_count, 'Most Popular' AS category
 FROM style_counts
 ORDER BY styles_count DESC
 LIMIT 3)

UNION ALL

-- Bottom 3 (Least Popular)
(SELECT style, styles_count, 'Least Popular' AS category
 FROM style_counts
 ORDER BY styles_count ASC
 LIMIT 3);
```

#### 2️2️. Artist with the most Portrait paintings outside USA
```sql
SELECT a.full_name,
       a.nationality,
       COUNT(*) AS total_paintings
FROM work w
JOIN artist a ON w.artist_id = a.artist_id
JOIN museum m ON w.museum_id = m.museum_id
JOIN subject s ON w.work_id = s.work_id
WHERE m.country <> 'USA'
  AND s.subject = 'Portraits'
GROUP BY a.full_name, a.nationality
ORDER BY total_paintings DESC
LIMIT 3;
```
