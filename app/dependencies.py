import motor.motor_asyncio
from fastapi.security import OAuth2PasswordBearer
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
database = client.dayder
