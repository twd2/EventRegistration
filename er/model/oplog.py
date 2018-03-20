from bson import objectid

from er import db
from er.util import argmethod

TYPE_DELETE_EVENT = 10
TYPE_DELETE_REGISTRATION = 20
TYPE_DELETE_DOCUMENT = 30


@argmethod.wrap
async def add(creator_id: objectid.ObjectId, type: int, **kwargs):
  """
    Add an operation log. Returns the document id.
  """
  obj_id = objectid.ObjectId()
  coll = db.coll('oplog')
  doc = {'_id': obj_id,
         'creator_id': creator_id,
         'type': type,
         **kwargs}
  await coll.insert_one(doc)
  return obj_id


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('oplog')
  await coll.create_index('creator_id')


if __name__ == '__main__':
  argmethod.invoke_by_args()
