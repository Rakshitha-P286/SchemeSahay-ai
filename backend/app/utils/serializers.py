from bson import ObjectId

def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [serialize(x) for x in value]
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items() if k != "_id"} | ({"id": str(value["_id"])} if "_id" in value else {})
    return value
