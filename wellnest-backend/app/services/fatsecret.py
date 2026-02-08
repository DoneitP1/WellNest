"""
FatSecret API Integration for Food Search

Provides food search functionality with nutritional information.
"""

import httpx
import hashlib
import hmac
import base64
import time
import urllib.parse
import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class FoodSearchResult:
    """Represents a food item from FatSecret search."""
    food_id: str
    food_name: str
    brand_name: Optional[str]
    food_type: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: str
    serving_description: str


class FatSecretClient:
    """
    FatSecret API Client using OAuth 2.0
    
    Register for API keys at: https://platform.fatsecret.com/api/
    """

    BASE_URL = "https://platform.fatsecret.com/rest/server.api"
    TOKEN_URL = "https://oauth.fatsecret.com/connect/token"

    def __init__(self):
        self.consumer_key = os.getenv("FATSECRET_CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("FATSECRET_CONSUMER_SECRET", "")
        self._access_token = None
        self._token_expires_at = 0

    def _get_access_token(self) -> Optional[str]:
        """Get or refresh OAuth 2.0 access token."""
        if not self.consumer_key or not self.consumer_secret:
            return None

        # Return existing token if valid (with 60s buffer)
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        try:
            # Basic Auth header for token request
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            auth_header = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials",
                "scope": "basic"
            }
            
            with httpx.Client() as client:
                response = client.post(self.TOKEN_URL, headers=headers, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    self._access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 86400)
                    self._token_expires_at = time.time() + expires_in
                    return self._access_token
                else:
                    print(f"Failed to get access token: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    def _make_request(self, method_name: str, extra_params: dict = None) -> dict:
        """Make authenticated request to FatSecret API."""
        if not self.consumer_key or not self.consumer_secret:
            # Return mock data if no API keys
            return self._get_mock_response(method_name, extra_params)

        token = self._get_access_token()
        if not token:
            print("No access token available, falling back to mock data")
            return self._get_mock_response(method_name, extra_params)

        params = {
            "method": method_name,
            "format": "json",
        }

        if extra_params:
            params.update(extra_params)

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Make request
        with httpx.Client() as client:
            response = client.get(self.BASE_URL, params=params, headers=headers)
            try:
                if response.status_code == 200:
                    result = response.json()
                    # Check for API errors (like IP restriction)
                    if "error" in result:
                        print(f"FatSecret API error: {result['error']}")
                        return self._get_mock_response(method_name, extra_params)
                    return result
                else:
                    print(f"FatSecret API status {response.status_code}: {response.text}")
                    return self._get_mock_response(method_name, extra_params)
            except Exception as e:
                print(f"FatSecret API exception: {e}")
                return self._get_mock_response(method_name, extra_params)

    def _get_mock_response(self, method_name: str, extra_params: dict = None) -> dict:
        """Return mock data for development without API keys."""
        search_query = extra_params.get("search_expression", "").lower() if extra_params else ""

        # Common foods database for mock responses
        mock_foods = {
            "banana": {
                "food_id": "1001",
                "food_name": "Banana",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 medium (118g)",
                    "metric_serving_amount": "118",
                    "metric_serving_unit": "g",
                    "calories": "105",
                    "protein": "1.3",
                    "carbohydrate": "27",
                    "fat": "0.4",
                    "fiber": "3.1"
                }}
            },
            "apple": {
                "food_id": "1002",
                "food_name": "Apple",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 medium (182g)",
                    "metric_serving_amount": "182",
                    "metric_serving_unit": "g",
                    "calories": "95",
                    "protein": "0.5",
                    "carbohydrate": "25",
                    "fat": "0.3",
                    "fiber": "4.4"
                }}
            },
            "chicken": {
                "food_id": "1003",
                "food_name": "Chicken Breast (Grilled)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "100g",
                    "metric_serving_amount": "100",
                    "metric_serving_unit": "g",
                    "calories": "165",
                    "protein": "31",
                    "carbohydrate": "0",
                    "fat": "3.6",
                    "fiber": "0"
                }}
            },
            "rice": {
                "food_id": "1004",
                "food_name": "White Rice (Cooked)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (158g)",
                    "metric_serving_amount": "158",
                    "metric_serving_unit": "g",
                    "calories": "206",
                    "protein": "4.3",
                    "carbohydrate": "45",
                    "fat": "0.4",
                    "fiber": "0.6"
                }}
            },
            "egg": {
                "food_id": "1005",
                "food_name": "Egg (Boiled)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 large (50g)",
                    "metric_serving_amount": "50",
                    "metric_serving_unit": "g",
                    "calories": "78",
                    "protein": "6.3",
                    "carbohydrate": "0.6",
                    "fat": "5.3",
                    "fiber": "0"
                }}
            },
            "bread": {
                "food_id": "1006",
                "food_name": "White Bread",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 slice (25g)",
                    "metric_serving_amount": "25",
                    "metric_serving_unit": "g",
                    "calories": "66",
                    "protein": "2.1",
                    "carbohydrate": "13",
                    "fat": "0.8",
                    "fiber": "0.6"
                }}
            },
            "milk": {
                "food_id": "1007",
                "food_name": "Whole Milk",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (244g)",
                    "metric_serving_amount": "244",
                    "metric_serving_unit": "g",
                    "calories": "149",
                    "protein": "8",
                    "carbohydrate": "12",
                    "fat": "8",
                    "fiber": "0"
                }}
            },
            "pasta": {
                "food_id": "1008",
                "food_name": "Spaghetti (Cooked)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (140g)",
                    "metric_serving_amount": "140",
                    "metric_serving_unit": "g",
                    "calories": "220",
                    "protein": "8.1",
                    "carbohydrate": "43",
                    "fat": "1.3",
                    "fiber": "2.5"
                }}
            },
            "salmon": {
                "food_id": "1009",
                "food_name": "Salmon (Grilled)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "100g",
                    "metric_serving_amount": "100",
                    "metric_serving_unit": "g",
                    "calories": "208",
                    "protein": "20",
                    "carbohydrate": "0",
                    "fat": "13",
                    "fiber": "0"
                }}
            },
            "avocado": {
                "food_id": "1010",
                "food_name": "Avocado",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1/2 avocado (68g)",
                    "metric_serving_amount": "68",
                    "metric_serving_unit": "g",
                    "calories": "114",
                    "protein": "1.4",
                    "carbohydrate": "6",
                    "fat": "10.5",
                    "fiber": "4.6"
                }}
            },
            "yogurt": {
                "food_id": "1011",
                "food_name": "Greek Yogurt",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (245g)",
                    "metric_serving_amount": "245",
                    "metric_serving_unit": "g",
                    "calories": "100",
                    "protein": "17",
                    "carbohydrate": "6",
                    "fat": "0.7",
                    "fiber": "0"
                }}
            },
            "oatmeal": {
                "food_id": "1012",
                "food_name": "Oatmeal (Cooked)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (234g)",
                    "metric_serving_amount": "234",
                    "metric_serving_unit": "g",
                    "calories": "158",
                    "protein": "6",
                    "carbohydrate": "27",
                    "fat": "3.2",
                    "fiber": "4"
                }}
            },
            "potato": {
                "food_id": "1013",
                "food_name": "Baked Potato",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 medium (173g)",
                    "metric_serving_amount": "173",
                    "metric_serving_unit": "g",
                    "calories": "161",
                    "protein": "4.3",
                    "carbohydrate": "37",
                    "fat": "0.2",
                    "fiber": "3.8"
                }}
            },
            "steak": {
                "food_id": "1014",
                "food_name": "Beef Steak (Grilled)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "100g",
                    "metric_serving_amount": "100",
                    "metric_serving_unit": "g",
                    "calories": "271",
                    "protein": "26",
                    "carbohydrate": "0",
                    "fat": "18",
                    "fiber": "0"
                }}
            },
            "coffee": {
                "food_id": "1015",
                "food_name": "Black Coffee",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 cup (240ml)",
                    "metric_serving_amount": "240",
                    "metric_serving_unit": "ml",
                    "calories": "2",
                    "protein": "0.3",
                    "carbohydrate": "0",
                    "fat": "0",
                    "fiber": "0"
                }}
            },
            "pizza": {
                "food_id": "1016",
                "food_name": "Pizza (Cheese)",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 slice (107g)",
                    "metric_serving_amount": "107",
                    "metric_serving_unit": "g",
                    "calories": "285",
                    "protein": "12.3",
                    "carbohydrate": "36",
                    "fat": "10.4",
                    "fiber": "2.5"
                }}
            },
            "burger": {
                "food_id": "1017",
                "food_name": "Hamburger",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 burger (215g)",
                    "metric_serving_amount": "215",
                    "metric_serving_unit": "g",
                    "calories": "540",
                    "protein": "25",
                    "carbohydrate": "40",
                    "fat": "31",
                    "fiber": "2"
                }}
            },
            "salad": {
                "food_id": "1018",
                "food_name": "Garden Salad",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 bowl (207g)",
                    "metric_serving_amount": "207",
                    "metric_serving_unit": "g",
                    "calories": "35",
                    "protein": "2.6",
                    "carbohydrate": "7",
                    "fat": "0.4",
                    "fiber": "2.8"
                }}
            },
            "orange": {
                "food_id": "1019",
                "food_name": "Orange",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 medium (131g)",
                    "metric_serving_amount": "131",
                    "metric_serving_unit": "g",
                    "calories": "62",
                    "protein": "1.2",
                    "carbohydrate": "15",
                    "fat": "0.2",
                    "fiber": "3.1"
                }}
            },
            "cheese": {
                "food_id": "1020",
                "food_name": "Cheddar Cheese",
                "food_type": "Generic",
                "servings": {"serving": {
                    "serving_description": "1 slice (28g)",
                    "metric_serving_amount": "28",
                    "metric_serving_unit": "g",
                    "calories": "113",
                    "protein": "7",
                    "carbohydrate": "0.4",
                    "fat": "9.3",
                    "fiber": "0"
                }}
            }
        }

        # Find matching foods
        matching_foods = []
        for key, food in mock_foods.items():
            if search_query in key or search_query in food["food_name"].lower():
                matching_foods.append(food)

        # If no exact match, return first few foods as suggestions
        if not matching_foods and search_query:
            matching_foods = list(mock_foods.values())[:5]

        return {"foods": {"food": matching_foods}}

    def search_foods(self, query: str, max_results: int = 10) -> List[FoodSearchResult]:
        """
        Search for foods by name.

        Args:
            query: Search term
            max_results: Maximum number of results to return

        Returns:
            List of FoodSearchResult objects
        """
        response = self._make_request("foods.search", {
            "search_expression": query,
            "max_results": str(max_results)
        })

        results = []
        foods = response.get("foods", {}).get("food", [])

        # Handle single result (not in a list)
        if isinstance(foods, dict):
            foods = [foods]

        for food in foods:
            # Get first serving info
            servings = food.get("servings", {}).get("serving", {})
            if isinstance(servings, list):
                serving = servings[0] if servings else {}
            else:
                serving = servings

            results.append(FoodSearchResult(
                food_id=food.get("food_id", ""),
                food_name=food.get("food_name", ""),
                brand_name=food.get("brand_name"),
                food_type=food.get("food_type", "Generic"),
                calories=float(serving.get("calories", 0)),
                protein=float(serving.get("protein", 0)),
                carbs=float(serving.get("carbohydrate", 0)),
                fat=float(serving.get("fat", 0)),
                fiber=float(serving.get("fiber", 0)),
                serving_size=f"{serving.get('metric_serving_amount', '')} {serving.get('metric_serving_unit', '')}".strip(),
                serving_description=serving.get("serving_description", "1 serving")
            ))

        return results[:max_results]

    def get_food_details(self, food_id: str) -> Optional[FoodSearchResult]:
        """
        Get detailed nutritional information for a specific food.

        Args:
            food_id: FatSecret food ID

        Returns:
            FoodSearchResult with detailed nutrition info
        """
        response = self._make_request("food.get.v2", {
            "food_id": food_id
        })

        food = response.get("food", {})
        if not food:
            return None

        # Get first serving info
        servings = food.get("servings", {}).get("serving", {})
        if isinstance(servings, list):
            serving = servings[0] if servings else {}
        else:
            serving = servings

        return FoodSearchResult(
            food_id=food.get("food_id", ""),
            food_name=food.get("food_name", ""),
            brand_name=food.get("brand_name"),
            food_type=food.get("food_type", "Generic"),
            calories=float(serving.get("calories", 0)),
            protein=float(serving.get("protein", 0)),
            carbs=float(serving.get("carbohydrate", 0)),
            fat=float(serving.get("fat", 0)),
            fiber=float(serving.get("fiber", 0)),
            serving_size=f"{serving.get('metric_serving_amount', '')} {serving.get('metric_serving_unit', '')}".strip(),
            serving_description=serving.get("serving_description", "1 serving")
        )
