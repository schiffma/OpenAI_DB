# OpenAI_DB

Python program using the OpenAI-API to create SQL-statements based on a context given.
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