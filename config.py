from os import getenv
class Config:   
    APP_ID = int(getenv("APP_ID", "21288218"))
    API_HASH = getenv("API_HASH", "dd47d5c4fbc31534aa764ef9918b3acd")
    TG_BOT_TOKEN = getenv("TG_BOT_TOKEN", "") 
    OWNER_ID = int(getenv("OWNER_ID", ""))
    DATABASE_URI = getenv("DATABASE_URI", "")
    TO_CHANNEL = int(getenv('TO_CHANNEL'))
