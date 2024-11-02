import motor.motor_asyncio

client  = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
database = client.get_database("dayder")

announcement_collection = database.announcement

user_collection = database.user
