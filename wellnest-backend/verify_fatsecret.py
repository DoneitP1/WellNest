import os
import sys
# Ensure app module can be found
sys.path.append(os.getcwd())

from dotenv import load_dotenv
from app.services.fatsecret import FatSecretClient

# Load env vars
load_dotenv()

def test_fatsecret_integration():
    client = FatSecretClient()
    
    print(f"Consumer Key present: {bool(client.consumer_key)}")
    print(f"Consumer Secret present: {bool(client.consumer_secret)}")
    
    try:
        print("\nSearching for 'apple'...")
        # Search for something that shouldn't be in the mock data to confirm real API
        results = client.search_foods("apple", max_results=1)
        
        if not results:
            print("No results found.")
            return
            
        first_result = results[0]
        print(f"Found: {first_result.food_name} (ID: {first_result.food_id})")
        print(f"Calories: {first_result.calories}")
        
        # Check if ID looks like mock data (mock IDs were 1001-1020)
        if first_result.food_id == "1002":
            print("\nWARNING: Returned MOCK data! Credentials might be invalid or not loaded.")
        else:
            print("\nSUCCESS: Returned REAL data! Integration is working.")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    test_fatsecret_integration()
