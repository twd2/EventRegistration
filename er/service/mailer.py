import asyncio
import aiosmtplib as asmtp
import logging

from email.mime import text

from er.util import argmethod
from er.util import options

options.define('smtp_host', default='', help='SMTP server')
options.define('smtp_port', default=465, help='SMTP server')
options.define('smtp_user', default='', help='SMTP username')
options.define('smtp_password', default='', help='SMTP password')
options.define('mail_from', default='', help='Mail from')

_logger = logging.getLogger(__name__)

_queue = None
_consumer = None


async def _consume(queue):
  while True:
    msg = await queue.get()
    _logger.info('Sending mail...')
    for i in range(3):
      if i != 0:
        _logger.warn('Retrying...')
      try:
        async with asmtp.SMTP_SSL(hostname=options.smtp_host, port=options.smtp_port) as server:
          await server.ehlo()
          await server.login(options.smtp_user, options.smtp_password)
          await server.sendmail(options.mail_from, msg['To'], msg.as_string())
        _logger.info('Sent.')
        break
      except Exception as e:
        _logger.error('Send mail error: %s', repr(e))
    queue.task_done()


async def _publish(queue, obj):
  await queue.put(obj)


def init():
  global _queue, _consumer
  _queue = asyncio.Queue()
  _consumer = asyncio.ensure_future(_consume(_queue))


@argmethod.wrap
async def send_mail(to: str, subject: str, content: str):
  msg = text.MIMEText(content, _subtype='html', _charset='UTF-8')
  msg['Subject'] = subject
  msg['From'] = options.mail_from
  msg['To'] = to
  await _publish(_queue, msg)


if __name__ == '__main__':
  argmethod.invoke_by_args()
