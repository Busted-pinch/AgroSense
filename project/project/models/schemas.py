from pydantic import BaseModel, EmailStr
from typing import List

class SignupInput(BaseModel):
    email: EmailStr
    password: str

class SignupOutput(BaseModel):
    message: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MarketRequest(BaseModel):
    supply: float
    demand: float
    cost: float
    price: float

class MarketOutput(BaseModel):
    profit: float
    supply_status: str

class GuidelineOutput(BaseModel):
    recommendations: List[str]