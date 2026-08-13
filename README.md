Module 1 — Data Pipeline
📌 Overview

This module implements a complete data pipeline for collecting, cleaning, transforming, storing, and querying book data from Books to Scrape.

The pipeline follows:

Web Scraping
     ↓
Raw Book Data
     ↓
Data Cleaning & Transformation
     ↓
SQLite Database
     ↓
SQL Queries
     ↓
Analysis / Output


Module Objectives
Scrape book information from the website.
Collect books from multiple categories/pages.
Clean and standardize the scraped data.
Store the cleaned data in a normalized SQLite database.
Query the database using SQL.
Demonstrate the results using SQL and/or pandas.
Keep the entire process reproducible.
📁 Directory Structure
project-root/
│
├── data_pipeline/
│   ├── README.md
│   ├── scrape_books.py
│   ├── clean_data.py
│   ├── create_database.py
│   ├── queries.sql
│   ├── bookstore.db
│   └── output/
│       ├── books_clean.csv
│       └── query_results.csv
│
├── analytics/
│   └── ...
│
├── support_assistant/
│   └── ...
│
└── README.md

If the pipeline is implemented in one notebook instead of multiple scripts, replace the Python scripts above with the notebook name, for example data_pipeline.ipynb.

🛠️ Technologies Used
Technology	Purpose
Python	Pipeline implementation
Requests	Download web pages
BeautifulSoup	HTML parsing
Pandas	Data cleaning and analysis
SQLite	Relational database
SQL	Data querying
Jupyter Notebook	Optional interactive execution
⚙️ Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
2. Create a virtual environment
Windows
python -m venv .venv
.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install requests beautifulsoup4 pandas

If a requirements.txt file is provided:

pip install -r requirements.txt
🚀 Running the Pipeline

Run the pipeline in the following order:

Step 1 — Scrape
python scrape_books.py

This collects book information from Books to Scrape.

Typical fields collected:

Book title
Price
Availability
Rating
Category
Product URL
Step 2 — Clean and Transform
python clean_data.py

The cleaning stage:

Removes unnecessary whitespace.
Standardizes text values.
Converts prices to numeric values.
Converts availability to a usable numeric representation.
Converts ratings to numeric values.
Removes duplicate records.
Handles missing or invalid values.
Produces a clean dataset for database loading.

Example cleaned data:

title	price	availability	rating	category
A Light in the Attic	51.77	22	3	Poetry
Tipping the Velvet	53.74	20	1	Historical Fiction
Step 3 — Create SQLite Database
python create_database.py

This creates:

bookstore.db

The database can be recreated from the provided script, so the database is not dependent on a particular machine.

🗄️ Database Design

The database uses a normalized relational structure.

Example schema:

┌──────────────────┐
│     Categories   │
├──────────────────┤
│ category_id PK   │
│ category_name    │
└────────┬─────────┘
         │
         │
         ▼
┌──────────────────┐
│      Books       │
├──────────────────┤
│ book_id PK       │
│ title            │
│ price            │
│ availability     │
│ rating           │
│ category_id FK   │
│ product_url      │
└──────────────────┘
Books

Stores information about each scraped book.

Categories

Stores unique book categories.

Relationship
Categories 1 ─────────── * Books

One category can contain many books.

🔍 SQL Queries

The executed SQL queries are stored in:

queries.sql
Query 1 — View all books
SELECT *
FROM Books
LIMIT 10;

Output

book_id | title                  | price | availability | rating
----------------------------------------------------------------
1       | A Light in the Attic  | 51.77 | 22           | 3
2       | Tipping the Velvet    | 53.74 | 20           | 1
...

Query 2 — Find books above a specific price
SELECT title, price
FROM Books
WHERE price > 40
ORDER BY price DESC;
Purpose

Identifies relatively expensive books in the dataset.

Query 3 — Count books by category
SELECT
    c.category_name,
    COUNT(b.book_id) AS book_count
FROM Categories c
JOIN Books b
    ON c.category_id = b.category_id
GROUP BY c.category_name
ORDER BY book_count DESC;
Purpose

Demonstrates:

JOIN
GROUP BY
COUNT
ORDER BY
Query 4 — Average book price
SELECT
    AVG(price) AS average_price
FROM Books;
Purpose

Calculates the average price of books in the database.

Query 5 — Highest-rated books
SELECT title, rating
FROM Books
WHERE rating = 5
ORDER BY title;
Purpose

Finds books with the highest available rating.

🐼 SQL ↔ Pandas

The pipeline also demonstrates the relationship between SQL and pandas operations.

SQL	Pandas
SELECT	df[...]
WHERE	df[df["column"] ...]
GROUP BY	df.groupby()
COUNT()	.count() / .size()
AVG()	.mean()
ORDER BY	.sort_values()
JOIN	pd.merge()

Example:

df.groupby("category")["price"].mean()

is conceptually similar to:

SELECT category, AVG(price)
FROM Books
GROUP BY category;
🧹 Data Cleaning Decisions

The following cleaning decisions were made before loading the data into SQLite:

1. Duplicate records

Duplicate books are removed using an appropriate unique identifier such as the product URL/title.

2. Price

Prices are converted from scraped text into numeric values.

Example:

£51.77 → 51.77
3. Availability

Availability text is converted into a numeric stock count where possible.

Example:

"In stock (22 available)" → 22
4. Rating

Rating text is converted into an integer from 1–5.

5. Text fields

Leading/trailing whitespace is removed and text values are standardized.

6. Missing values

Missing or invalid values are inspected and handled before database insertion.

🧠 Design Decisions
Why Requests + BeautifulSoup?

requests is used to retrieve HTML pages and BeautifulSoup is used to parse the HTML structure.

This keeps the scraper simple and lightweight because the target website provides the required book information directly in the HTML.

Why SQLite?

SQLite was selected because:

It requires no separate database server.
It is easy to reproduce locally.
It supports standard SQL.
It works well for a small educational dataset.
The database can be stored directly in the repository.
Why normalize categories?

Categories are stored separately instead of repeating the category name for every book.

This reduces unnecessary duplication and demonstrates relational database design.

Why keep the recreation script?

The database can be recreated from the source data and scripts.

This makes the project reproducible even if the .db file is removed.

🔁 Reproducibility

To reproduce the complete pipeline:

python scrape_books.py
python clean_data.py
python create_database.py

Then inspect the database:

sqlite3 bookstore.db

Run:

SELECT name
FROM sqlite_master
WHERE type = 'table';
✅ Pipeline Checklist

Web scraping implemented

Multiple pages/categories handled

Data cleaned

Data transformed

SQLite database created

Relational schema implemented

SQL queries included

Query outputs documented

pandas/SQL workflow demonstrated

Installation instructions provided

Run instructions provided

Design decisions documented

Database recreation supported

📌 Expected Deliverables

The /data_pipeline directory should contain:

data_pipeline/
│
├── README.md
├── scrape_books.py          # Scraping code
├── clean_data.py            # Cleaning/transformation
├── create_database.py       # SQLite creation/loading
├── queries.sql              # Executed SQL queries
├── bookstore.db             # SQLite database
│
└── output/
    ├── books_clean.csv
    └── query_results.csv

If using a single notebook:

data_pipeline/
├── README.md
├── data_pipeline.ipynb
├── bookstore.db
├── queries.sql
└── output/
🎯 Module Outcome

This module demonstrates an end-to-end data engineering workflow:

Scrape → Clean → Transform → Store → Query → Analyze

The implementation is designed to be reproducible, structured, and easy to run locally as part of the complete project repository.
