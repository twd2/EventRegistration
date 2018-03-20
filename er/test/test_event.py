import datetime
import unittest

from bson import objectid

from er import error
from er.model import event
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)
DUMMY_NAME = '9# basketball'
DUMMY_NAME2 = '10# basketball'
DUMMY_INTRO = '5 vs 5'
DUMMY_CREATOR_ID = objectid.ObjectId('e' * 24)
DUMMY_BEGIN_AT = datetime.datetime(2017, 11, 1, 12, 0, 0)
DUMMY_END_AT = datetime.datetime(2017, 12, 1, 12, 0, 0)
DUMMY_PLACE = '1'
DUMMY_TIME = '1'
DUMMY_REGISTER_LIMIT = 1
DUMMY_SHOW_LIST= True
DUMMY_IS_GROUP = True
DUMMY_MEMBER_LB = 2
DUMMY_MEMBER_UB = 3
DUMMY_TAGS = ['9#']
DUMMY_FIELDS = [{'type': event.TYPE_STRING, 'name': '大学生平均学分绩点'},
                {'type': event.TYPE_STRING, 'name': '参赛理由'}]
DUMMY_FIELDS2 = [''] * 1001
DUMMY_FIELDS3 = [{'type': event.TYPE_STRING}]
DUMMY_FIELDS4 = [{'type': event.TYPE_STRING, 'name': '大学生平均学分绩点'},
                {'type': event.TYPE_STRING, 'name': ''}]
DUMMY_FIELDS5 = [{'type': 1, 'name': '大学生平均学分绩点'}]


class Test(base.DatabaseTestCase):
  def test_check_tags(self):
    with self.assertRaises(error.ValidationError):
      event.check_tags([''] * 1001)
    with self.assertRaises(error.ValidationError):
      event.check_tags([''])
    with self.assertRaises(error.ValidationError):
      event.check_tags(['f' * 65])

  def test_sanitize_and_check_fields(self):
    with self.assertRaises(error.ValidationError):
      event.sanitize_and_check_fields(DUMMY_FIELDS2)
    with self.assertRaises(error.ValidationError):
      event.sanitize_and_check_fields(DUMMY_FIELDS3)
    with self.assertRaises(error.ValidationError):
      event.sanitize_and_check_fields(DUMMY_FIELDS4)
    with self.assertRaises(error.ValidationError):
      event.sanitize_and_check_fields(DUMMY_FIELDS5)

  def test_check_register(self):
    with self.assertRaises(error.ValidationError):
      event.check_register(-1)

  def test_check_time(self):
    with self.assertRaises(error.ValidationError):
      event.check_time(DUMMY_END_AT, DUMMY_BEGIN_AT)

  def test_check_match_place(self):
    with self.assertRaises(error.ValidationError):
      event.check_match_place('')

  def test_check_match_time(self):
    with self.assertRaises(error.ValidationError):
      event.check_match_time('')

  def test_check_member(self):
    with self.assertRaises(error.ValidationError):
      event.check_member(-1, DUMMY_MEMBER_UB)
    with self.assertRaises(error.ValidationError):
      event.check_member(DUMMY_MEMBER_LB, -1)
    with self.assertRaises(error.ValidationError):
      event.check_member(DUMMY_MEMBER_UB, DUMMY_MEMBER_LB)

  @base.wrap_coro
  async def test_add(self):
    with self.assertRaises(error.ValidationError):
      eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID, DUMMY_END_AT, DUMMY_BEGIN_AT,
                            DUMMY_PLACE, DUMMY_TIME, DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                            DUMMY_IS_GROUP, DUMMY_MEMBER_LB, DUMMY_MEMBER_UB,
                            DUMMY_TAGS, DUMMY_FIELDS)
    with self.assertRaises(error.ValidationError):
      eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID, DUMMY_BEGIN_AT, DUMMY_END_AT,
                            DUMMY_PLACE, DUMMY_TIME, DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                            DUMMY_IS_GROUP, DUMMY_MEMBER_UB, DUMMY_MEMBER_LB,
                            DUMMY_TAGS, DUMMY_FIELDS)
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID, DUMMY_BEGIN_AT, DUMMY_END_AT,
                          DUMMY_PLACE, DUMMY_TIME, DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                          DUMMY_IS_GROUP, DUMMY_MEMBER_LB, DUMMY_MEMBER_UB, DUMMY_TAGS, DUMMY_FIELDS)
    edoc = await event.get(eid)
    self.assertEqual(edoc['_id'], eid)
    self.assertEqual(edoc['name'], DUMMY_NAME)
    self.assertEqual(edoc['intro'], DUMMY_INTRO)
    self.assertEqual(edoc['creator_id'], DUMMY_CREATOR_ID)
    self.assertEqual(edoc['begin_at'], DUMMY_BEGIN_AT)
    self.assertEqual(edoc['end_at'], DUMMY_END_AT)
    self.assertEqual(edoc['place'], DUMMY_PLACE)
    self.assertEqual(edoc['time'], DUMMY_TIME)
    self.assertEqual(edoc['register_limit'], DUMMY_REGISTER_LIMIT)
    self.assertEqual(edoc['show_list'], DUMMY_SHOW_LIST)
    self.assertEqual(edoc['is_group'], DUMMY_IS_GROUP)
    self.assertEqual(edoc['member_lb'], DUMMY_MEMBER_LB)
    self.assertEqual(edoc['member_ub'], DUMMY_MEMBER_UB)
    self.assertEqual(edoc['tags'], DUMMY_TAGS)
    self.assertEqual(edoc['fields'], DUMMY_FIELDS)

  @base.wrap_coro
  async def test_delete(self):
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID,
                          DUMMY_BEGIN_AT, DUMMY_END_AT, DUMMY_PLACE, DUMMY_TIME,
                          DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST, DUMMY_IS_GROUP,
                          DUMMY_MEMBER_LB, DUMMY_MEMBER_UB,
                          DUMMY_TAGS, DUMMY_FIELDS)
    edoc = await event.get(eid)
    await event.delete(eid)
    with self.assertRaises(error.EventNotFoundError):
      edoc = await event.get(eid)

  @base.wrap_coro
  async def test_inc(self):
    with self.assertRaises(error.EventNotFoundError):
      edoc = await event.inc(DUMMY_ID, num_view=1, num_register=1)
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID,
                          DUMMY_BEGIN_AT, DUMMY_END_AT, DUMMY_PLACE, DUMMY_TIME,
                          DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                          DUMMY_IS_GROUP, DUMMY_MEMBER_LB, DUMMY_MEMBER_UB,
                          DUMMY_TAGS, DUMMY_FIELDS)
    edoc = await event.get(eid)
    self.assertEqual(0, edoc['num_view'])
    self.assertEqual(0, edoc['num_register'])
    edoc = await event.inc(eid, num_view=1, num_register=1)
    self.assertEqual(1, edoc['num_view'])
    self.assertEqual(1, edoc['num_register'])

  @base.wrap_coro
  async def test_inc_limited(self):
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID,
                          DUMMY_BEGIN_AT, DUMMY_END_AT, DUMMY_PLACE, DUMMY_TIME,
                          DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                          DUMMY_IS_GROUP, DUMMY_MEMBER_LB, DUMMY_MEMBER_UB,
                          DUMMY_TAGS, DUMMY_FIELDS)
    edoc = await event.get(eid)
    self.assertEqual(0, edoc['num_view'])
    self.assertEqual(0, edoc['num_register'])
    edoc = await event.inc_limited(eid, 'num_register', edoc['register_limit'])
    self.assertEqual(0, edoc['num_view'])
    self.assertEqual(1, edoc['num_register'])
    edoc = await event.inc_limited(eid, 'num_register', edoc['register_limit'])
    self.assertEqual(None, edoc)
    edoc = await event.get(eid)
    self.assertEqual(0, edoc['num_view'])
    self.assertEqual(1, edoc['num_register'])

  @base.wrap_coro
  async def test_get(self):
    with self.assertRaises(error.EventNotFoundError):
      edoc = await event.get(DUMMY_ID)

  @base.wrap_coro
  async def test_edit(self):
    with self.assertRaises(error.EventNotFoundError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name='', intro='', fields=[])
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, begin_at=DUMMY_BEGIN_AT)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, end_at=DUMMY_END_AT)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, begin_at=DUMMY_END_AT,
                              end_at=DUMMY_BEGIN_AT)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, register_limit=-1)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, member_lb=DUMMY_MEMBER_LB)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, member_ub=DUMMY_MEMBER_UB)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, intro=DUMMY_INTRO,
                              fields=DUMMY_FIELDS, member_lb=DUMMY_MEMBER_UB,
                              member_ub=DUMMY_MEMBER_LB)
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, place='')
    with self.assertRaises(error.ValidationError):
      edoc = await event.edit(DUMMY_ID, name=DUMMY_NAME, time='')
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID,
                          DUMMY_BEGIN_AT, DUMMY_END_AT, DUMMY_PLACE, DUMMY_TIME,
                          DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST,
                          DUMMY_IS_GROUP, DUMMY_MEMBER_LB, DUMMY_MEMBER_UB,
                          DUMMY_TAGS, DUMMY_FIELDS)
    edoc = await event.edit(eid, name=DUMMY_NAME2, tags=[], fields=[])

  @base.wrap_coro
  async def test_get_dict(self):
    eid = await event.add(DUMMY_NAME, DUMMY_INTRO, DUMMY_CREATOR_ID,
                          DUMMY_BEGIN_AT, DUMMY_END_AT, DUMMY_PLACE, DUMMY_TIME,
                          DUMMY_REGISTER_LIMIT, DUMMY_SHOW_LIST, DUMMY_IS_GROUP,
                          DUMMY_MEMBER_LB, DUMMY_MEMBER_UB)
    edoc = await event.get(eid)
    edict = await event.get_dict([DUMMY_ID, eid])
    self.assertEqual(len(edict), 1)
    self.assertEqual(edoc, edict[eid])


if __name__ == '__main__':
  unittest.main()
