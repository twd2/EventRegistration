import accept
import asyncio
import calendar
import datetime
import functools
import hmac
import logging
import markupsafe
import pytz
import sockjs
from aiohttp import web
from email import utils

from er import app
from er import error
from er import template
from er.model import builtin
from er.model import token
from er.model import user
from er.model import message
from er.service import mailer
from er.util import json
from er.util import locale
from er.util import options

_logger = logging.getLogger(__name__)


class HandlerBase:
  NAME = None
  TITLE = None

  async def prepare(self):
    self.now = datetime.datetime.utcnow()
    self.translate = locale.get_translate(options.default_locale)  # Default translate for errors.
    self.session = await self.update_session()
    if 'uid' in self.session:
      uid = self.session['uid']
      self.user = await user.get(uid)
      self.num_unread = await message.get_by_receiver(uid, unread_only=True).count()
    else:
      self.user = builtin.USER_GUEST
    self.view_lang = 'zh_CN' # TODO(twd2)
    # TODO(twd2): UnknownTimeZoneError
    self.timezone = pytz.timezone('Asia/Shanghai')
    self.translate = locale.get_translate(self.view_lang)
    self.datetime_span = functools.partial(_datetime_span, timezone=self.timezone)
    self.datetime_text = functools.partial(_datetime_text, timezone=self.timezone)
    self.datetime_stamp = _datetime_stamp
    self.reverse_url = _reverse_url
    self.build_path = _build_path

  def has_role(self, role, require_enable=True):
    if require_enable and not self.is_enabled():
      return False
    return self.user['role'] <= role

  def check_role(self, role, require_enable=True):
    if not self.has_role(role, require_enable=False):
      raise error.PermissionError(role)
    if require_enable and not self.is_enabled():
      raise error.UserNotEnabledError()

  def is_enabled(self):
    return bool(self.user['enable_at'])

  def check_enable(self):
    if not self.is_enabled():
      raise error.UserNotEnabledError()

  async def update_session(self, **kwargs):
    """Update or create session if necessary.

    If 'sid' in cookie, the 'expire_at' field is updated.
    If 'sid' not in cookie, only create when there is extra data.

    Args:
      new_saved: use saved session on creation.
      kwargs: extra data.

    Returns:
      The session document.
    """
    (sid,), session = map(self.request.cookies.get, ['sid']), None
    token_type = token.TYPE_SESSION
    session_expire_seconds = options.session_expire_seconds
    if sid:
      session = await token.update(sid, token_type, session_expire_seconds,
                                   **{**kwargs,
                                      'update_ip': self.remote_ip,
                                      'update_ua': self.request.headers.get('User-Agent')})
    if kwargs and not session:
      sid, session = await token.add(token_type, session_expire_seconds,
                                     **{**kwargs,
                                        'create_ip': self.remote_ip,
                                        'create_ua': self.request.headers.get('User-Agent')})
    if session:
      cookie_kwargs = {'domain': options.cookie_domain,
                       'secure': options.cookie_secure,
                       'httponly': True}
      timestamp = calendar.timegm(session['expire_at'].utctimetuple())
      cookie_kwargs['expires'] = utils.formatdate(timestamp, usegmt=True)
      cookie_kwargs['max_age'] = session_expire_seconds
      self.response.set_cookie('sid', sid, **cookie_kwargs)
    else:
      self.clear_cookies('sid')
    return session or {}

  async def delete_session(self):
    sid, = map(self.request.cookies.get, ['sid'])
    if sid:
      await token.delete(sid, token.TYPE_SESSION)
    self.clear_cookies('sid')

  def clear_cookies(self, *names):
    for name in names:
      if name in self.request.cookies:
        self.response.set_cookie(name, '',
                                 expires=utils.formatdate(0, usegmt=True),
                                 domain=options.cookie_domain,
                                 secure=options.cookie_secure,
                                 httponly=True)

  @property
  def remote_ip(self):
    if options.ip_header:
      return self.request.headers.get(options.ip_header)
    else:
      return self.request.transport.get_extra_info('peername')[0]

  @property
  def csrf_token(self):
    if self.session:
      return _get_csrf_token(self.session['_id'])
    else:
      return ''

  def render_html(self, template_name, **kwargs):
    kwargs['handler'] = self
    if '_' not in kwargs:
      kwargs['_'] = self.translate
    if 'page_name' not in kwargs:
      kwargs['page_name'] = self.NAME
    if 'page_title' not in kwargs:
      kwargs['page_title'] = self.translate(self.TITLE)
    if 'path_components' not in kwargs:
      kwargs['path_components'] = self.build_path((self.translate(self.NAME), None))
    kwargs['reverse_url'] = self.reverse_url
    kwargs['datetime_span'] = self.datetime_span
    return template.Environment().get_template(template_name).render(kwargs)

  def render_title(self, page_title=None):
    if not page_title:
      page_title = self.translate(self.TITLE)
    page_title += ' - ' + self.translate('赛事报名')
    return page_title

  async def send_mail(self, mail, title, template_name, **kwargs):
    content = self.render_html(template_name, url_prefix=options.url_prefix,
                               **kwargs)
    translate = self.translate
    if '_' in kwargs:
      translate = kwargs['_']
    await mailer.send_mail(mail, '{} - {}'.format(translate(title), translate('赛事报名')), content)


class Handler(web.View, HandlerBase):
  @asyncio.coroutine
  def __iter__(self):
    try:
      self.response = web.Response()
      yield from HandlerBase.prepare(self)
      yield from super(Handler, self).__iter__()
    except asyncio.CancelledError:
      raise
    except error.UserFacingError as e:
      self.response.set_status(e.http_status, None)
      if isinstance(e, error.PermissionError):
        e.args = (self.translate(e.args[0]), *e.args[1:])
      if self.prefer_json:
        self.response.content_type = 'application/json'
        message = self.translate(e.message).format(*e.args)
        self.response.text = json.encode({'error': {**e.to_dict(), 'message': message}})
      else:
        self.render(e.template_name, error=e,
                    page_name='error', page_title=self.translate('error'),
                    path_components=self.build_path((self.translate('error'), None)))
      uid = self.user['_id'] if hasattr(self, 'user') else None
      _logger.warning('User facing error by %s %s %s: %s', self.url, self.remote_ip, uid, repr(e))
    except Exception as e:
      uid = self.user['_id'] if hasattr(self, 'user') else None
      _logger.error('System error by %s %s %s: %s', self.url, self.remote_ip, uid, repr(e))
      raise
    return self.response

  def render(self, template_name, **kwargs):
    self.response.content_type = 'text/html'
    self.response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate')
    self.response.headers.add('Pragma', 'no-cache')
    self.response.text = self.render_html(template_name, **kwargs)

  def json(self, obj):
    self.response.content_type = 'application/json'
    self.response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate')
    self.response.headers.add('Pragma', 'no-cache')
    self.response.text = json.encode(obj)

  async def binary(self, data, content_type='application/octet-stream', file_name=None):
    self.response = web.StreamResponse()
    self.response.content_length = len(data)
    self.response.content_type = content_type
    if file_name:
      for char in '/<>:\"\'\\|?* ':
        file_name = file_name.replace(char, '')
      self.response.headers.add('Content-Disposition',
                                'attachment; filename="{}"'.format(file_name))
    await self.response.prepare(self.request)
    self.response.write(data)

  @property
  def prefer_json(self):
    for d in accept.parse(self.request.headers.get('Accept')):
      if d.media_type == 'application/json':
        return True
      elif d.media_type == 'text/html' or d.all_types:
        return False
    return False

  @property
  def url(self):
    return self.request.path

  @property
  def referer_or_main(self):
    return self.request.headers.get('referer') or self.reverse_url('main')

  def redirect(self, redirect_url):
    self.response.set_status(web.HTTPFound.status_code, None)
    self.response.headers['Location'] = redirect_url

  def json_or_redirect(self, redirect_url, **kwargs):
    if self.prefer_json:
      self.json(kwargs)
    else:
      self.redirect(redirect_url)

  def json_or_render(self, template_name, **kwargs):
    if self.prefer_json:
      self.json(kwargs)
    else:
      self.render(template_name, **kwargs)

  @property
  def ui_context(self):
    return {'csrf_token': self.csrf_token,
            'url_prefix': options.url_prefix}

  @property
  def user_context(self):
    return {'uid': self.user['_id']}


class OperationHandler(Handler):
  DEFAULT_OPERATION = 'default'

  async def post(self):
    arguments = (await self.request.post()).copy()
    operation = arguments.pop('operation', self.DEFAULT_OPERATION)
    try:
      method = getattr(self, 'post_' + operation)
    except AttributeError:
      raise error.InvalidOperationError(operation) from None
    await method(**arguments)


class Connection(sockjs.Session, HandlerBase):
  def __init__(self, request, *args, **kwargs):
    super(Connection, self).__init__(*args, **kwargs)
    self.request = request
    self.response = web.Response()  # dummy response

  async def on_open(self):
    pass

  async def on_message(self, **kwargs):
    pass

  async def on_close(self):
    pass

  def send(self, **kwargs):
    super(Connection, self).send(json.encode(kwargs))


@functools.lru_cache()
def _get_csrf_token(session_id_binary):
  return hmac.new(b'csrf_token', session_id_binary, 'sha256').hexdigest()


@functools.lru_cache()
def _reverse_url(name, **kwargs):
  if kwargs:
    return app.Application().router[name].url(parts=kwargs)
  else:
    return app.Application().router[name].url()


@functools.lru_cache()
def _build_path(*args):
  return [('赛事报名', _reverse_url('main')), *args]


@functools.lru_cache()
def _datetime_span(dt, relative=True, format='%Y-%m-%d %H:%M:%S', timezone=pytz.utc):
  if not dt.tzinfo:
    dt = dt.replace(tzinfo=pytz.utc)
  return markupsafe.Markup(
      '<span class="time{0}" data-timestamp="{1}">{2}</span>'.format(
          ' relative' if relative else '',
          calendar.timegm(dt.utctimetuple()),
          dt.astimezone(timezone).strftime(format)))


@functools.lru_cache()
def _datetime_text(dt, format='%Y-%m-%d %H:%M:%S', timezone=pytz.utc):
  if not dt.tzinfo:
    dt = dt.replace(tzinfo=pytz.utc)
  return dt.astimezone(timezone).strftime(format)


@functools.lru_cache()
def _datetime_stamp(dt):
  if not dt.tzinfo:
    dt = dt.replace(tzinfo=pytz.utc)
  return calendar.timegm(dt.utctimetuple())


# Decorators
def require_role(role, require_enable=True):
  def decorate(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      self.check_role(role, require_enable)
      return func(self, *args, **kwargs)

    return wrapper

  return decorate


def require_csrf_token(func):
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    if self.csrf_token and self.csrf_token != kwargs.pop('csrf_token', ''):
      raise error.CsrfTokenError()
    return func(self, *args, **kwargs)

  return wrapper


def route_argument(func):
  @functools.wraps(func)
  def wrapped(self, **kwargs):
    return func(self, **kwargs, **self.request.match_info)

  return wrapped


def get_argument(func):
  @functools.wraps(func)
  def wrapped(self, **kwargs):
    return func(self, **kwargs, **self.request.query)

  return wrapped


def post_argument(coro):
  @functools.wraps(coro)
  async def wrapped(self, **kwargs):
    return await coro(self, **kwargs, **await self.request.post())

  return wrapped


def sanitize(func):
  @functools.wraps(func)
  def wrapped(self, **kwargs):
    kwargs_sanitized = {}
    for key, value in kwargs.items():
      try:
        kwargs_sanitized[key] = func.__annotations__[key](value)
      except KeyError:
        pass
      except Exception:
        raise error.InvalidArgumentError(key)
    return func(self, **kwargs_sanitized)

  return wrapped
