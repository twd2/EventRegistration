from bson import objectid

from er import app
from er import error
from er import template
from er.model import builtin
from er.model import user
from er.model import message
from er.handler import base


@app.route('/manage', 'manage_main')
class ManageMainHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  async def get(self):
    self.render('manage_main.html')


@app.route('/manage/admin', 'manage_admin')
class ManageAdminHandler(base.OperationHandler):
  @base.require_role(builtin.ROLE_ROOT)
  async def get(self):
    udocs = await user.get_list_by_role(builtin.ROLE_ADMIN)
    self.render('manage_admin.html', udocs=udocs)

  @base.require_role(builtin.ROLE_ROOT)
  @base.require_csrf_token
  @base.sanitize
  async def post_add(self, *, username: str):
    try:
      await user.set_role_by_username(username, builtin.ROLE_ADMIN,
                                      when_old_role=builtin.ROLE_USER)
    except error.UserNotFoundError:
      raise error.UserNotFoundError(username, '或者，他/她已经是管理员。') from None
    self.json_or_redirect(self.referer_or_main)

  @base.require_role(builtin.ROLE_ROOT)
  @base.require_csrf_token
  @base.sanitize
  async def post_remove(self, *, uid: objectid.ObjectId):
    uids = list(map(objectid.ObjectId, (await self.request.post()).getall('uid')))
    await user.set_roles(uids, builtin.ROLE_USER, when_old_role=builtin.ROLE_ADMIN)
    self.json_or_redirect(self.referer_or_main)


@app.route('/manage/message', 'manage_message')
class ManageMessageHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  async def get(self):
    self.render('manage_message.html')

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, username: str, title: str, content: str):
    udoc = await user.get_by_username(username)
    await message.add(self.user['_id'], udoc['_id'], title, content)
    self.json_or_redirect(self.referer_or_main)


@app.route('/manage/mail', 'manage_mail')
class ManageMailHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  async def get(self):
    self.render('manage_mail.html')

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, username: str, title: str, content: str):
    udoc = await user.get_by_username(username)
    await self.send_mail(udoc['mail'], title, 'admin_mail.html',
                         page_title=title, content=content)
    self.json_or_redirect(self.referer_or_main)
