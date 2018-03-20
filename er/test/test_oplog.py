import unittest
from bson import objectid

from er import error
from er.model import builtin
from er.model import oplog
from er.test import base


DUMMY_UID = objectid.ObjectId('f' * 24)


class Test(base.DatabaseTestCase):
  @base.wrap_coro
  async def test_add(self):
    await oplog.add(DUMMY_UID, oplog.TYPE_DELETE_EVENT, edoc={'dummy': 'dummy'})
    await oplog.add(DUMMY_UID, oplog.TYPE_DELETE_REGISTRATION, rdoc={'dummy': 'dummy'})


if __name__ == '__main__':
  unittest.main()
