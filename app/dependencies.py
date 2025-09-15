import motor.motor_asyncio
from fastapi.security import OAuth2PasswordBearer
from os import getenv

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

client = motor.motor_asyncio.AsyncIOMotorClient(getenv("MONGO_URL"))
database = client.dayder
