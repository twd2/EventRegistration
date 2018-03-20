import unittest
from bson import objectid

from er import error
from er.model import builtin
from er.model import token
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)
DUMMY_EXPIRE = 1000


class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_add_get(self):
    tid, tdoc = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tdoc2 = await token.get(tid, token.TYPE_SESSION)
    self.assertEqual(tdoc['_id'], tdoc2['_id'])
    self.assertEqual(tdoc['token_type'], tdoc2['token_type'])
    self.assertEqual(DUMMY_ID, tdoc2['uid'])

  @base.wrap_coro
  async def test_get_most_recent_session_by_uid(self):
    tid1, tdoc1 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tid2, tdoc2 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tdoc1 = await token.update(tid1, token.TYPE_SESSION, DUMMY_EXPIRE)
    tdoc = await token.get_most_recent_session_by_uid(DUMMY_ID)
    self.assertEqual(tdoc['_id'], tdoc1['_id'])

  @base.wrap_coro
  async def test_get_session_list_by_uid(self):
    tid1, tdoc1 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tid2, tdoc2 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tdocs = await token.get_session_list_by_uid(DUMMY_ID)
    self.assertEqual(len(tdocs), 2)
    self.assertEqual(tdocs[0]['_id'], tdoc1['_id'])
    self.assertEqual(tdocs[1]['_id'], tdoc2['_id'])

  @base.wrap_coro
  async def test_delete(self):
    tid, tdoc = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    succ = await token.delete(tid, token.TYPE_SESSION)
    self.assertTrue(succ)
    tdoc = await token.get(tid, token.TYPE_SESSION)
    self.assertEqual(tdoc, None)

  @base.wrap_coro
  async def test_delete_by_uid(self):
    tid1, tdoc1 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    tid2, tdoc2 = await token.add(token.TYPE_SESSION, DUMMY_EXPIRE, uid=DUMMY_ID)
    succ = await token.delete_by_uid(DUMMY_ID)
    self.assertTrue(succ)
    tdoc = await token.get(tid1, token.TYPE_SESSION)
    self.assertEqual(tdoc, None)
    tdoc = await token.get(tid2, token.TYPE_SESSION)
    self.assertEqual(tdoc, None)


if __name__ == '__main__':
  unittest.main()
