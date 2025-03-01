import os
import tempfile
import pytest
from app import create_app
from app.db import get_db, init_db

@pytest.fixture
def app():
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app with test settings
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    
    # Create the database and load test data
    with app.app_context():
        # Initialize database structure
        db = get_db()
        
        # Create necessary tables manually instead of using schema.sql
        # Create user table
        db.execute(
            "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)"
        )
        
        # Create Products table to match Northwind structure
        db.execute(
            "CREATE TABLE IF NOT EXISTS Products (ProductID INTEGER PRIMARY KEY, ProductName TEXT, CategoryID INTEGER, UnitPrice REAL, UnitsInStock INTEGER)"
        )
        
        # Create cart table
        db.execute(
            """CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shopper_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        
        # Create Categories table
        db.execute(
            "CREATE TABLE IF NOT EXISTS Categories (CategoryID INTEGER PRIMARY KEY, CategoryName TEXT)"
        )
        
        # Create the 'Alphabetical list of products' table needed by categories.py and search.py
        db.execute("""
            CREATE TABLE IF NOT EXISTS "Alphabetical list of products" (
                ProductID INTEGER PRIMARY KEY,
                ProductName TEXT,
                CategoryID INTEGER,
                CategoryName TEXT,
                UnitPrice REAL,
                UnitsInStock INTEGER,
                Discontinued INTEGER
            )
        """)
        
        # Add test data
        # Add a test user
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            ("test_user", "pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f")
        )
        
        # Add test product
        db.execute(
            "INSERT INTO Products (ProductID, ProductName, CategoryID, UnitPrice, UnitsInStock) VALUES (?, ?, ?, ?, ?)",
            (9999, "Test Product", 1, 10.99, 50)
        )
        
        # Add test category
        db.execute(
            "INSERT INTO Categories (CategoryID, CategoryName) VALUES (?, ?)",
            (1, "Test Category")
        )
        
        # Add a product to the Alphabetical list of products
        db.execute("""
            INSERT INTO "Alphabetical list of products" 
            (ProductID, ProductName, CategoryID, CategoryName, UnitPrice, UnitsInStock, Discontinued) 
            VALUES (9999, "Test Category Product", 1, "Test Category", 10.99, 50, 0)
        """)
        
        db.commit()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)

class AuthActions:
    def __init__(self, client):
        self._client = client
    
    def login(self, username="test_user", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )
    
    def logout(self):
        return self._client.get("/auth/logout")