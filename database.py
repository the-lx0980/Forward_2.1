import logging
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATABASE_URI = Config.DATABASE_URI
DATABASE_NAME = "forward_media" 
COLLECTION_NAME = "media-collection" 


client = AsyncIOMotorClient(DATABASE_URI)
database = client[DATABASE_NAME]
instance = Instance.from_db(database)

@instance.register
class Data(Document):
    id = fields.StrField(attribute='_id', required=True)
    use = fields.StrField(required=True)
    caption = fields.StrField(required=True)

    class Meta:
        collection_name = COLLECTION_NAME

async def save_data(id, caption):
    try:
        data = Data(
            id=id,
            use = "forward",
            caption=caption          
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
    else:
        try:
            await data.commit()
        except DuplicateKeyError:
            logger.warning("Already saved in Database")
        else:
            logger.info("Messsage saved in DB")


async def get_search_results():
    filter = {'use': "forward"}
    cursor = Data.find(filter)
    cursor.sort('$natural', 1)
    cursor.skip(0).limit(1)
    Messages = await cursor.to_list(length=1)
    return Messages
