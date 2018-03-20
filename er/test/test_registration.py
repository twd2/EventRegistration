import unittest
from bson import objectid

from er import error
from er.model import registration
from er.test import base

DUMMY_ID = objectid.ObjectId('f' * 24)
DUMMY_ID1 = objectid.ObjectId('a' * 24)
DUMMY_ID2 = objectid.ObjectId('b' * 24)
DUMMY_ID3 = objectid.ObjectId('c' * 24)
DUMMY_REASON = 'wo zui qiang'
DUMMY_CONFIDENCE = '100 percent'
DUMMY_REPLY = 'bao ming cheng gong, nin zui qiang'

class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_check_status(self):
    with self.assertRaises(error.ValidationError):
      registration.check_status(100)

  @base.wrap_coro
  async def test_add(self):
    event_id = DUMMY_ID
    creator_id = DUMMY_ID
    forcer_id = DUMMY_ID
    fields_ = [{'name': 'reason', 'value': DUMMY_REASON}, {'name': 'confidence', 'value': DUMMY_CONFIDENCE}]
    status_ = registration.STATUS_APPROVED
    await registration.add(creator_id,
                           event_id,
                           forcer_id=forcer_id,
                           fields=fields_,
                           reply=DUMMY_REPLY,
                           status=status_)
    docs = await registration.get_multi_by_creator(creator_id).to_list()
    rdoc = docs[0]
    self.assertEqual(1, len(docs))
    self.assertEqual(creator_id, rdoc['creator_id'])
    self.assertEqual(event_id, rdoc['event_id'])
    self.assertEqual(forcer_id, rdoc['forcer_id'])
    self.assertEqual(DUMMY_REPLY, rdoc['reply'])
    self.assertEqual(registration.STATUS_APPROVED, rdoc['status'])
    self.assertEqual('reason', rdoc['fields'][0]['name'])
    self.assertEqual(DUMMY_REASON, rdoc['fields'][0]['value'])
    self.assertEqual('confidence', rdoc['fields'][1]['name'])
    self.assertEqual(DUMMY_CONFIDENCE, rdoc['fields'][1]['value'])
    with self.assertRaises(error.DuplicateRegistrationError):
      await registration.add(creator_id, event_id)

  @base.wrap_coro
  async def test_get(self):
    with self.assertRaises(error.RegistrationNotFoundError):
      doc = await registration.get(DUMMY_ID)

  @base.wrap_coro
  async def test_edit(self):
    creator_id_ = DUMMY_ID
    event_id_ = DUMMY_ID
    obj_id = await registration.add(creator_id_, event_id_)
    fields_ = [{'name': 'reason', 'value': DUMMY_REASON}, {'name': 'confidence', 'value': DUMMY_CONFIDENCE}]
    status_ = registration.STATUS_APPROVED
    rdoc = await registration.edit(obj_id,
                                   fields=fields_,
                                   reply=DUMMY_REPLY,
                                   status=status_,
                                   rank=5,
                                   result='1cm',
                                   team_ids=[])
    rrdoc = await registration.get(obj_id)
    self.assertEqual(creator_id_, rdoc['creator_id'])
    self.assertEqual(event_id_, rdoc['event_id'])
    self.assertEqual(DUMMY_REPLY, rdoc['reply'])
    self.assertEqual(registration.STATUS_APPROVED, rdoc['status'])
    self.assertEqual(5, rdoc['rank'])
    self.assertEqual('1cm', rdoc['result'])
    self.assertEqual('reason', rdoc['fields'][0]['name'])
    self.assertEqual(DUMMY_REASON, rdoc['fields'][0]['value'])
    self.assertEqual('confidence', rdoc['fields'][1]['name'])
    self.assertEqual(DUMMY_CONFIDENCE, rdoc['fields'][1]['value'])
    self.assertEqual(creator_id_, rrdoc['creator_id'])
    self.assertEqual(event_id_, rrdoc['event_id'])
    self.assertEqual(DUMMY_REPLY, rrdoc['reply'])
    self.assertEqual(registration.STATUS_APPROVED, rrdoc['status'])
    self.assertEqual(5, rrdoc['rank'])
    self.assertEqual('1cm', rrdoc['result'])
    self.assertEqual('reason', rdoc['fields'][0]['name'])
    self.assertEqual(DUMMY_REASON, rdoc['fields'][0]['value'])
    self.assertEqual('confidence', rdoc['fields'][1]['name'])
    self.assertEqual(DUMMY_CONFIDENCE, rdoc['fields'][1]['value'])
    with self.assertRaises(error.RegistrationNotFoundError):
      doc = await registration.edit(objectid.ObjectId(), reply=DUMMY_REPLY)
    with self.assertRaises(error.InvalidArgumentError):
      doc = await registration.edit(obj_id, creator_id=DUMMY_ID)
    with self.assertRaises(error.InvalidArgumentError):
      doc = await registration.edit(obj_id, event_id=DUMMY_ID)
    with self.assertRaises(error.InvalidArgumentError):
      doc = await registration.edit(obj_id, forcer_id=DUMMY_ID)

  @base.wrap_coro
  async def test_get_by_ids(self):
    creator_id_ = objectid.ObjectId()
    event_id_ = objectid.ObjectId()
    obj_id = await registration.add(creator_id_, event_id_)
    doc = await registration.get_by_ids(creator_id_, event_id_)
    self.assertEqual(obj_id, doc['_id'])
    self.assertEqual(await registration.get_by_ids(DUMMY_ID, DUMMY_ID), None)

  @base.wrap_coro
  async def test_get_multi_by_creator(self):
    obj_ids = []
    creator_id_ = DUMMY_ID
    event_id_ = DUMMY_ID
    event_id_2 = objectid.ObjectId()
    obj_id1 = await registration.add(creator_id_, event_id_)
    obj_ids.append(obj_id1)
    obj_id2 = await registration.add(creator_id_, event_id_2)
    obj_ids.append(obj_id2)
    docs = await registration.get_multi_by_creator(creator_id_).to_list()
    self.assertEqual(2, len(docs))
    self.assertIn(docs[0]['_id'], obj_ids)
    self.assertIn(docs[1]['_id'], obj_ids)

  @base.wrap_coro
  async def test_get_multi_by_event(self):
    obj_ids = []
    creator_id_ = DUMMY_ID
    event_id_ = DUMMY_ID
    creator_id_2 = objectid.ObjectId()
    obj_id1 = await registration.add(creator_id_, event_id_)
    obj_ids.append(obj_id1)
    obj_id2 = await registration.add(creator_id_2, event_id_)
    obj_ids.append(obj_id2)
    docs = await registration.get_multi_by_event(event_id_).to_list()
    self.assertEqual(2, len(docs))
    self.assertIn(docs[0]['_id'], obj_ids)
    self.assertIn(docs[1]['_id'], obj_ids)

  @base.wrap_coro
  async def test_delete(self):
    rid = await registration.add(DUMMY_ID, DUMMY_ID)
    rdoc = await registration.get(rid)
    await registration.delete(rid)
    with self.assertRaises(error.RegistrationNotFoundError):
      rdoc = await registration.get(rid)

  @base.wrap_coro
  async def test_review(self):
    obj_ids = []
    creator_id_ = DUMMY_ID
    event_id_ = DUMMY_ID
    creator_id_2 = objectid.ObjectId()
    obj_id1 = await registration.add(creator_id_, event_id_)
    obj_ids.append(obj_id1)
    obj_id2 = await registration.add(creator_id_2, event_id_)
    obj_ids.append(obj_id2)
    await registration.review(obj_ids, 1, 'hello world')

  @base.wrap_coro
  async def test_has_group(self):
    await registration.add(DUMMY_ID, DUMMY_ID, team_leader=DUMMY_ID, team_ids=[])
    rid = await registration.add(DUMMY_ID, DUMMY_ID1, team_leader=DUMMY_ID1, team_ids=[DUMMY_ID2])
    await registration.add(DUMMY_ID1, DUMMY_ID1, team_leader=DUMMY_ID, team_ids=[])
    self.assertTrue(await registration.has_group(DUMMY_ID, DUMMY_ID))
    self.assertFalse(await registration.has_group(DUMMY_ID, DUMMY_ID1))
    self.assertFalse(await registration.has_group(DUMMY_ID, DUMMY_ID2))
    self.assertFalse(await registration.has_group(DUMMY_ID, DUMMY_ID3))
    self.assertTrue(await registration.has_group(DUMMY_ID1, DUMMY_ID))
    self.assertTrue(await registration.has_group(DUMMY_ID1, DUMMY_ID1))
    self.assertTrue(await registration.has_group(DUMMY_ID1, DUMMY_ID2))
    self.assertFalse(await registration.has_group(DUMMY_ID1, DUMMY_ID3))
    self.assertTrue(await registration.has_group(DUMMY_ID1, DUMMY_ID, exc=rid))
    self.assertFalse(await registration.has_group(DUMMY_ID1, DUMMY_ID1, exc=rid))
    self.assertFalse(await registration.has_group(DUMMY_ID1, DUMMY_ID2, exc=rid))
    self.assertFalse(await registration.has_group(DUMMY_ID1, DUMMY_ID3, exc=rid))


if __name__ == '__main__':
  unittest.main()
