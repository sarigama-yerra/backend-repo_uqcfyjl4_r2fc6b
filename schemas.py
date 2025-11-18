"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Coin identifier app schemas

class CoinAnalysis(BaseModel):
    """
    Coin analyses collection schema
    Collection name: "coinanalysis" (lowercase of class name)
    """
    filename: Optional[str] = Field(None, description="Original uploaded file name")
    name: Optional[str] = Field(None, description="Coin name or type, e.g., 'Lincoln Wheat Cent'")
    country: Optional[str] = Field(None, description="Country or region of origin")
    year: Optional[str] = Field(None, description="Year or date range visible/estimated")
    denomination: Optional[str] = Field(None, description="Face value / denomination")
    composition: Optional[str] = Field(None, description="Metal composition")
    mint_mark: Optional[str] = Field(None, description="Mint mark if detected")
    history: Optional[str] = Field(None, description="Historical background and significance")
    features: Optional[str] = Field(None, description="Key identifying features")
    condition_estimate: Optional[str] = Field(None, description="Estimated condition/grade if possible")
    estimated_value: Optional[str] = Field(None, description="Estimated value range in USD or local currency")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score between 0 and 1")
    model: Optional[str] = Field(None, description="AI model used for analysis")
    raw_analysis: Optional[Dict[str, Any]] = Field(
        None, description="Raw JSON response from the AI before normalization"
    )
