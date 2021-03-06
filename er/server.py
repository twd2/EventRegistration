import atexit
import logging
import logging.config
import os
import signal
import socket
import sys
import urllib.parse

from aiohttp import web
from er import app
from er.util import options

options.define('listen', default='http://127.0.0.1:8888', help='Server listening address.')
options.define('prefork', default=1, help='Number of prefork workers.')
options.define('log_format',
               default=('%(log_color)s[%(levelname).1s '
                        '%(asctime)s %(module)s:%(lineno)d]%(reset)s %(message)s'),
               help='Log format.')

_logger = logging.getLogger(__name__)


def main():
  logging.config.dictConfig({
    'version': 1,
    'handlers': {
      'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'colored',
      },
    },
    'formatters': {
      'colored': {
        '()': 'colorlog.ColoredFormatter',
        'format': options.log_format,
        'datefmt': '%y%m%d %H:%M:%S'
      }
    },
    'root': {
      'level': 'DEBUG' if options.debug else 'INFO',
      'handlers': ['console'],
    },
    'loggers': {
      'sockjs': {
        'level': 'WARNING',
      },
    },
    'disable_existing_loggers': False,
  })
  url = urllib.parse.urlparse(options.listen)
  if url.scheme == 'http':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    host, port_str = url.netloc.rsplit(':', 1)
    sock.bind((host, int(port_str)))
  elif url.scheme == 'unix':
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      os.remove(url.path)
    except FileNotFoundError:
      pass
    sock.bind(url.path)
  else:
    _logger.error('Invalid listening scheme %s', url.scheme)
    return 1
  for i in range(1, options.prefork):
    pid = os.fork()
    if not pid:
      break
    else:
      atexit.register(lambda: os.kill(pid, signal.SIGTERM))
  web.run_app(app.Application(), sock=sock, access_log=None)

if __name__ == '__main__':
  sys.exit(main())
