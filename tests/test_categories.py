import pytest
from app.db import get_db

def test_category_items(client, app):
    # Make sure our test category exists in the test database
    with app.app_context():
        db = get_db()
        try:
            # Check if category 1 exists, if not create it
            category = db.execute("SELECT * FROM Categories WHERE CategoryID = 1").fetchone()
            if not category:
                db.execute(
                    "INSERT INTO Categories (CategoryID, CategoryName) VALUES (?, ?)",
                    (1, "Test Category")
                )
                db.commit()
                
            # Create the 'Alphabetical list of products' table needed by categories.py
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
            
            # Add a test product
            db.execute("""
                INSERT INTO "Alphabetical list of products" 
                (ProductID, ProductName, CategoryID, UnitPrice, UnitsInStock, Discontinued) 
                VALUES (9999, "Test Category Product", 1, 10.99, 50, 0)
            """)
            db.commit()
        except Exception as e:
            print(f"Database setup error: {e}")
    
    # Test viewing a category
    response = client.get("/categories/1/")
    assert response.status_code == 200
    
    # Test viewing a category that doesn't exist
    response = client.get("/categories/999/")
    assert response.status_code == 404