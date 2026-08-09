Module 1 Data Pipeline
pip install requests beautifulsoup4 pandas lxml
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

BASE_URL = "https://books.toscrape.com/"

categories = [
    "Travel",
    "Mystery",
    "Historical Fiction"
]

rating_map = {
    "One":1,
    "Two":2,
    "Three":3,
    "Four":4,
    "Five":5
}

GBP_TO_INR = 105.50

books = []

home = requests.get(BASE_URL)
soup = BeautifulSoup(home.text,"html.parser")

category_links = {}

sidebar = soup.find("ul",class_="nav-list").find("ul")

for item in sidebar.find_all("li"):
    name = item.text.strip()
    link = BASE_URL + item.a["href"]
    category_links[name] = link


for category in categories:

    url = category_links[category]

    while True:

        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")

        articles = soup.find_all("article",class_="product_pod")

        for book in articles:

            title = book.h3.a["title"]

            price = book.find("p",class_="price_color").text

            rating_text = book.p["class"][1]

            availability = book.find("p",class_="instock availability").text.strip()

            books.append([
                title,
                price,
                rating_text,
                availability,
                category
            ])

        next_btn = soup.find("li",class_="next")

        if next_btn:

            next_page = next_btn.a["href"]
            url = url.replace("index.html",next_page)

        else:
            break

df = pd.DataFrame(
    books,
    columns=[
        "title",
        "price",
        "star_rating",
        "availability",
        "category"
    ]
)

print(df.head())
print("Books:",len(df))
df["price_gbp"] = (
    df["price"]
    .replace("£","",regex=True)
    .astype(float)
)

df["rating"] = df["star_rating"].map(rating_map)

median_rating = int(df["rating"].median())

df["rating"] = df["rating"].fillna(median_rating)

df["in_stock"] = df["availability"].str.contains("In stock")

df["price_inr"] = df["price_gbp"] * GBP_TO_INR

df = df.drop(columns=["price","star_rating","availability"])
df.to_csv("books.csv",index=False)
conn = sqlite3.connect("books.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(
category_id INTEGER PRIMARY KEY AUTOINCREMENT,
category_name TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
price_gbp REAL,
price_inr REAL,
rating INTEGER,
in_stock INTEGER,
category_id INTEGER,
FOREIGN KEY(category_id)
REFERENCES categories(category_id)
)
""")
for cat in df["category"].unique():

    cursor.execute(
        "INSERT OR IGNORE INTO categories(category_name) VALUES(?)",
        (cat,)
    )

conn.commit()
cat_df = pd.read_sql("SELECT * FROM categories",conn)

merged = df.merge(
    cat_df,
    left_on="category",
    right_on="category_name"
)

for _,row in merged.iterrows():

    cursor.execute("""
    INSERT INTO books(
    title,
    price_gbp,
    price_inr,
    rating,
    in_stock,
    category_id
    )
    VALUES(?,?,?,?,?,?)
    """,
    (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        int(row["rating"]),
        int(row["in_stock"]),
        int(row["category_id"])
    ))

conn.commit()
SELECT title,price_gbp
FROM books
WHERE rating=5;
SELECT title,price_gbp
FROM books
ORDER BY price_gbp DESC;
SELECT *
FROM books
LIMIT 10;
SELECT DISTINCT rating
FROM books;
SELECT title,price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 40;
SELECT
b.title,
c.category_name,
b.rating,
b.price_gbp
FROM books b
JOIN categories c
ON b.category_id=c.category_id
ORDER BY b.rating DESC
LIMIT 10;
queries = {

"Query1":
"""
SELECT title,price_gbp
FROM books
WHERE rating=5
""",

"Query2":
"""
SELECT title,price_gbp
FROM books
ORDER BY price_gbp DESC
""",

"Query3":
"""
SELECT *
FROM books
LIMIT 10
""",

"Query4":
"""
SELECT DISTINCT rating
FROM books
""",

"Query5":
"""
SELECT title,price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 40
""",

"Join":
"""
SELECT
b.title,
c.category_name,
b.rating,
b.price_gbp
FROM books b
JOIN categories c
ON b.category_id=c.category_id
ORDER BY b.rating DESC
LIMIT 10
"""
}

for name,q in queries.items():

    print("\n",name)

    print(pd.read_sql(q,conn))
    df1 = pd.read_sql(
"""
SELECT *
FROM books
WHERE rating=5
""",
conn
)

df2 = pd.read_sql(
"""
SELECT
b.title,
c.category_name,
b.rating
FROM books b
JOIN categories c
ON b.category_id=c.category_id
""",
conn
)

print(df1.head())

print(df2.head())
books_df = pd.read_sql("SELECT * FROM books",conn)

categories_df = pd.read_sql("SELECT * FROM categories",conn)

merge_df = books_df.merge(
    categories_df,
    on="category_id"
)

print(merge_df[
    ["title","category_name","rating"]
].head())
