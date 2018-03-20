import collections
import datetime
import functools

from bson import objectid
from pymongo import ReturnDocument

from er import db
from er import error
from er.util import argmethod
from er.util import validator

TYPE_ATHLETE = 0
TYPE_TEAM = 1


Field = functools.partial(
  collections.namedtuple('Field', ['key', 'name', 'length_min', 'length_max']),
  length_min=1, length_max=500)

ATHLETE_FIELDS = [
  Field('year', '入选年份'),
  Field('name', '姓名'),
  Field('gender', '性别'),
  Field('grade', '级数'),
  Field('class', '班级'),
  Field('subject', '主要项目'),
  Field('link', '访谈记录链接', length_min=0),
  Field('bio', '个人简介'),
  Field('honor', '个人荣誉'),
  Field('images_text', '个人风采图片', length_min=0),
]

ATHLETE_FIELDS = collections.OrderedDict((f.key, f) for f in ATHLETE_FIELDS)

TEAM_FIELDS = [
  Field('name', '队名'),
  Field('bio', '队伍简介'),
  Field('instructor', '教练'),
  Field('leader', '队长'),
  Field('members', '队员'),
  Field('images_text', '队伍风采图片', length_min=0),
]

TEAM_FIELDS = collections.OrderedDict((f.key, f) for f in TEAM_FIELDS)


@argmethod.wrap
async def add(type: int, **kwargs):
  """
    Add an document. Returns the document id.
  """
  obj_id = objectid.ObjectId()
  coll = db.coll('documents')
  await coll.insert_one({'_id': obj_id,
                         'type': type,
                         'num_view': 0,
                         **kwargs})
  return obj_id


@argmethod.wrap
async def delete(did: objectid.ObjectId, type: int):
  coll = db.coll('documents')
  return await coll.delete_one({'type': type, '_id': did})


@argmethod.wrap
async def inc(did: objectid.ObjectId, type: int, **kwargs):
  """
    Increase num_view.
  """
  coll = db.coll('documents')
  ddoc = await coll.find_one_and_update(
    filter={'type': type, '_id': did},
    update={'$inc': kwargs},
    return_document=ReturnDocument.AFTER)
  if not ddoc:
    raise error.DocumentNotFoundError(did)
  return ddoc


@argmethod.wrap
async def get(did: objectid.ObjectId, type: int):
  """
    Get an event by its _id.
  """
  coll = db.coll('documents')
  ddoc = await coll.find_one({'type': type, '_id': did})
  if not ddoc:
    raise error.DocumentNotFoundError(did)
  return ddoc


@argmethod.wrap
async def edit(did: objectid.ObjectId, type: int, **kwargs):
  coll = db.coll('documents')
  ddoc = await coll.find_one_and_update({'type': type, '_id': did},
                                        update={'$set': kwargs},
                                        return_document=ReturnDocument.AFTER)
  if not ddoc:
    raise error.DocumentNotFoundError(did)
  return ddoc


def get_multi(type, **kwargs):
  coll = db.coll('documents')
  return coll.find({'type': type, **kwargs})


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('documents')
  await coll.create_index([('type', 1), ('_id', -1)])
  await coll.create_index([('type', 1), ('year', -1), ('_id', -1)], sparse=True)


if __name__ == '__main__':
  argmethod.invoke_by_args()
