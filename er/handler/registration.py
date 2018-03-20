import asyncio

from bson import objectid

from er import app
from er import error
from er.model import builtin
from er.model import oplog
from er.model import registration
from er.model import event
from er.model import message
from er.util import pagination
from er.handler import base
from er.model import user


@app.route('/registration', 'register_main')
class RegisterMainHandler(base.Handler):
  REGISTRATIONS_PER_PAGE = 20

  @base.get_argument
  @base.sanitize
  async def get(self, page: int=1):
    rdocs, rpcount, _ = await pagination.paginate(
      registration.get_multi_by_creator(self.user['_id']), page, self.REGISTRATIONS_PER_PAGE)
    edict = await event.get_dict(set(rdoc['event_id'] for rdoc in rdocs))
    qs = ''
    self.render('register_main.html', page=page, rpcount=rpcount,
                qs=qs, rdocs=rdocs, edict=edict)


@app.route('/event/{eid:\w{24}}/register', 'register_add')
class RegisterAddHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, eid: objectid.ObjectId, field: str='', teammates: str='',
                 team_leader: str=''):
    edoc = await event.get(eid)
    if not edoc['begin_at'] <= self.now < edoc['end_at']:
      raise error.EventClosedError(edoc['_id'])
    fields = []
    for field, value in zip(edoc['fields'], (await self.request.post()).getall('field', [])):
      fields.append({'name': field['name'], 'value': value})
    edoc = await event.inc_limited(eid, 'num_register', edoc['register_limit'])
    if not edoc:
      raise error.EventQuotaFulledError(eid)
    if edoc['is_group']:
      if teammates:
        teammates = list(set(teammates.split(',')))
      else:
        teammates = list()
      if team_leader in teammates:
        raise error.DuplicateTeammateError
      if edoc['member_lb'] > (len(teammates) + 1):
        raise error.TeammateNumberBelowRangeError(edoc['member_lb'])
      elif (len(teammates) + 1) > edoc['member_ub']:
        raise error.TeammateNumberAboveRangeError(edoc['member_ub'])
      team_leader_uid = (await user.get_by_username(team_leader))['_id']
      has_group = await registration.has_group(edoc['_id'], team_leader_uid)
      if has_group:
        raise error.DuplicateTeamRegistrationError(team_leader)
      team_ids = list()
      teammate_udict = await user.get_dict_by_username(teammates)
      for teammate in teammates:
        if teammate not in teammate_udict:
          raise error.UserNotFoundError(teammate)
        uid = teammate_udict[teammate]['_id']
        # TODO: performance improve
        has_group = await registration.has_group(edoc['_id'], uid)
        if has_group:
          raise error.DuplicateTeamRegistrationError(teammate)
        team_ids.append(uid)
    else:
      team_ids = []
      team_leader_uid = None
    rid = await registration.add(self.user['_id'], eid, fields=fields,
                                 team_ids=team_ids, team_leader=team_leader_uid)
    self.json_or_redirect(self.reverse_url('register_detail', rid=rid))


@app.route('/event/{eid:\w{24}}/register_force', 'register_force')
class RegisterForceHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.sanitize
  async def get(self, *, eid: objectid.ObjectId):
    edoc = await event.get(eid)
    fields = []
    for field in edoc['fields']:
      fields.append({'name': field['name']})
    self.render('register_force.html', edoc=edoc, fields=fields)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, eid: objectid.ObjectId, username: str, field: str=''):
    udoc, edoc = await asyncio.gather(user.get_by_username(username), event.get(eid))
    fields = []
    for field, value in zip(edoc['fields'], (await self.request.post()).getall('field', [])):
      fields.append({'name': field['name'], 'value': value})
    edoc = await event.inc_limited(eid, 'num_register', edoc['register_limit'])
    if not edoc:
      raise error.EventQuotaFulledError(eid)
    rid = await registration.add(udoc['_id'], eid, fields=fields,
                                 forcer_id=self.user['_id'])
    self.json_or_redirect(self.reverse_url('register_detail', rid=rid))


@app.route('/registration/{rid:\w{24}}/delete', 'register_delete')
class RegisterDeleteHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, rid: objectid.ObjectId):
    rdoc = await registration.get(rid)
    if self.user['_id'] != rdoc['creator_id']:
      self.check_role(builtin.ROLE_ADMIN)
    edoc = await event.get(rdoc['event_id'])
    if not edoc['begin_at'] <= self.now < edoc['end_at']:
      raise error.EventClosedError(edoc['_id'])
    if rdoc['status'] == registration.STATUS_APPROVED:
      raise error.RegistrationApprovedError(rdoc['_id'])
    await oplog.add(self.user['_id'], oplog.TYPE_DELETE_REGISTRATION, rdoc=rdoc)
    await registration.delete(rid)
    await event.inc(edoc['_id'], num_register=-1)
    self.json_or_redirect(self.reverse_url('event_detail', eid=edoc['_id']))


@app.route('/registration/{rid:\w{24}}/edit', 'register_edit')
class RegisterEditHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER)
  @base.route_argument
  @base.sanitize
  async def get(self, *, rid: objectid.ObjectId):
    rdoc = await registration.get(rid)
    if self.user['_id'] != rdoc['creator_id']:
      self.check_role(builtin.ROLE_ADMIN)
      udoc = await user.get(rdoc['creator_id'])
    else:
      udoc = None
    edoc = await event.get(rdoc['event_id'])
    if not edoc['begin_at'] <= self.now < edoc['end_at']:
      raise error.EventClosedError(edoc['_id'])
    if rdoc['status'] == registration.STATUS_APPROVED:
      raise error.RegistrationApprovedError(rdoc['_id'])
    fields = []
    rdict = {}
    for field in rdoc['fields']:
      rdict[field['name']] = field['value']
    for field in edoc['fields']:
      if field['name'] in rdict:
        fields.append({'name': field['name'], 'value': rdict[field['name']]})
      else:
        fields.append({'name': field['name']})
    team_ids = rdoc['team_ids']
    teammates = list()
    team_leader = None
    if edoc['is_group']:
      teammate_udict = await user.get_dict(team_ids)
      for team_id in team_ids:
        teammates.append(teammate_udict[team_id]['username'])
      teammates = ','.join(teammates)
      team_leader = (await user.get(rdoc['team_leader']))['username']
    self.render('register_edit.html', edoc=edoc, fields=fields, udoc=udoc,
                teammates_text=teammates, team_leader_text=team_leader)

  @base.require_role(builtin.ROLE_USER)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, rid: objectid.ObjectId, field: str='', teammates: str='',
                 team_leader: str=''):
    rdoc = await registration.get(rid)
    if self.user['_id'] != rdoc['creator_id']:
      self.check_role(builtin.ROLE_ADMIN)
    edoc = await event.get(rdoc['event_id'])
    if not edoc['begin_at'] <= self.now < edoc['end_at']:
      raise error.EventClosedError(edoc['_id'])
    if rdoc['status'] == registration.STATUS_APPROVED:
      raise error.RegistrationApprovedError(rdoc['_id'])
    fields = []
    for field, value in zip(edoc['fields'], (await self.request.post()).getall('field', [])):
      fields.append({'name': field['name'], 'value': value})
    if edoc['is_group']:
      if teammates:
        teammates = list(set(teammates.split(',')))
      else:
        teammates = list()
      if team_leader in teammates:
        raise error.DuplicateTeammateError
      if edoc['member_lb'] > (len(teammates) + 1):
        raise error.TeammateNumberBelowRangeError(edoc['member_lb'])
      elif (len(teammates) + 1) > edoc['member_ub']:
        raise error.TeammateNumberAboveRangeError(edoc['member_ub'])
      team_leader_uid = (await user.get_by_username(team_leader))['_id']
      has_group = await registration.has_group(edoc['_id'], team_leader_uid, exc=rid)
      if has_group:
        raise error.DuplicateTeamRegistrationError(team_leader)
      team_ids = list()
      teammate_udict = await user.get_dict_by_username(teammates)
      for teammate in teammates:
        if teammate not in teammate_udict:
          raise error.UserNotFoundError(teammate)
        uid = teammate_udict[teammate]['_id']
        # TODO: performance improve
        has_group = await registration.has_group(edoc['_id'], uid, exc=rid)
        if has_group:
          raise error.DuplicateTeamRegistrationError(teammate)
        team_ids.append(uid)
    else:
      team_ids = []
      team_leader_uid = None
    await registration.edit(rid, fields=fields, status=registration.STATUS_PENDING,
                            team_ids=team_ids, team_leader=team_leader_uid)
    self.json_or_redirect(self.reverse_url('register_detail', rid=rid))


@app.route('/registration/{rid:\w{24}}', 'register_detail')
class RegisterDetailHandler(base.Handler):
  @base.require_role(builtin.ROLE_USER)
  @base.route_argument
  @base.sanitize
  async def get(self, *, rid: objectid.ObjectId):
    rdoc = await registration.get(rid)
    if self.user['_id'] != rdoc['creator_id']:
      self.check_role(builtin.ROLE_ADMIN)
    edoc, udoc = await asyncio.gather(event.get(rdoc['event_id']), user.get(rdoc['creator_id']))
    owner_udoc = await user.get(edoc['creator_id'])
    fields = []
    rdict = {}
    for field in rdoc['fields']:
      rdict[field['name']] = field['value']
    for field in edoc['fields']:
      if field['name'] in rdict:
        fields.append({'name': field['name'], 'value': rdict[field['name']]})
      else:
        fields.append({'name': field['name']})
    if edoc['is_group']:
      team_ids = rdoc['team_ids']
      teammates = list()
      teammate_udict = await user.get_dict(team_ids)
      for team_id in team_ids:
        teammates.append(teammate_udict[team_id]['username'])
      teammates = ','.join(teammates)
      team_leader_udoc = await user.get(rdoc['team_leader'])
    else:
      teammates = []
      team_leader_udoc = None
    path_components = self.build_path(
        (self.translate('event_main'), self.reverse_url('event_main')),
        (edoc['name'], self.reverse_url('event_detail', eid=edoc['_id'])),
        (self.translate('event_detail'), None))
    self.render('register_detail.html', edoc=edoc, rdoc=rdoc, udoc=udoc, owner_udoc=owner_udoc,
                fields=fields, teammates=teammates, team_leader_udoc=team_leader_udoc,
                page_title=edoc['name'], path_components=path_components)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, rid: objectid.ObjectId, result: str='', rank: int):
    await registration.edit(rid, result=result, rank=rank)
    self.json_or_redirect(self.referer_or_main)


@app.route('/registration/review', 'register_review')
class RegisterReviewHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, rid: objectid.ObjectId=None, reply: str, status: int):
    rids = (await self.request.post()).getall('rid', [])
    rids = list(set(map(objectid.ObjectId, rids)))
    edoc = None
    await registration.review(rids, status, reply)
    rdocs = await registration.get_multi(_id={'$in': rids}).to_list()
    udict = await user.get_dict(set(rdoc['creator_id'] for rdoc in rdocs))
    for rdoc in rdocs:
      udoc = udict[rdoc['creator_id']]
      if not edoc:
        edoc = await event.get(rdoc['event_id'])
      if status == registration.STATUS_APPROVED:
        title = '恭喜，您的报名已通过审核'
        content = '您于 {} 报名的比赛 {} 已通过审核！'.format(
          self.datetime_text(rdoc['_id'].generation_time), edoc['name'])
      else:
        title = '很抱歉，您的报名未通过审核'
        content = '您于 {} 报名的比赛 {} 未通过审核。'.format(
          self.datetime_text(rdoc['_id'].generation_time), edoc['name'])
      if reply:
        content += '\n\n管理员回复：\n\n' + reply
      await asyncio.gather(self.send_mail(udoc['mail'], title, 'result_mail.html',
                                          status=status, page_title=title,
                                          reply=reply, rdoc=rdoc, edoc=edoc),
                           message.add(self.user['_id'], udoc['_id'], title, content))
    if len(rids) == 1:
      self.json_or_redirect(self.reverse_url('register_detail', rid=rids[0]))
    else:
      self.json_or_redirect(self.referer_or_main)

