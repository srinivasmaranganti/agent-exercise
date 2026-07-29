import wikipedia
import sqlite3


def web_search(query: str) -> str:
    """Searches Wikipedia for a given query string and returns a summary."""
    try:
        # Limit sentences to keep the LLM context window concise
        return wikipedia.summary(query, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Ambiguous query. Options: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "No results found for this topic."

def check_order_status(order_id: str) -> str:
    """Retrieves live shipping and carrier data for a specific customer order ID from the database."""
    try:
        conn = sqlite3.connect("customer_service.db")
        cursor = conn.cursor()
        
        # Execute parameterized SQL query to safely avoid injection attacks
        cursor.execute("SELECT status, carrier, ship_date FROM orders WHERE UPPER(order_id) = ?", (order_id.upper(),))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            status, carrier, ship_date = result
            return f"Status: {status} | Carrier: {carrier} | Ship Date: {ship_date}"
            
        return f"Order ID '{order_id}' not found in the customer database."
        
    except sqlite3.Error as e:
        return f"Database query error: {str(e)}"

def get_refund_policy(item_category: str) -> str:
    """Returns the company refund policy rules for a specific category."""
    policies = {
        "electronics": "30-day return window. Must include original packaging. 15% restocking fee.",
        "clothing": "60-day return window. Tags must be attached. Free return shipping."
    }
    return policies.get(item_category.lower(), "Standard 30-day return policy applies to all other items.")

# Expose tools to the core agent ReAct loop
AVAILABLE_TOOLS = {
    "check_order_status": check_order_status,
    "get_refund_policy": get_refund_policy
}

