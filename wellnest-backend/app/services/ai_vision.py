"""
WellNest AI Vision Module

Uses Claude Vision API to analyze food images and estimate nutritional content.
"""

import base64
import json
import os
import re
from typing import Optional, List, TypedDict
from dataclasses import dataclass
from enum import Enum
import httpx


class AnalysisConfidence(str, Enum):
    HIGH = "high"        # > 0.8
    MEDIUM = "medium"    # 0.5 - 0.8
    LOW = "low"          # < 0.5


@dataclass
class FoodItem:
    """Represents a single food item detected in the image."""
    name: str
    name_tr: Optional[str]  # Turkish name
    estimated_portion: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    confidence: float


@dataclass
class FoodAnalysisResult:
    """Result of food image analysis."""
    success: bool
    food_items: List[FoodItem]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    meal_type_suggestion: str
    confidence_level: AnalysisConfidence
    raw_response: str
    error_message: Optional[str] = None


class FoodAnalyzer:
    """
    Analyzes food images using Claude Vision API.

    Usage:
        analyzer = FoodAnalyzer(api_key="your-anthropic-api-key")
        result = await analyzer.analyze_food_image(image_bytes)
    """

    SYSTEM_PROMPT = """You are a professional nutritionist AI assistant specialized in food recognition and nutritional analysis.

Your task is to analyze food images and provide accurate nutritional estimates.

IMPORTANT GUIDELINES:
1. Identify ALL food items visible in the image
2. Estimate portion sizes based on visual cues (plate size, utensils, common serving sizes)
3. Provide nutritional values per item AND totals
4. If you cannot identify a food item clearly, indicate low confidence
5. Consider cooking methods (fried, grilled, steamed) as they affect calorie content
6. Account for visible sauces, dressings, or toppings

OUTPUT FORMAT:
You MUST respond with a valid JSON object in the following format:
{
    "success": true/false,
    "food_items": [
        {
            "name": "Food name in English",
            "name_tr": "Turkish name (if known)",
            "estimated_portion": "Description (e.g., '1 cup', '150g', '1 medium slice')",
            "calories": integer,
            "protein": float (grams),
            "carbs": float (grams),
            "fat": float (grams),
            "fiber": float (grams),
            "confidence": float (0.0 to 1.0)
        }
    ],
    "total_calories": integer,
    "total_protein": float,
    "total_carbs": float,
    "total_fat": float,
    "total_fiber": float,
    "meal_type_suggestion": "breakfast/lunch/dinner/snack",
    "analysis_notes": "Any relevant notes about the analysis"
}

If the image doesn't contain food or is unclear:
{
    "success": false,
    "error_message": "Description of the issue",
    "food_items": [],
    "total_calories": 0,
    "total_protein": 0,
    "total_carbs": 0,
    "total_fat": 0,
    "total_fiber": 0,
    "meal_type_suggestion": "unknown",
    "analysis_notes": ""
}

Be conservative with estimates - it's better to slightly underestimate than overestimate portions."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FoodAnalyzer.

        Args:
            api_key: Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"

    async def analyze_food_image(
        self,
        image_data: bytes,
        image_type: str = "image/jpeg",
        additional_context: Optional[str] = None
    ) -> FoodAnalysisResult:
        """
        Analyze a food image and return nutritional estimates.

        Args:
            image_data: Raw image bytes
            image_type: MIME type of the image (image/jpeg, image/png, image/webp, image/gif)
            additional_context: Optional context (e.g., "This is my breakfast")

        Returns:
            FoodAnalysisResult with detected foods and nutritional information
        """
        # Encode image to base64
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

        # Build the user message
        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_type,
                    "data": image_base64,
                },
            },
            {
                "type": "text",
                "text": "Please analyze this food image and provide nutritional estimates.",
            },
        ]

        if additional_context:
            user_content[1]["text"] += f"\n\nAdditional context: {additional_context}"

        # Prepare the API request
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": self.SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

            result = response.json()
            raw_response = result["content"][0]["text"]

            # Parse the JSON response
            return self._parse_response(raw_response)

        except httpx.HTTPStatusError as e:
            return FoodAnalysisResult(
                success=False,
                food_items=[],
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fat=0,
                total_fiber=0,
                meal_type_suggestion="unknown",
                confidence_level=AnalysisConfidence.LOW,
                raw_response="",
                error_message=f"API error: {e.response.status_code} - {e.response.text}",
            )
        except Exception as e:
            return FoodAnalysisResult(
                success=False,
                food_items=[],
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fat=0,
                total_fiber=0,
                meal_type_suggestion="unknown",
                confidence_level=AnalysisConfidence.LOW,
                raw_response="",
                error_message=f"Analysis failed: {str(e)}",
            )

    def _parse_response(self, raw_response: str) -> FoodAnalysisResult:
        """Parse the Claude response into a structured result."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[\s\S]*\}', raw_response)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            if not data.get("success", False):
                return FoodAnalysisResult(
                    success=False,
                    food_items=[],
                    total_calories=0,
                    total_protein=0,
                    total_carbs=0,
                    total_fat=0,
                    total_fiber=0,
                    meal_type_suggestion="unknown",
                    confidence_level=AnalysisConfidence.LOW,
                    raw_response=raw_response,
                    error_message=data.get("error_message", "Could not identify food in image"),
                )

            # Parse food items
            food_items = []
            for item in data.get("food_items", []):
                food_items.append(FoodItem(
                    name=item.get("name", "Unknown"),
                    name_tr=item.get("name_tr"),
                    estimated_portion=item.get("estimated_portion", "1 serving"),
                    calories=int(item.get("calories", 0)),
                    protein=float(item.get("protein", 0)),
                    carbs=float(item.get("carbs", 0)),
                    fat=float(item.get("fat", 0)),
                    fiber=float(item.get("fiber", 0)),
                    confidence=float(item.get("confidence", 0.5)),
                ))

            # Calculate overall confidence
            if food_items:
                avg_confidence = sum(f.confidence for f in food_items) / len(food_items)
                if avg_confidence > 0.8:
                    confidence_level = AnalysisConfidence.HIGH
                elif avg_confidence > 0.5:
                    confidence_level = AnalysisConfidence.MEDIUM
                else:
                    confidence_level = AnalysisConfidence.LOW
            else:
                confidence_level = AnalysisConfidence.LOW

            return FoodAnalysisResult(
                success=True,
                food_items=food_items,
                total_calories=int(data.get("total_calories", 0)),
                total_protein=float(data.get("total_protein", 0)),
                total_carbs=float(data.get("total_carbs", 0)),
                total_fat=float(data.get("total_fat", 0)),
                total_fiber=float(data.get("total_fiber", 0)),
                meal_type_suggestion=data.get("meal_type_suggestion", "snack"),
                confidence_level=confidence_level,
                raw_response=raw_response,
            )

        except (json.JSONDecodeError, ValueError) as e:
            return FoodAnalysisResult(
                success=False,
                food_items=[],
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fat=0,
                total_fiber=0,
                meal_type_suggestion="unknown",
                confidence_level=AnalysisConfidence.LOW,
                raw_response=raw_response,
                error_message=f"Failed to parse response: {str(e)}",
            )

    async def analyze_food_image_from_url(
        self,
        image_url: str,
        additional_context: Optional[str] = None
    ) -> FoodAnalysisResult:
        """
        Analyze a food image from a URL.

        Args:
            image_url: URL of the image to analyze
            additional_context: Optional context about the meal

        Returns:
            FoodAnalysisResult with detected foods and nutritional information
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()

                # Determine image type from content-type header
                content_type = response.headers.get("content-type", "image/jpeg")

                return await self.analyze_food_image(
                    image_data=response.content,
                    image_type=content_type,
                    additional_context=additional_context,
                )

        except httpx.HTTPError as e:
            return FoodAnalysisResult(
                success=False,
                food_items=[],
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fat=0,
                total_fiber=0,
                meal_type_suggestion="unknown",
                confidence_level=AnalysisConfidence.LOW,
                raw_response="",
                error_message=f"Failed to fetch image: {str(e)}",
            )


# Synchronous wrapper for non-async contexts
def analyze_food_image_sync(
    image_data: bytes,
    api_key: Optional[str] = None,
    image_type: str = "image/jpeg",
    additional_context: Optional[str] = None
) -> FoodAnalysisResult:
    """
    Synchronous wrapper for food image analysis.

    Args:
        image_data: Raw image bytes
        api_key: Anthropic API key
        image_type: MIME type of the image
        additional_context: Optional context about the meal

    Returns:
        FoodAnalysisResult with detected foods and nutritional information
    """
    import asyncio

    analyzer = FoodAnalyzer(api_key=api_key)

    # Run the async function synchronously
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(
        analyzer.analyze_food_image(
            image_data=image_data,
            image_type=image_type,
            additional_context=additional_context,
        )
    )
