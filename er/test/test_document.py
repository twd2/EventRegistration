import datetime
import unittest

from bson import objectid

from er import error
from er.model import document
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)
DUMMY_TYPE = document.TYPE_TEAM + 1


class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_add(self):
    did = await document.add(DUMMY_TYPE)
    ddoc = await document.get(did, DUMMY_TYPE)
    self.assertEqual(ddoc['_id'], did)
    self.assertEqual(ddoc['type'], DUMMY_TYPE)

  @base.wrap_coro
  async def test_delete(self):
    did = await document.add(DUMMY_TYPE)
    ddoc = await document.get(did, DUMMY_TYPE)
    await document.delete(did, DUMMY_TYPE)
    with self.assertRaises(error.DocumentNotFoundError):
      ddoc = await document.get(did, DUMMY_TYPE)

  @base.wrap_coro
  async def test_inc(self):
    with self.assertRaises(error.DocumentNotFoundError):
      ddoc = await document.inc(DUMMY_ID, DUMMY_TYPE, num_view=1)
    did = await document.add(DUMMY_TYPE)
    ddoc = await document.get(did, DUMMY_TYPE)
    self.assertEqual(0, ddoc['num_view'])
    ddoc = await document.inc(did, DUMMY_TYPE, num_view=1)
    self.assertEqual(1, ddoc['num_view'])

  @base.wrap_coro
  async def test_get(self):
    with self.assertRaises(error.DocumentNotFoundError):
      ddoc = await document.get(DUMMY_ID, DUMMY_TYPE)

  @base.wrap_coro
  async def test_edit(self):
    with self.assertRaises(error.DocumentNotFoundError):
      ddoc = await document.edit(DUMMY_ID, DUMMY_TYPE, name='111')
    did = await document.add(DUMMY_TYPE, name='123')
    ddoc = await document.get(did, DUMMY_TYPE)
    self.assertEqual(ddoc['name'], '123')
    ddoc = await document.edit(did, DUMMY_TYPE, name='456')
    self.assertEqual(ddoc['name'], '456')
    ddoc = await document.get(did, DUMMY_TYPE)
    self.assertEqual(ddoc['name'], '456')

  @base.wrap_coro
  async def test_get_multi(self):
    did = await document.add(DUMMY_TYPE, name='123')
    did2 = await document.add(DUMMY_TYPE, name='456')
    ddocs = await document.get_multi(DUMMY_TYPE).sort('_id', 1).to_list()
    self.assertEqual(len(ddocs), 2)
    self.assertEqual(ddocs[0]['name'], '123')
    self.assertEqual(ddocs[1]['name'], '456')


if __name__ == '__main__':
  unittest.main()
