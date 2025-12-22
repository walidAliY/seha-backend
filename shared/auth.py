import jwt
import os
from datetime import datetime, timedelta

# Configuration retrieved from the .env file [cite: 342]
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

def verify_token(token: str):
    """
    Decodes and verifies a JWT token. 
    Returns the payload if valid, otherwise raises an error.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}