from os import getenv

class Config:   
    API_ID = int(getenv("API_ID", ""))
    API_HASH = getenv("API_HASH", "")
    TG_BOT_TOKEN = getenv("TG_BOT_TOKEN", "") 
    OWNER_ID = int(getenv("OWNER_ID", ""))
    DATABASE_URI = getenv("DATABASE_URI", "")
    TO_CHANNEL = int(getenv('TO_CHANNEL'))
