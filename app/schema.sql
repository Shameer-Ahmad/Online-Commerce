-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS cart;

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
  shopper_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT current_timestamp,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  order_id INTEGER NOT NULL,
  user_id INTEGER,
  shopper_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
)

CREATE TABLE Authentication(
  userID TEXT PRIMARY KEY,
  hashed_password TEXT NOT NULL,
  sessionID TEXT
)