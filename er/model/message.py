from bson import objectid
from pymongo import ReturnDocument

from er import db
from er import error
from er.util import argmethod


@argmethod.wrap
async def add(sender_id: objectid.ObjectId, receiver_id: objectid.ObjectId,
              title: str, content: str):
  """
    Add a message. Returns the document id.
  """
  obj_id = objectid.ObjectId()
  coll = db.coll('messages')
  await coll.insert_one({'_id': obj_id,
                         'sender_id': sender_id,
                         'receiver_id': receiver_id,
                         'title': title,
                         'content': content,
                         'read': False})
  return obj_id


@argmethod.wrap
async def get(mid: objectid.ObjectId):
  """
    Get a message by its _id.
  """
  coll = db.coll('messages')
  mdoc = await coll.find_one({'_id': mid})
  if not mdoc:
    raise error.MessageNotFoundError(mid)
  return mdoc


@argmethod.wrap
def get_by_receiver(receiver_id: objectid.ObjectId, unread_only: bool=True):
  """
    Get messages by its receiver_id.
  """
  coll = db.coll('messages')
  if unread_only:
    query = {'receiver_id': receiver_id, 'read': False}
  else:
    query = {'receiver_id': receiver_id}
  return coll.find(query).sort('_id', -1)


@argmethod.wrap
async def set_read(mid: objectid.ObjectId, read: bool=True):
  """
    set the read status of the message
  """
  coll = db.coll('messages')
  mdoc = await coll.find_one_and_update(
    filter={'_id': mid},
    update={'$set': {'read': read}},
    return_document=ReturnDocument.AFTER)
  if not mdoc:
    raise error.MessageNotFoundError(mid)
  return mdoc


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('messages')
  await coll.create_index('sender_id')
  await coll.create_index([('receiver_id', 1),
                           ('read', 1),
                           ('_id', -1)])
  await coll.create_index([('receiver_id', 1),
                           ('_id', -1)])


if __name__ == '__main__':
  argmethod.invoke_by_args()
