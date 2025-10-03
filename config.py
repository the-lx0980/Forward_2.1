import os
class Config:   
    APP_ID = int(os.environ.get("APP_ID", "21288218"))
    API_HASH = os.environ.get("API_HASH", "dd47d5c4fbc31534aa764ef9918b3acd")
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "") 
    OWNER_ID = int(os.environ.get("OWNER_ID", "")
    DATABASE_URI = os.environ.get("DATABASE_URI", "")
    TO_CHANNEL = int(os.environ.get('TO_CHANNEL'))
