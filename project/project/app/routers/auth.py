from fastapi import APIRouter, HTTPException
from models.schemas import SignupInput, SignupOutput, LoginInput, TokenOutput
from app.services.auth_service import create_user, authenticate_user, create_access_token
from app.utils.logger import logger  

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/signup", response_model=SignupOutput)
def signup(data: SignupInput):
    logger.info("Signup request received for email=%s", data.email)
    try:
        create_user(data.email, data.password)
        logger.info("User registered successfully: %s", data.email)
        return {"message": "User registered"}
    except Exception as e:
        logger.error("Signup failed for email=%s: %s", data.email, e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenOutput)
def login(data: LoginInput):
    logger.info("Login request received for email=%s", data.email)
    if not authenticate_user(data.email, data.password):
        logger.warning("Login failed for email=%s: Invalid credentials", data.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": data.email})
    logger.info("Login successful for email=%s", data.email)
    return {"access_token": token, "token_type": "bearer"}
