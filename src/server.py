import os
import asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env file
load_dotenv()

# --- Firebase Initialization ---
try:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized with credentials from FIREBASE_CREDENTIALS_PATH")
    else:
        # Falls back to GOOGLE_APPLICATION_CREDENTIALS or default compute service account if cred_path is not defined
        firebase_admin.initialize_app()
        print("Firebase initialized with Application Default Credentials")
    
    db = firestore.client()
except Exception as e:
    print(f"Warning: Firebase initialization failed. Error: {e}")
    db = None

# Create an MCP server
port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Retail Tools Server", host="0.0.0.0", port=port)

# --- Tools ---

@mcp.tool()
def get_demand_forecast(product_id: str, days: int) -> Dict[str, Any]:
    """
    Get the demand forecast for a specific product over a given number of days.
    
    Args:
        product_id: The unique identifier for the product (e.g., 'P1001')
        days: Number of days to forecast into the future
    """
    base_demand = 50 # Default fallback
    if db:
        # Fetch pricing and base demand data from Firebase pricing collection
        doc_ref = db.collection("pricing").document(product_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            base_demand = data.get("base_demand", 50)
            
    forecast = []
    for day in range(1, days + 1):
        daily_demand = base_demand + (day * 2)
        forecast.append({"day": day, "expected_demand": daily_demand})
        
    return {
        "product_id": product_id,
        "forecast_period_days": days,
        "total_expected_demand": sum(f["expected_demand"] for f in forecast),
        "daily_breakdown": forecast
    }

@mcp.tool()
def calculate_elasticity(product_id: str, current_price: float, proposed_price: float) -> Dict[str, Any]:
    """
    Calculate the expected change in demand based on a proposed price change using the product's price elasticity.
    
    Args:
        product_id: The unique identifier for the product
        current_price: The current price of the product
        proposed_price: The proposed new price
    """
    elasticity_coefficient = -1.0 # Default fallback
    
    if db:
        doc_ref = db.collection("elasticity").document(product_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            elasticity_coefficient = data.get("coefficient", -1.0)
            
    price_change_percent = (proposed_price - current_price) / current_price
    expected_demand_change_percent = price_change_percent * elasticity_coefficient
    
    return {
        "product_id": product_id,
        "elasticity_coefficient": elasticity_coefficient,
        "price_change_percent": round(price_change_percent * 100, 2),
        "expected_demand_change_percent": round(expected_demand_change_percent * 100, 2),
        "recommendation": "Favorable" if (total_revenue_change := (1+expected_demand_change_percent)*(proposed_price/current_price)) > 1 else "Unfavorable"
    }

@mcp.tool()
def check_inventory(product_id: str, location_id: str = None) -> Dict[str, Any]:
    """
    Check the current inventory levels for a product.
    
    Args:
        product_id: The unique identifier for the product
        location_id: Optional location identifier (e.g. 'Store-A'). If None, checks all known locations.
    """
    if not db:
        return {"error": "Firebase database is not initialized properly."}
        
    doc_ref = db.collection("inventory").document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        return {"error": f"Product {product_id} not found in inventory system."}
        
    item = doc.to_dict()
    
    if location_id and item.get("location") != location_id:
        return {"error": f"Product {product_id} not found at location {location_id}."}
        
    quantity = item.get("quantity", 0)
    reorder_point = item.get("reorder_point", 0)
    
    status = "Healthy"
    if quantity <= 0:
        status = "Out of Stock"
    elif quantity <= reorder_point:
        status = "Needs Reorder"
        
    return {
        "product_id": product_id,
        "location": item.get("location", "Unknown"),
        "quantity_on_hand": quantity,
        "reorder_point": reorder_point,
        "status": status
    }

if __name__ == "__main__":
    # Initialize and run the server using Server-Sent Events (SSE) over HTTP
    # Cloud Run requires binding to 0.0.0.0 and listening to the $PORT env variable
    mcp.run(transport='sse')
