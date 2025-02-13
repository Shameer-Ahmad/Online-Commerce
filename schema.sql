-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS cart;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  NAME TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL
);

CREATE TABLE cart (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  shopper_id 
  created TIMESTAMP NOT NULL DEFAULT current_timestamp,
  product_id TEXT NOT NULL,
  quantity INTEGER,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
