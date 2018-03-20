from bson import objectid

from er import app
from er import error as ererror
from er import template
from er.model import builtin
from er.model import user
from er.model import message
from er.util import options
from er.util import misc
from er.util import pagination
from er.util import validator
from er.service import oauth
from er.handler import base


@app.route('/login', 'login')
@app.route('/login/{return_eid}', 'login_with_return_eid')
class LoginHandler(base.Handler):
  @base.get_argument
  @base.route_argument
  @base.sanitize
  async def get(self, code: str='', error: str='', return_eid: str='', **kwargs):
    if self.has_role(builtin.ROLE_USER):
      self.json_or_redirect(self.referer_or_main)
      return
    if not code and not error:
      self.json_or_redirect(
        oauth.get_auth_url(options.url_prefix + self.url))
    else:
      if error:
        raise ererror.OAuthDeniedError()
      assert bool(code)
      access_token = await oauth.get_access_token(code)
      rawdoc = await oauth.get_userinfo(access_token)
      udoc = await user.init(rawdoc['name'], rawdoc)
      await self.update_session(uid=udoc['_id'])
      if udoc['enable_at']:
        if return_eid:
          self.json_or_redirect(self.reverse_url('event_detail', eid=return_eid))
        else:
          self.json_or_redirect(self.reverse_url('main'))
      else:
        if return_eid:
          self.json_or_redirect(self.reverse_url('user_info') + '?return_eid=' + return_eid)
        else:
          self.json_or_redirect(self.reverse_url('user_info'))


@app.route('/logout', 'logout')
class UserLogoutHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER, require_enable=False)
  async def get(self):
    self.render('logout.html')

  @base.require_role(builtin.ROLE_USER, require_enable=False)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self):
    await self.delete_session()
    self.json_or_redirect(self.referer_or_main)


@app.route('/user/info', 'user_info')
class UserInfoHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER, require_enable=False)
  async def get(self):
    if not self.user['enable_at']:
      year = None
      clas = None
      try:
        bdoc = self.user['raw']['bachelor']
        year = self.user['raw']['bachelor']['year']
        if year != None:
          year = str(year)
          clas = self.user['raw']['bachelor']['classNumber']
      except KeyError:
        pass
      except ValueError:
        pass
      default_udoc = {
        'name': self.user['raw'].get('fullname', ''),
        'mail': self.user['raw'].get('email', ''),
        'student_id': year + '011' if year else '',
        'gender': '男',
        'birthday': self.user['raw'].get('birthdate', ''),
        'degree': '本科学位',
        'department': '计算机系',
        'class': '计{}{}'.format(year[-1], clas) if year else '计',
        'size': 'L',
        'mobile': self.user['raw'].get('mobile', ''),
        'room': '紫荆二号楼 '
      }
    else:
      default_udoc = {}
    self.render('user_info.html', default_udoc=default_udoc)

  @base.require_role(builtin.ROLE_USER, require_enable=False)
  @base.get_argument
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, name: str, mail: str, return_eid: str=''):
    pdict = await self.request.post()
    kwargs = dict((f.key, pdict.get(f.key, '')) for f in user.FIELDS.values())
    validator.check_fields_by_descriptor(kwargs, user.FIELDS)
    await user.edit(self.user['_id'], name=name, mail=mail, **kwargs)
    if return_eid:
      self.json_or_redirect(self.reverse_url('event_detail', eid=return_eid))
    else:
      self.json_or_redirect(self.referer_or_main)


@app.route('/user/message', 'user_message')
class UserMessageHandler(base.Handler):
  MESSAGES_PER_PAGE = 20

  @base.require_role(builtin.ROLE_USER, require_enable=False)
  @base.get_argument
  @base.sanitize
  async def get(self, unread_only: int=0, page: int=1):
    mdocs = message.get_by_receiver(self.user['_id'], unread_only=unread_only)
    mdocs, mpcount, _ = await pagination.paginate(mdocs, page, self.MESSAGES_PER_PAGE)
    udict = await user.get_dict(set(mdoc['sender_id'] for mdoc in mdocs))
    qs = 'unread_only={0}'.format(unread_only)
    self.render('user_message.html', page=page, mpcount=mpcount, qs=qs, mdocs=mdocs,
                unread_only=unread_only, udict=udict)


@app.route('/user/message/{mid}', 'user_message_detail')
class UserMessageDetailHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER, require_enable=False)
  @base.route_argument
  @base.sanitize
  async def get(self, mid: objectid.ObjectId):
    mdoc = await message.set_read(mid)
    udoc = await user.get(mdoc['sender_id'])
    self.num_unread = await message.get_by_receiver(self.user['_id'], unread_only=True).count()
    path_components = self.build_path(
        (self.translate('user_message'), self.reverse_url('user_message')),
        (mdoc['title'], None))
    self.render('user_message_detail.html', mid=mid, mdoc=mdoc, udoc=udoc,
                path_components=path_components,
                page_title=mdoc['title'])


@app.route('/user/search', 'user_search')
class UserSearchHandler(base.Handler):
  def modify_udoc(self, udict, key):
    udoc = udict[key]
    udict[key] = {'_id': udoc['_id'],
                  'username': udoc['username'],
                  'username_lower': udoc['username_lower'],
                  'gravatar_url': misc.gravatar_url(udoc.get('mail')),
                  'name': udoc['name']}

  @base.require_role(builtin.ROLE_USER)
  @base.get_argument
  @base.route_argument
  @base.sanitize
  async def get(self, q: str):
    udocs = await user.get_list_by_name(q)
    udocs.extend(await user.get_prefix_list(q))
    for i in range(len(udocs)):
      self.modify_udoc(udocs, i)
    self.json(udocs)
