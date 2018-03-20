from bson import objectid
from pymongo import ReturnDocument
from pymongo import errors

from er import db
from er import error
from er.util import argmethod
from er.util import validator

STATUS_PENDING = 0
STATUS_REJECTED = 1
STATUS_APPROVED = 2

STATUS_TEXTS = {STATUS_APPROVED: '通过审核',
                STATUS_PENDING: '等待审核',
                STATUS_REJECTED: '审核未通过'}

def is_status(s):
  return s in {STATUS_REJECTED, STATUS_APPROVED, STATUS_PENDING}


def check_status(s):
  if not is_status(s):
    raise error.ValidationError('报名状态', '只能为等待、未通过与已通过。')


@argmethod.wrap
async def add(creator_id: objectid.ObjectId, event_id: objectid.ObjectId, forcer_id: objectid.ObjectId=None,
              team_ids: list=[], team_leader: objectid.ObjectId=None, fields: list=[],
              status: int=STATUS_PENDING, reply: str=''):
  """
  Add a registration into database after ensuring it's not duplicate.
  """
  check_status(status)
  validator.check_fields(fields)
  validator.check_reply(reply)
  validator.check_team_ids(team_ids)
  coll = db.coll('registrations')
  obj_id = objectid.ObjectId()
  try:
    await coll.insert_one({'_id': obj_id,
                           'creator_id': creator_id,
                           'event_id': event_id,
                           'forcer_id': forcer_id,
                           'team_ids': team_ids,
                           'team_leader': team_leader,
                           'fields': fields,
                           'status': status,
                           'reply': reply,
                           'rank': 0,
                           'result': ''})
  except errors.DuplicateKeyError:
    raise error.DuplicateRegistrationError(creator_id, event_id)
  return obj_id


@argmethod.wrap
async def get(rid: objectid.ObjectId):
  """
  Find a document by its _id.
  """
  coll = db.coll('registrations')
  rdoc = await coll.find_one({'_id': rid})
  if not rdoc:
    raise error.RegistrationNotFoundError(rid)
  return rdoc


@argmethod.wrap
async def get_by_ids(creator: objectid.ObjectId, event: objectid.ObjectId):
    """
    Find a document by its creator_id and event_id.
    """
    coll = db.coll('registrations')
    rdoc = await coll.find_one({'creator_id': creator,
                                'event_id': event})
    return rdoc


@argmethod.wrap
def get_multi_by_creator(creator_id: objectid.ObjectId):
  coll = db.coll('registrations')
  return coll.find({'creator_id': creator_id}).sort('_id', -1)


@argmethod.wrap
def get_multi_by_event(event_id: objectid.ObjectId, **kwargs):
  coll = db.coll('registrations')
  return coll.find({'event_id': event_id, **kwargs}).sort('_id', 1)


def get_multi(**kwargs):
  coll = db.coll('registrations')
  return coll.find(kwargs)


@argmethod.wrap
async def edit(rid: objectid.ObjectId, **kwargs):
  """
  Find and edit a document.
  """
  if 'status' in kwargs:
    check_status(kwargs['status'])
  if 'creator_id' in kwargs:
    raise error.InvalidArgumentError('creator_id')
  if 'event_id' in kwargs:
    raise error.InvalidArgumentError('event_id')
  if 'forcer_id' in kwargs:
    raise error.InvalidArgumentError('forcer_id')
  if 'fields' in kwargs:
    validator.check_fields(kwargs['fields'])
  if 'reply' in kwargs:
    validator.check_reply(kwargs['reply'])
  if 'rank' in kwargs:
    validator.check_rank(kwargs['rank'])
  if 'result' in kwargs:
    validator.check_result(kwargs['result'])
  if 'team_ids' in kwargs:
    validator.check_team_ids(kwargs['team_ids'])
  coll = db.coll('registrations')
  rdoc = await coll.find_one_and_update({'_id': rid},
                                        update={'$set': kwargs},
                                        return_document=ReturnDocument.AFTER)
  if not rdoc:
    raise error.RegistrationNotFoundError(rid)
  return rdoc


@argmethod.wrap
async def delete(rid: objectid.ObjectId):
  coll = db.coll('registrations')
  return await coll.delete_one({'_id': rid})


async def review(rids, status, reply=''):
  validator.check_reply(reply)
  check_status(status)
  coll = db.coll('registrations')
  await coll.update_many({'_id': {'$in': list(set(rids))}},
                         {'$set': {'status': status, 'reply': reply}})


@argmethod.wrap
async def has_group(eid: objectid.ObjectId, uid: objectid.ObjectId, exc: objectid.ObjectId=None):
  coll = db.coll('registrations')
  query = {'event_id': eid, '$or': [{'team_leader': uid}, {'team_ids': uid}]}
  if exc:
    query['_id'] = {'$ne': exc}
  return bool(await coll.find_one(query))


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('registrations')
  await coll.create_index([('creator_id', 1), ('event_id', 1)],
                          unique=True)
  await coll.create_index([('creator_id', 1), ('_id', -1)])
  await coll.create_index([('event_id', 1), ('_id', 1)])
  await coll.create_index([('event_id', 1), ('rank', 1), ('_id', 1)])
  await coll.create_index([('event_id', 1), ('team_leader', 1)], sparse=True)
  await coll.create_index([('event_id', 1), ('team_ids', 1)], sparse=True)


if __name__ == '__main__':
  argmethod.invoke_by_args()
