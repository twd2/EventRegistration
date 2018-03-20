import unittest
from bson import objectid

from er import error
from er.model import builtin
from er.model import user
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)
DUMMY_USERNAME = 'twd2'
DUMMY_USERNAME2 = 'twd3'
DUMMY_NAME = 'twd'
DUMMY_NAME2 = 'yyf'


class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_init(self):
    udoc = await user.init(DUMMY_USERNAME)
    self.assertEqual(udoc['username'], DUMMY_USERNAME)
    self.assertEqual(udoc['enable_at'], None)
    uid = udoc['_id']
    self.assertTrue(uid)
    udoc = await user.edit(uid, mail='twd2@example.org', keep_enabled=True)
    self.assertEqual(udoc['enable_at'], None)
    udoc = await user.edit(uid, mail='twd3@example.org')
    self.assertNotEqual(udoc['enable_at'], None)
    udoc = await user.init(DUMMY_USERNAME)
    self.assertNotEqual(udoc['enable_at'], None)
    udoc2 = await user.get(uid)
    self.assertEqual(udoc, udoc2)

  @base.wrap_coro
  async def test_get(self):
    with self.assertRaises(error.UserNotFoundError):
      udoc = await user.get(DUMMY_ID)

  @base.wrap_coro
  async def test_get_by_username(self):
    with self.assertRaises(error.UserNotFoundError):
      udoc = await user.get_by_username(DUMMY_USERNAME)
    udoc = await user.init(DUMMY_USERNAME)
    udoc2 = await user.get_by_username(DUMMY_USERNAME)
    self.assertEqual(udoc, udoc2)

  @base.wrap_coro
  async def test_get_list_by_name(self):
    udoc1 = await user.init(DUMMY_USERNAME)
    udoc1 = await user.edit(udoc1['_id'], name=DUMMY_NAME)
    udoc2 = await user.init(DUMMY_USERNAME2)
    udoc2 = await user.edit(udoc2['_id'], name=DUMMY_NAME)
    udocs = await user.get_list_by_name(DUMMY_NAME)
    self.assertEqual(len(udocs), 2)
    self.assertIn(udoc1, udocs)
    self.assertIn(udoc2, udocs)

  @base.wrap_coro
  async def test_get_dict(self):
    udoc = await user.init(DUMMY_USERNAME)
    uid = udoc['_id']
    udoc = await user.get(uid)
    udict = await user.get_dict([DUMMY_ID, uid])
    self.assertEqual(len(udict), 1)
    self.assertEqual(udoc, udict[uid])

  @base.wrap_coro
  async def test_edit(self):
    with self.assertRaises(error.UserNotFoundError):
      udoc = await user.edit(DUMMY_ID, mail='twd2@example.org', keep_enabled=True)
    with self.assertRaises(error.ValidationError):
      udoc = await user.edit(DUMMY_ID, name='', mail='twd2@example.org')
    with self.assertRaises(error.InvalidArgumentError):
      udoc = await user.edit(DUMMY_ID, role=builtin.ROLE_ROOT)

  @base.wrap_coro
  async def test_set_role(self):
    udoc = await user.init(DUMMY_USERNAME)
    uid = udoc['_id']
    udoc = await user.set_role(uid, 0)
    self.assertEqual(udoc['role'], 0)
    with self.assertRaises(error.UserNotFoundError):
      await user.set_role(DUMMY_ID, 0)

  @base.wrap_coro
  async def test_set_role_by_username(self):
    udoc = await user.init(DUMMY_USERNAME)
    self.assertNotEqual(udoc['role'], builtin.ROLE_ROOT)
    udoc = await user.set_role_by_username(DUMMY_USERNAME, builtin.ROLE_ROOT)
    self.assertEqual(udoc['role'], builtin.ROLE_ROOT)
    with self.assertRaises(error.UserNotFoundError):
      await user.set_role_by_username(DUMMY_USERNAME,
                                      builtin.ROLE_USER, when_old_role=builtin.ROLE_ADMIN)
    udoc = await user.get(udoc['_id'])
    self.assertEqual(udoc['role'], builtin.ROLE_ROOT)
    with self.assertRaises(error.UserNotFoundError):
      await user.set_role_by_username(DUMMY_USERNAME2, builtin.ROLE_ROOT)

  @base.wrap_coro
  async def test_get_prefix_list(self):
    udoc = await user.init(DUMMY_USERNAME)
    udoc2 = await user.init(DUMMY_USERNAME2)
    udocs = await user.get_prefix_list('twd')
    self.assertEqual(len(udocs), 2)
    self.assertEqual(udocs[0], udoc)
    self.assertEqual(udocs[1], udoc2)

  @base.wrap_coro
  async def test_set_roles(self):
    udoc = await user.init(DUMMY_USERNAME)
    udoc2 = await user.init(DUMMY_USERNAME2)
    self.assertNotEqual(udoc['role'], builtin.ROLE_ROOT)
    self.assertNotEqual(udoc2['role'], builtin.ROLE_ROOT)
    uids = [udoc['_id'], udoc2['_id']]
    await user.set_roles(uids, builtin.ROLE_ROOT)
    udoc = await user.get(udoc['_id'])
    self.assertEqual(udoc['role'], builtin.ROLE_ROOT)
    udoc2 = await user.get(udoc2['_id'])
    self.assertEqual(udoc2['role'], builtin.ROLE_ROOT)
    await user.set_roles(uids, builtin.ROLE_USER, when_old_role=builtin.ROLE_ADMIN)
    udoc = await user.get(udoc['_id'])
    self.assertEqual(udoc['role'], builtin.ROLE_ROOT)
    udoc2 = await user.get(udoc2['_id'])
    self.assertEqual(udoc2['role'], builtin.ROLE_ROOT)
    udoc = await user.set_role(udoc['_id'], builtin.ROLE_ADMIN)
    await user.set_roles(uids, builtin.ROLE_USER, when_old_role=builtin.ROLE_ADMIN)
    udoc = await user.get(udoc['_id'])
    self.assertEqual(udoc['role'], builtin.ROLE_USER)
    udoc2 = await user.get(udoc2['_id'])
    self.assertEqual(udoc2['role'], builtin.ROLE_ROOT)

  @base.wrap_coro
  async def test_get_list_by_role(self):
    udoc = await user.init(DUMMY_USERNAME)
    udoc2 = await user.init(DUMMY_USERNAME2)
    uids = [udoc['_id'], udoc2['_id']]
    await user.set_roles(uids, builtin.ROLE_ROOT)
    udocs = await user.get_list_by_role(builtin.ROLE_ROOT)
    self.assertEqual(len(udocs), 2)
    self.assertEqual(udocs[0]['_id'], udoc['_id'])
    self.assertEqual(udocs[1]['_id'], udoc2['_id'])


if __name__ == '__main__':
  unittest.main()
