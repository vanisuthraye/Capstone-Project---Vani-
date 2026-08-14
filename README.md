# Module 1 — Data Pipeline

## 📌 Overview

This module implements a complete data pipeline for collecting, cleaning, transforming, storing, and querying book data from **Books to Scrape**.

**Pipeline flow:**

```
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
```

## 🎯 Module Objectives

- Scrape book information from the website
- Collect books from multiple categories/pages
- Clean and standardize the scraped data
- Store the cleaned data in a normalized SQLite database
- Query the database using SQL
- Demonstrate results using SQL and/or pandas
- Keep the entire process reproducible

## 📁 Directory Structure

```
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
```

> **Note:** If the pipeline is implemented in one notebook instead of multiple scripts, replace the Python scripts above with the notebook name (e.g., `data_pipeline.ipynb`).

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| Requests | Download web pages |
| BeautifulSoup | HTML parsing |
| Pandas | Data cleaning and analysis |
| SQLite | Relational database |
| SQL | Data querying |
| Jupyter Notebook | Optional interactive execution |

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install requests beautifulsoup4 pandas
```

If a `requirements.txt` file is provided:

```bash
pip install -r requirements.txt
```

## 🚀 Running the Pipeline

Run the pipeline in the following order.

### Step 1 — Scrape

```bash
python scrape_books.py
```

Collects book information from Books to Scrape. Typical fields collected:

- Book title
- Price
- Availability
- Rating
- Category
- Product URL

### Step 2 — Clean and Transform

```bash
python clean_data.py
```

The cleaning stage:

- Removes unnecessary whitespace
- Standardizes text values
- Converts prices to numeric values
- Converts availability to a usable numeric representation
- Converts ratings to numeric values
- Removes duplicate records
- Handles missing or invalid values
- Produces a clean dataset for database loading

**Example cleaned data:**

| title | price | availability | rating | category |
|---|---|---|---|---|
| A Light in the Attic | 51.77 | 22 | 3 | Poetry |
| Tipping the Velvet | 53.74 | 20 | 1 | Historical Fiction |

### Step 3 — Create SQLite Database

```bash
python create_database.py
```

This creates `bookstore.db`. The database can be recreated from the provided script, so it is not dependent on a particular machine.

## 🗄️ Database Design

The database uses a normalized relational structure.

```
┌──────────────────┐
│    Categories    │
├──────────────────┤
│ category_id  PK  │
│ category_name    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│       Books       │
├──────────────────┤
│ book_id      PK  │
│ title            │
│ price            │
│ availability     │
│ rating           │
│ category_id  FK  │
│ product_url      │
└──────────────────┘
```

**Books** — Stores information about each scraped book.

**Categories** — Stores unique book categories.

**Relationship:** `Categories 1 ─── * Books` (one category can contain many books)

## 🔍 SQL Queries

All executed SQL queries are stored in `queries.sql`.

### Query 1 — View all books

```sql
SELECT *
FROM Books
LIMIT 10;
```

**Output**
```
book_id | title                  | price | availability | rating
----------------------------------------------------------------
1       | A Light in the Attic  | 51.77 | 22           | 3
2       | Tipping the Velvet    | 53.74 | 20           | 1
...
```

### Query 2 — Find books above a specific price

```sql
SELECT title, price
FROM Books
WHERE price > 40
ORDER BY price DESC;
```

**Purpose:** Identifies relatively expensive books in the dataset.

### Query 3 — Count books by category

```sql
SELECT
    c.category_name,
    COUNT(b.book_id) AS book_count
FROM Categories c
JOIN Books b
    ON c.category_id = b.category_id
GROUP BY c.category_name
ORDER BY book_count DESC;
```

**Purpose:** Demonstrates `JOIN`, `GROUP BY`, `COUNT`, and `ORDER BY`.

### Query 4 — Average book price

```sql
SELECT
    AVG(price) AS average_price
FROM Books;
```

**Purpose:** Calculates the average price of books in the database.

### Query 5 — Highest-rated books

```sql
SELECT title, rating
FROM Books
WHERE rating = 5
ORDER BY title;
```

**Purpose:** Finds books with the highest available rating.

## 🐼 SQL ↔ Pandas

The pipeline also demonstrates the relationship between SQL and pandas operations.

| SQL | Pandas |
|---|---|
| `SELECT` | `df[...]` |
| `WHERE` | `df[df["column"] ...]` |
| `GROUP BY` | `df.groupby()` |
| `COUNT()` | `.count()` / `.size()` |
| `AVG()` | `.mean()` |
| `ORDER BY` | `.sort_values()` |
| `JOIN` | `pd.merge()` |

**Example:**

```python
df.groupby("category")["price"].mean()
```

is conceptually similar to:

```sql
SELECT category, AVG(price)
FROM Books
GROUP BY category;
```

## 🧹 Data Cleaning Decisions

The following cleaning decisions were made before loading the data into SQLite:

1. **Duplicate records** — Removed using a unique identifier such as the product URL/title.
2. **Price** — Converted from scraped text into numeric values (e.g., `£51.77 → 51.77`).
3. **Availability** — Converted into a numeric stock count where possible (e.g., `"In stock (22 available)" → 22`).
4. **Rating** — Converted into an integer from 1–5.
5. **Text fields** — Leading/trailing whitespace removed; text values standardized.
6. **Missing values** — Inspected and handled before database insertion.

## 🧠 Design Decisions

**Why Requests + BeautifulSoup?**
`requests` retrieves HTML pages and `BeautifulSoup` parses the HTML structure. This keeps the scraper simple and lightweight, since the target website provides the required book information directly in the HTML.

**Why SQLite?**
- Requires no separate database server
- Easy to reproduce locally
- Supports standard SQL
- Works well for a small educational dataset
- The database can be stored directly in the repository

**Why normalize categories?**
Categories are stored separately instead of repeating the category name for every book. This reduces unnecessary duplication and demonstrates relational database design.

**Why keep the recreation script?**
The database can be recreated from the source data and scripts, making the project reproducible even if the `.db` file is removed.

## 🔁 Reproducibility

To reproduce the complete pipeline:

```bash
python scrape_books.py
python clean_data.py
python create_database.py
```

Then inspect the database:

```bash
sqlite3 bookstore.db
```

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table';
```

## ✅ Pipeline Checklist

- [x] Web scraping implemented
- [x] Multiple pages/categories handled
- [x] Data cleaned
- [x] Data transformed
- [x] SQLite database created
- [x] Relational schema implemented
- [x] SQL queries included
- [x] Query outputs documented
- [x] pandas/SQL workflow demonstrated
- [x] Installation instructions provided
- [x] Run instructions provided
- [x] Design decisions documented
- [x] Database recreation supported

## 📌 Expected Deliverables

The `/data_pipeline` directory should contain:

```
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
```

If using a single notebook:

```
data_pipeline/
├── README.md
├── data_pipeline.ipynb
├── bookstore.db
├── queries.sql
└── output/
```

## 🎯 Module Outcome

This module demonstrates an end-to-end data engineering workflow — from web scraping, through cleaning and transformation, to structured storage and SQL-based analysis.
