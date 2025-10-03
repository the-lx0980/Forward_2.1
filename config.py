from os import getenv

class Config:   
    API_ID = int(getenv("API_ID", ""))
    API_HASH = getenv("API_HASH", "")
    TG_BOT_TOKEN = getenv("TG_BOT_TOKEN", "") 
    OWNER_ID = set(int(x) for x in getenv("OWNER_ID", "").split())
    DATABASE_URI = getenv("DATABASE_URI", "")
    TO_CHANNEL = int(getenv('TO_CHANNEL'))
