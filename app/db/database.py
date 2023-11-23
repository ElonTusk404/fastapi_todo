from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()
client = AsyncIOMotorClient(os.environ['DATABASE_URL'])
db = client.prod