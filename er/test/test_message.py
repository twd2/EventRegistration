import unittest
from bson import objectid

from er import error
from er.model import message
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)


class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_add(self):
    sender_id = objectid.ObjectId()
    receiver_id = objectid.ObjectId()
    title = 'whz'
    content = 'tai qiang le!'
    mid = await message.add(sender_id, receiver_id, title, content)
    mdoc = await message.get(mid)
    self.assertEqual(mid, mdoc['_id'])
    self.assertEqual(sender_id, mdoc['sender_id'])
    self.assertEqual(receiver_id, mdoc['receiver_id'])
    self.assertEqual(title, mdoc['title'])
    self.assertEqual(content, mdoc['content'])

  @base.wrap_coro
  async def test_get(self):
    with self.assertRaises(error.MessageNotFoundError):
      mdoc = await message.get(DUMMY_ID)

  @base.wrap_coro
  async def test_get_by_receiver(self):
    sender_id = objectid.ObjectId()
    receiver_id = objectid.ObjectId()
    title = 'whz'
    content = 'tai qiang le!'
    mid1 = await message.add(sender_id, receiver_id, title, content)
    mid2 = await message.add(sender_id, receiver_id, title, content)
    await message.set_read(mid1, True)
    mdocs1 = await message.get_by_receiver(receiver_id, unread_only=True).to_list()
    mdocs2 = await message.get_by_receiver(receiver_id, unread_only=False).to_list()
    self.assertEqual(1, len(mdocs1))
    self.assertEqual(mid2, mdocs1[0]['_id'])
    self.assertEqual(2, len(mdocs2))
    self.assertEqual(mid2, mdocs2[0]['_id'])
    self.assertEqual(mid1, mdocs2[1]['_id'])

  @base.wrap_coro
  async def test_set_read(self):
    with self.assertRaises(error.MessageNotFoundError):
      mdoc = await message.set_read(DUMMY_ID)

    sender_id = objectid.ObjectId()
    receiver_id = objectid.ObjectId()
    title = 'whz'
    content = 'tai qiang le!'
    mid = await message.add(sender_id, receiver_id, title, content)
    mdoc = await message.get(mid)
    self.assertEqual(False, mdoc['read'])
    mdoc = await message.set_read(mid, True)
    self.assertEqual(True, mdoc['read'])
    mdoc = await message.set_read(mid, False)
    self.assertEqual(False, mdoc['read'])


if __name__ == '__main__':
  unittest.main()
