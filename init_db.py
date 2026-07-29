import sqlite3

def setup_database():
    # Connects to a local file database (creates it if missing)
    conn = sqlite3.connect("customer_service.db")
    cursor = conn.cursor()
    
    # Create the orders table schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            carrier TEXT NOT NULL,
            ship_date TEXT NOT NULL
        )
    """)
    
    # Seed mock enterprise tracking rows
    mock_orders = [
        ("ORD12345", "Delivered", "FedEx", "2026-07-25"),
        ("ORD67890", "Processing at fulfillment center", "UPS", "Pending"),
        ("ORD99999", "In Transit", "DHL", "2026-07-28")
    ]
    
    cursor.executemany("INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?)", mock_orders)
    conn.commit()
    conn.close()
    print("💾 Database initialized successfully as 'customer_service.db'!")

if __name__ == "__main__":
    setup_database()
