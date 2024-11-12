import motor.motor_asyncio
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
database = client.dayder
