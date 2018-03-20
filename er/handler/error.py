from er import error
from er.handler import base


class NotFoundHandler(base.Handler):
  async def get(self):
    raise error.NotFoundError(self.url)
