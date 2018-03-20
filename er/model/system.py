from pymongo import ReturnDocument

from er import db
from er.util import argmethod


@argmethod.wrap
async def ensure_indexes():
  coll = db.coll('system')


if __name__ == '__main__':
  argmethod.invoke_by_args()
