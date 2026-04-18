import csv
import random

NUM_PRODUCTS = 100
LOCATIONS = ["Store-A", "Store-B", "Warehouse-1", "Distribution-Center-West"]

def generate_inventory_csv(filename="inventory.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "location", "quantity", "reorder_point"])
        for i in range(1, NUM_PRODUCTS + 1):
            product_id = f"P{1000 + i}"
            location = random.choice(LOCATIONS)
            quantity = random.randint(0, 500)
            reorder_point = random.randint(20, 100)
            writer.writerow([product_id, location, quantity, reorder_point])

def generate_elasticity_csv(filename="elasticity.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "coefficient"])
        for i in range(1, NUM_PRODUCTS + 1):
            product_id = f"P{1000 + i}"
            # Elasticity coefficient usually between -0.1 and -3.0
            coefficient = round(random.uniform(-3.0, -0.1), 2)
            writer.writerow([product_id, coefficient])

def generate_pricing_csv(filename="pricing.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "base_demand"])
        for i in range(1, NUM_PRODUCTS + 1):
            product_id = f"P{1000 + i}"
            base_demand = random.randint(10, 500)
            writer.writerow([product_id, base_demand])

if __name__ == "__main__":
    generate_inventory_csv()
    generate_elasticity_csv()
    generate_pricing_csv()
    print("Generated inventory.csv, elasticity.csv, and pricing.csv with 100 sample products each.")
