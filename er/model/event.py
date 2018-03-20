import datetime

from bson import objectid
from pymongo import ReturnDocument

from er import db
from er import error
from er.util import argmethod
from er.util import validator

TYPE_STRING = 0


def check_tags(tags):
  if len(tags) > 1000:
    raise error.ValidationError('标签', '标签个数须小于等于1000个。')
  for tag in tags:
    if not (0 < len(tag) <= 64):
      raise error.ValidationError('标签', '每个标签的字数须介于1~64之间。')


def sanitize_and_check_fields(fields):
  if len(fields) > 1000:
    raise error.ValidationError('附加字段', '附加字段个数须小于等于1000。')
  for field in fields:
    if not (isinstance(field, dict) and len(field) == 2 and 'type' in field and 'name' in field):
      raise error.ValidationError('附加字段', '每个附加字段须包含且只包含类型和名称。')
    field['name'] = str(field['name'])
    field['type'] = int(field['type'])
    if not validator.is_name(field['name']):
      raise error.ValidationError('附加字段', '每个附加字段的名称须介于1~64之间。')
    if field['type'] != TYPE_STRING:
      raise error.ValidationError('附加字段', '每个附加字段的类型只能为字符串。')


def check_time(begin_at: datetime.datetime, end_at: datetime.datetime):
  if begin_at > end_at:
    raise error.ValidationError('开始时间', '结束时间', '结束时间不得早于开始时间。')


def check_match_place(place: str):
  if not (0 < len(place) <= 500):
    raise error.ValidationError('比赛地点', '比赛地点的字数须介于1~500之间。')


def check_match_time(time: str):
  if not (0 < len(time) <= 500):
    raise error.ValidationError('比赛时间', '比赛时间的字数须介于1~500之间。')


def check_register(register_limit: int):
  if register_limit < 0:
    raise error.ValidationError('报名数限制', '报名数限制须大于等于0。')


def check_member(member_lb: int, member_ub: int):
  if member_lb < 1:
    raise error.ValidationError('每组人数下限', '每组人数下限须大于等于1。')
  if member_lb > member_ub:
    raise error.ValidationError('每组人数下限', '每组人数上限', '每组人数下限不得大于每组人数上限。')


@argmethod.wrap
async def add(name: str, intro: str, creator_id: objectid.ObjectId,
              begin_at: datetime.datetime, end_at: datetime.datetime,
              place: str, time: str, register_limit: int,
              show_list: bool=False, is_group: bool=False, member_lb: int=0,
              member_ub: int=0, tags: list=[], fields: list=[]):
  """
    Add an event. Returns the document id.
  """
  obj_id = objectid.ObjectId()
  coll = db.coll('events')
  validator.check_name(name)
  validator.check_intro(intro)
  check_time(begin_at, end_at)
  check_match_place(place)
  check_match_time(time)
  check_register(register_limit)
  check_member(member_lb, member_ub)
  check_tags(tags)
  sanitize_and_check_fields(fields)
  await coll.insert_one({'_id': obj_id,
                         'name': name,
                         'intro': intro,
                         'creator_id': creator_id,
                         'tags': tags,
                         'begin_at': begin_at,
                         'end_at': end_at,
                         'num_view': 0,
                         'num_register': 0,
                         'place': place,
                         'time': time,
                         'register_limit': register_limit,
                         'show_list': show_list,
                         'is_group': is_group,
                         'member_lb': member_lb,
                         'member_ub': member_ub,
                         'fields': fields})
  return obj_id


@argmethod.wrap
async def delete(eid: objectid.ObjectId):
  coll = db.coll('events')
  return await coll.delete_one({'_id': eid})


@argmethod.wrap
async def inc(eid: objectid.ObjectId, **kwargs):
  """
    Increase num_view and/or num_register.
  """
  coll = db.coll('events')
  edoc = await coll.find_one_and_update(
    filter={'_id': eid},
    update={'$inc': kwargs},
    return_document=ReturnDocument.AFTER)
  if not edoc:
    raise error.EventNotFoundError(eid)
  return edoc


@argmethod.wrap
async def inc_limited(eid: objectid.ObjectId, field: str, limit: int, inc: int=1):
  coll = db.coll('events')
  edoc = await coll.find_one_and_update(filter={'_id': eid,
                                                 field: {'$not': {'$gte': limit}}},
                                         update={'$inc': {field: inc}},
                                         return_document=ReturnDocument.AFTER)
  return edoc


@argmethod.wrap
async def get(eid: objectid.ObjectId):
  """
    Get an event by its _id.
  """
  coll = db.coll('events')
  edoc = await coll.find_one({'_id': eid})
  if not edoc:
    raise error.EventNotFoundError(eid)
  return edoc


@argmethod.wrap
async def edit(eid: objectid.ObjectId, **kwargs):
  if 'name' in kwargs:
    validator.check_event_name(kwargs['name'])
  if 'intro' in kwargs:
    validator.check_intro(kwargs['intro'])
  if ('begin_at' in kwargs) != ('end_at' in kwargs):
    raise error.ValidationError('开始时间', '结束时间', '开始时间和结束时间必须同时出现。')
  if 'begin_at' in kwargs and 'end_at' in kwargs:
    check_time(kwargs['begin_at'], kwargs['end_at'])
  if 'place' in kwargs:
    check_match_place(kwargs['place'])
  if 'time' in kwargs:
    check_match_time(kwargs['time'])
  if 'register_limit' in kwargs:
    check_register(kwargs['register_limit'])
  if ('member_lb' in kwargs) != ('member_ub' in kwargs):
    raise error.ValidationError('每组人数下限', '每组人数上限', '每组人数下限和每组人数上限必须同时出现。')
  if 'member_lb' in kwargs and 'member_ub' in kwargs:
    check_member(kwargs['member_lb'], kwargs['member_ub'])
  if 'tags' in kwargs:
    check_tags(kwargs['tags'])
  if 'fields' in kwargs:
    sanitize_and_check_fields(kwargs['fields'])
  coll = db.coll('events')
  edoc = await coll.find_one_and_update({'_id': eid},
                                        update={'$set': kwargs},
                                        return_document=ReturnDocument.AFTER)
  if not edoc:
    raise error.EventNotFoundError(eid)
  return edoc


def get_multi(**kwargs):
  coll = db.coll('events')
  return coll.find(kwargs)


async def get_dict(eids):
  result = dict()
  async for doc in get_multi(_id={'$in': list(set(eids))}):
    result[doc['_id']] = doc
  return result


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('events')
  await coll.create_index('name')
  await coll.create_index('creator_id')
  await coll.create_index('tags')
  await coll.create_index([('begin_at', -1),
                           ('_id', -1)])
  await coll.create_index([('num_view', -1),
                           ('_id', -1)])


if __name__ == '__main__':
  argmethod.invoke_by_args()
