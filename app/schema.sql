-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS Shopping_Cart;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS Authentication;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE Shopping_Cart (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  shopper_id TEXT NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES Products (ProductID)
);

-- do we use this table?
CREATE TABLE order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  order_id INTEGER NOT NULL,
  user_id INTEGER,
  shopper_id TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE Authentication(
  userID TEXT PRIMARY KEY,
  hashed_password TEXT NOT NULL,
  sessionID TEXT
);