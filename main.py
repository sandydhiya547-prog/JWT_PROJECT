from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import datetime

app = FastAPI()

SECRET_KEY = "change-this-to-a-long-secret-key"
ALGORITHM = "HS256"

security = HTTPBearer()


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginData):
    if data.username != "john" or data.password != "1234":
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    payload = {
        "user_id": 101,
        "username": data.username,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}


@app.get("/profile")
def profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        decoded_data = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return {
            "message": "Welcome",
            "user_id": decoded_data["user_id"],
            "username": decoded_data["username"]
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")