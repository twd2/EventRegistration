import aiomongo
import functools

from er.util import options

options.define('db_host', default='localhost', help='Database hostname or IP address.')
options.define('db_name', default='erdb', help='Database name.')


async def init():
  global _client, _db
  _client = await aiomongo.create_client('mongodb://' + options.db_host)
  _db = _client.get_database(options.db_name)


@functools.lru_cache()
def coll(name):
  return aiomongo.Collection(_db, name)

