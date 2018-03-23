import collections
import datetime
import functools
from bson import objectid
from pymongo import ReturnDocument

from er import db
from er import error
from er.model import builtin
from er.util import argmethod
from er.util import validator


Field = functools.partial(
  collections.namedtuple('Field', ['key', 'name', 'oauth_map', 'length_min', 'length_max']),
  oauth_map=None, length_min=1, length_max=500)

FIELDS = [
  Field('student_id', '学号'),
  Field('chinese_id', '证件号', length_min=0),
  Field('gender', '性别'),
  Field('birthday', '生日', oauth_map='birthdate', length_min=8, length_max=8),
  Field('degree', '攻读学位'),
  Field('department', '院系'),
  Field('class', '班级'),
  Field('size', '服装尺寸'),
  Field('mobile', '手机号码', oauth_map='mobile'),
  Field('room', '宿舍房间号')
]

FIELDS = collections.OrderedDict((f.key, f) for f in FIELDS)


@argmethod.wrap
async def init(username: str, rawdoc={}):
  """
    Get a user by its username. Create one and set enable_at=None when not exists.
  """
  coll = db.coll('users')
  init_udoc = {
    'username': username,
    'username_lower': username.lower(),
    'role': builtin.ROLE_USER,
    'name': '',
    'mail': '',
    'enable_at': None,
    'raw': rawdoc,
    **dict((f.key, '') for f in FIELDS.values())
  }
  udoc = await coll.find_one_and_update({'username': username},
                                        update={'$setOnInsert': init_udoc},
                                        upsert=True,
                                        return_document=ReturnDocument.AFTER)
  return udoc


@argmethod.wrap
async def get(uid: objectid.ObjectId):
  """
    Get a user by its _id.
  """
  coll = db.coll('users')
  udoc = await coll.find_one({'_id': uid})
  if not udoc:
    raise error.UserNotFoundError(uid)
  return udoc


@argmethod.wrap
async def get_by_username(username: str):
  """
    Get a user by its username.
  """
  coll = db.coll('users')
  udoc = await coll.find_one({'username': username})
  if not udoc:
    raise error.UserNotFoundError(username)
  return udoc


@argmethod.wrap
async def get_list_by_name(name: str):
  """
    Get a list of users by its (real) name.
  """
  coll = db.coll('users')
  return await get_multi(name=name).to_list()


@argmethod.wrap
async def edit(uid: objectid.ObjectId, keep_enabled=False, **kwargs):
  if 'role' in kwargs:
    raise error.InvalidArgumentError('role')
  if 'name' in kwargs:
    validator.check_name(kwargs['name'])
  if 'mail' in kwargs:
    validator.check_mail(kwargs['mail'])
  coll = db.coll('users')
  if not keep_enabled:
    kwargs['enable_at'] = datetime.datetime.utcnow()
  udoc = await coll.find_one_and_update({'_id': uid},
                                        update={'$set': kwargs},
                                        return_document=ReturnDocument.AFTER)
  if not udoc:
    raise error.UserNotFoundError(uid)
  return udoc


@argmethod.wrap
async def set_role(uid: objectid.ObjectId, role: int):
  coll = db.coll('users')
  udoc = await coll.find_one_and_update({'_id': uid},
                                        update={'$set': {'role': role}},
                                        return_document=ReturnDocument.AFTER)
  if not udoc:
    raise error.UserNotFoundError(uid)
  return udoc


@argmethod.wrap
async def set_role_by_username(username: str, role: int, when_old_role: int=None):
  coll = db.coll('users')
  filter = {}
  if when_old_role != None:
    filter = {'role': when_old_role}
  udoc = await coll.find_one_and_update({'username': username, **filter},
                                        update={'$set': {'role': role}},
                                        return_document=ReturnDocument.AFTER)
  if not udoc:
    raise error.UserNotFoundError(username)
  return udoc


async def set_roles(uids, role, when_old_role: int=None):
  coll = db.coll('users')
  filter = {}
  if when_old_role != None:
    filter = {'role': when_old_role}
  await coll.update_many({'_id': {'$in': list(set(uids))}, **filter},
                         {'$set': {'role': role}})


def get_multi(**kwargs):
  coll = db.coll('users')
  return coll.find(kwargs)


@argmethod.wrap
async def get_list_by_role(role: int):
  return await get_multi(role=role).to_list()


async def get_dict(uids):
  result = dict()
  async for doc in get_multi(_id={'$in': list(set(uids))}):
    result[doc['_id']] = doc
  return result


async def get_dict_by_username(usernames):
  result = dict()
  async for doc in get_multi(username={'$in': list(set(usernames))}):
    result[doc['username']] = doc
  return result


@argmethod.wrap
async def get_prefix_list(prefix: str, limit: int=50):
  prefix = prefix.lower()
  regex = '\\A\\Q{0}\\E'.format(prefix.replace('\\E', '\\E\\\\E\\Q'))
  coll = db.coll('users')
  udocs = await coll.find({'username_lower': {'$regex': regex}}) \
                    .limit(limit) \
                    .to_list()
  return udocs


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('users')
  await coll.create_index('username', unique=True)
  await coll.create_index('username_lower')
  await coll.create_index('name')
  await coll.create_index([('role', 1),
                           ('_id', 1)])


if __name__ == '__main__':
  argmethod.invoke_by_args()
