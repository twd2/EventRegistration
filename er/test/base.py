import asyncio
import functools
import os
import unittest

import pymongo

from er import db
from er.service import event
from er.util import options
from er.util import tools

wait = asyncio.get_event_loop().run_until_complete


class DatabaseTestCase(unittest.TestCase):
  def setUp(self):
    db._client = None
    db._db = None
    db.coll.cache_clear()
    options.db_name = 'unittest_' + str(os.getpid())
    wait(db.init())
    wait(tools.ensure_all_indexes())

  def tearDown(self):
    db._client.close()
    # wait(db._client.wait_closed())
    pymongo.MongoClient(options.db_host).drop_database(options.db_name)


def wrap_coro(coro):
  @functools.wraps(coro)
  def wrapped(*args, **kwargs):
    wait(coro(*args, **kwargs))

  return wrapped
