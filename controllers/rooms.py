from config import MONGODB_DB_NAME
from controllers.users import get_user
from mongodb import get_nosql_db
from models import RoomInDB
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


async def insert_room(username, room_name, collection):
    room = {}
    room["room_name"] = room_name
    user = await get_user(username)
    room["members"] = [user] if user is not None else []
    dbroom = RoomInDB(**room)
    response = collection.insert_one(dbroom.dict())
    return {"id_inserted": str(response.inserted_id)}


async def get_rooms():
    client = await get_nosql_db()
    db = client[MONGODB_DB_NAME]
    collection = db.rooms
    rows = collection.find()
    row_list = []
    for row in rows:
        row["_id"] = str(row["_id"])
        row_list.append(row)
    return row_list


async def get_room(room_name) -> RoomInDB:
    client = await get_nosql_db()
    db_client = client[MONGODB_DB_NAME]
    db = db_client.rooms
    row = db.find_one({"room_name": room_name})
    if row is not None:
        row["_id"] = str(row["_id"])
        return row
    else:
        return None


async def set_room_activity(room_name, activity_bool):
    client = await get_nosql_db()
    db_client = client[MONGODB_DB_NAME]
    db = db_client.rooms
    room = await get_room(room_name)
    if room is not None:
        _id = room["_id"]
        try:
            result = db.update_one({"_id": ObjectId(_id)}, { "$set": {"active": activity_bool}})
            if result.modified_count < 1:
                raise Exception("Room activity could not be updated")
        except Exception as e:
            logger.error(f"ERROR SETTING ACTIVITY: {e}")
        new_doc = await get_room(room_name)
        return new_doc
    else:
        return None