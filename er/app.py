import asyncio
import logging
from os import path

import sockjs
from aiohttp import web

from er import db
from er import error
from er.service import mailer
from er.service import staticmanifest
from er.util import json
from er.util import locale
from er.util import options
from er.util import tools

options.define('debug', default=False, help='Enable debug mode.')
options.define('static', default=True, help='Serve static files.')
options.define('ip_header', default='', help='Header name for remote IP.')
options.define('session_expire_seconds', default=2592000,
               help='Expire time for sessions, in seconds.')
options.define('cookie_domain', default='', help='Cookie domain.')
options.define('cookie_secure', default=False, help='Enable secure cookie flag.')
options.define('url_prefix', default='http://127.0.0.1:8888', help='URL prefix.')

_logger = logging.getLogger(__name__)


class Application(web.Application):
  def __init__(self):
    super(Application, self).__init__(middlewares=[self.error_middleware],
                                      debug=options.debug)
    globals()[self.__class__.__name__] = lambda: self  # singleton

    static_path = path.join(path.dirname(__file__), '.uibuild')
    translation_path = path.join(path.dirname(__file__), 'locale')

    # Initialize components.
    staticmanifest.init(static_path)
    locale.load_translations(translation_path)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.init())
    loop.run_until_complete(asyncio.gather(tools.ensure_all_indexes()))
    mailer.init()

    # Load handlers.
    from er.handler import athlete
    from er.handler import team
    from er.handler import main
    from er.handler import user
    from er.handler import manage
    from er.handler import event
    from er.handler import registration
    from er.handler import misc

    if options.static:
      self.router.add_static('/', static_path, name='static')

  async def error_middleware(self, app, handler):
    async def middleware_handler(request):
      try:
        response = await handler(request)
        return response
      except web.HTTPNotFound:
        from er.handler import error
        return await error.NotFoundHandler(request)

    return middleware_handler


def route(url, name):
  def decorate(handler):
    handler.NAME = handler.NAME or name
    handler.TITLE = handler.TITLE or name
    Application().router.add_route('*', url, handler, name=name)
    return handler

  return decorate


def connection_route(prefix, name):
  def decorate(conn):
    async def handler(msg, session):
      try:
        if msg.tp == sockjs.MSG_OPEN:
          await session.prepare()
          await session.on_open()
        elif msg.tp == sockjs.MSG_MESSAGE:
          await session.on_message(**json.decode(msg.data))
        elif msg.tp == sockjs.MSG_CLOSED:
          await session.on_close()
      except error.UserFacingError as e:
        _logger.warning("Websocket user facing error: %s", repr(e))
        session.close(4000, {'error': e.to_dict()})

    class Manager(sockjs.SessionManager):
      def get(self, id, create=False, request=None):
        if id not in self and create:
          self[id] = self._add(conn(request, id, self.handler,
                                    timeout=self.timeout, loop=self.loop, debug=self.debug))
        return self[id]

    loop = asyncio.get_event_loop()
    sockjs.add_endpoint(Application(), handler, name=name, prefix=prefix,
                        manager=Manager(name, Application(), handler, loop))
    return conn

  return decorate
