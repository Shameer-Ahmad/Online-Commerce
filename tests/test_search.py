import pytest
from app.db import get_db

def test_search_results(client, app):
    # First, we need to create the test database structure
    with app.app_context():
        db = get_db()
        
        # Create a view or table similar to 'Alphabetical list of products'
        try:
            db.execute("""
                CREATE TABLE IF NOT EXISTS "Alphabetical list of products" (
                    ProductID INTEGER PRIMARY KEY,
                    ProductName TEXT,
                    CategoryID INTEGER,
                    CategoryName TEXT,
                    UnitPrice REAL
                )
            """)
            
            # Add some test data to this table
            db.execute("""
                INSERT INTO "Alphabetical list of products" 
                (ProductID, ProductName, CategoryID, CategoryName, UnitPrice) 
                VALUES (9998, "Unique Test Product", 1, "Test Category", 10.99)
            """)
            db.commit()
        except Exception as e:
            print(f"Database setup error: {e}")
    
    # Test search with no query
    response = client.get("/search/results")
    assert response.status_code == 200
    
    # Test search with a query that should return results
    response = client.get("/search/results?q=Unique+Test")
    assert response.status_code == 200
    
    # Test search with a query that should return no results
    response = client.get("/search/results?q=NonexistentProduct12345")
    assert response.status_code == 200