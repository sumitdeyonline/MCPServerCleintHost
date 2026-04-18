import os
import csv
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

def initialize_firebase():
    """Initialize Firebase with the appropriate credentials."""
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase authenticated successfully with service account key.")
    else:
        # Fallback for Application Default Credentials
        firebase_admin.initialize_app()
        print("Firebase authenticated using Application Default Credentials.")
    
    return firestore.client()

def seed_database():
    print("Connecting to Firestore...")
    db = initialize_firebase()
    
    if not db:
        print("Could not connect to database. Aborting.")
        return

    # 1. Insert Inventory Data
    if os.path.exists("data/inventory.csv"):
        print("\n--- Inserting Inventory Data ---")
        with open("data/inventory.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row["product_id"]
                data = {
                    "location": row["location"],
                    "quantity": int(row["quantity"]),
                    "reorder_point": int(row["reorder_point"])
                }
                db.collection("inventory").document(product_id).set(data)
                print(f"Inserted inventory for {product_id}")
    else:
        print("\nMissing inventory.csv. Skipping...")

    # 2. Insert Elasticity Data
    if os.path.exists("data/elasticity.csv"):
        print("\n--- Inserting Elasticity Data ---")
        with open("data/elasticity.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row["product_id"]
                data = {
                    "coefficient": float(row["coefficient"])
                }
                db.collection("elasticity").document(product_id).set(data)
                print(f"Inserted elasticity for {product_id}")
    else:
        print("\nMissing elasticity.csv. Skipping...")

    # 3. Insert Pricing/Demand Data
    if os.path.exists("data/pricing.csv"):
        print("\n--- Inserting Pricing Data ---")
        with open("data/pricing.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row["product_id"]
                data = {
                    "base_demand": int(row["base_demand"])
                }
                db.collection("pricing").document(product_id).set(data)
                print(f"Inserted pricing for {product_id}")
    else:
        print("\nMissing pricing.csv. Skipping...")

    print("\n✅ Database seeding from CSV complete!")

if __name__ == "__main__":
    seed_database()
