-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

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

create table products(
  id integer primary key AUTOINCREMENT,
  name text not null,
  price decimal(10,2) not null
);
create table cart (
  id integer primary key AUTOINCREMENT,
  shopper_id 
  created timestamp not null default current_timestamp,
  product_d text not null,
  quantity integer,
  foreign key (product_id) references products(id)
);
