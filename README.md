# OpenAI_DB

Python program using the OpenAI-API to create SQL-statements based on a context given and execute them on a default database.
The default use case is the public available [GWR](https://www.housing-stat.ch/de/madd/public.html) data set, a data set
about all entrances, buildings and dwellings according to official registration in Switzerland.

The script ``load_GWR_PLZ_from_csv_duckdb.py`` will download the data and convert the .csv-feeds to a fast relational 
DuckDB database [DuckDB database](https://duckdb.org/).

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   $ cd OpenAI_DB
   ```

4. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

5. Add your [API key](https://platform.openai.com/account/api-keys) to the newly created `.env` file.

6. Create the GWR-DuckDB database:

   ```bash
   $ python load_GWR_PLZ_from_csv_duckdb.py
   ```

7. Run the app:

   ```bash
   $ python openai_sql_duckdb.py
   ```
   
## Examples

The following examples consist of questions formulated in German and their answers/results as tabulated dataframes and the generated SQL-statements 
used to generate them.

```
Question: 10 orte mit dem höchsten hotelanteil prozentual?
prompt_tokens:  1237
total_tokens:  1458
>> Runtime of OpenAI: 12.88 second.

>> Total Runtime of eval_sql: 0.25 second.

ChatGPT[gwr_ch_bfs_duck.db]: 
+----+--------------------+--------------------+
|    | city               |   hotel_percentage |
|----+--------------------+--------------------|
|  0 | Serpiano           |           40       |
|  1 | Jungfraujoch       |           33.3333  |
|  2 | Bürgenstock        |           23.5955  |
|  3 | Kleine Scheidegg   |           19.2308  |
|  4 | Vulpera            |           15.873   |
|  5 | Alp Grüm           |           12.5     |
|  6 | Samnaun Dorf       |           12.2995  |
|  7 | Acquarossa         |           11.9048  |
|  8 | Sils/Segl Baselgia |           10.5263  |
|  9 | Zermatt            |            9.56194 |
+----+--------------------+--------------------+
WITH total_buildings AS (
    SELECT ENTRANCE.DPLZNAME AS city, COUNT(*) AS total
    FROM BUILDING
    JOIN ENTRANCE ON BUILDING.EGID = ENTRANCE.EGID
    GROUP BY ENTRANCE.DPLZNAME
),
hotel_buildings AS (
    SELECT ENTRANCE.DPLZNAME AS city, COUNT(*) AS hotels
    FROM BUILDING
    JOIN ENTRANCE ON BUILDING.EGID = ENTRANCE.EGID
    JOIN CODES ON BUILDING.GKLAS = CODES.CECODID
    WHERE CODES.CODTXTLD = 'Hotelgebäude' AND CODES.CMERKM = 'GKLAS'
    GROUP BY ENTRANCE.DPLZNAME
)
SELECT hotel_buildings.city, (hotel_buildings.hotels::decimal / total_buildings.total::decimal) * 100 AS hotel_percentage
FROM hotel_buildings
JOIN total_buildings ON hotel_buildings.city = total_buildings.city
ORDER BY hotel_percentage DESC
LIMIT 10;

> Total Runtime of open_ai_sql: 13.13 second.

Question: 5 kantone mit den durchschnittlich ältesten Gebäude?
prompt_tokens:  1258
total_tokens:  1360
>> Runtime of OpenAI: 7.79 second.

>> Total Runtime of eval_sql: 0.07 second.

ChatGPT[gwr_ch_bfs_duck.db]: 
+----+----------+--------------------+
|    | kanton   |   avg_building_age |
|----+----------+--------------------|
|  0 | FR       |            2004.34 |
|  1 | UR       |            1992.26 |
|  2 | GE       |            1988.27 |
|  3 | GL       |            1984.5  |
|  4 | SO       |            1982.31 |
+----+----------+--------------------+
WITH building_age AS (
    SELECT 
        BUILDING.GDEKT AS kanton,
        AVG(BUILDING.GBAUJ) AS avg_building_age
    FROM 
        BUILDING
    WHERE 
        BUILDING.GBAUJ IS NOT NULL
    GROUP BY 
        BUILDING.GDEKT
)

SELECT 
    building_age.kanton,
    building_age.avg_building_age
FROM 
    building_age
ORDER BY 
    building_age.avg_building_age DESC
LIMIT 5;

> Total Runtime of open_ai_sql: 7.87 second.

Question: das gleiche aber mit alter
prompt_tokens:  1268
total_tokens:  1370
>> Runtime of OpenAI: 6.81 second.

>> Total Runtime of eval_sql: 0.05 second.

ChatGPT[gwr_ch_bfs_duck.db]: 
+----+----------+-----------+
|    | kanton   |   avg_age |
|----+----------+-----------|
|  0 | BS       |   82.8977 |
|  1 | AI       |   79.9786 |
|  2 | OW       |   77.9963 |
|  3 | VD       |   71.401  |
|  4 | GR       |   67.9431 |
+----+----------+-----------+
WITH building_age AS (
    SELECT 
        BUILDING.GDEKT AS kanton,
        AVG(BUILDING.GBAUJ) AS avg_building_age
    FROM 
        BUILDING
    WHERE 
        BUILDING.GBAUJ IS NOT NULL
    GROUP BY 
        BUILDING.GDEKT
)
SELECT 
    kanton,
    2022 - avg_building_age AS avg_age
FROM 
    building_age
ORDER BY 
    avg_age DESC
LIMIT 5;

> Total Runtime of open_ai_sql: 6.86 second.

```