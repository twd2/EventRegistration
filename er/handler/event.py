import datetime
import pytz

from bson import objectid

from er import app
from er import error
from er import template
from er.model import builtin
from er.model import user
from er.model import event
from er.model import oplog
from er.model import registration
from er.util import pagination
from er.handler import base


def csv_escape(s):
  if ',' not in s and '"' not in s:
    return s
  s = s.replace('"', '""')
  return '"' + s + '"'

async def generate_csv(self, eid, fields_filter=None):
  row_title = ['用户名', '姓名', *[f.name for f in user.FIELDS.values()], '报名时间', '审核状态']
  edoc = await event.get(eid)
  if edoc['is_group']:
    row_title.extend(['队长用户名', '队长姓名', '队员用户名', '队员姓名'])
  for field in edoc['fields']:
    row_title.append(field['name'])
  rows = [row_title]
  rdocs = await registration.get_multi_by_event(eid).to_list()
  udict = await user.get_dict(set(rdoc['creator_id'] for rdoc in rdocs))
  for rdoc in rdocs:
    udoc = udict[rdoc['creator_id']]
    fdict = dict((field['name'], field['value']) for field in rdoc['fields'])
    fields = [fdict.get(field['name'], '') for field in edoc['fields']]
    group_info = []
    if edoc['is_group']:
      team_ids = rdoc['team_ids']
      teammate_udict = await user.get_dict(team_ids)
      team_leader_udoc = await user.get(rdoc['team_leader'])
      group_info = [team_leader_udoc['username'], team_leader_udoc['name'],
                    ','.join(teammate_udict[team_id]['username'] for team_id in team_ids),
                    ','.join(teammate_udict[team_id]['name'] for team_id in team_ids)]
    row = [udoc['username'], udoc['name'],
           *[udoc[f.key] for f in user.FIELDS.values()],
           self.datetime_text(rdoc['_id'].generation_time),
           registration.STATUS_TEXTS[rdoc['status']],
           *group_info,
           *fields]
    rows.append(row)
  if fields_filter != None:
    rows = [[row[i] for i in fields_filter] for row in rows]
  csv_content = '\r\n'.join([','.join([csv_escape(c) for c in row]) for row in rows])
  data = '\uFEFF' + csv_content
  await self.binary(data.encode(), file_name='{}.csv'.format(edoc['name']))

@app.route('/event', 'event_main')
class EventMainHandler(base.Handler):
  EVENTS_PER_PAGE = 20

  @base.get_argument
  @base.sanitize
  async def get(self, page: int=1):
    edocs, epcount, _ = await pagination.paginate(event.get_multi().sort('_id', -1), page,
                                                  self.EVENTS_PER_PAGE)
    udict = await user.get_dict(set(edoc['creator_id'] for edoc in edocs))
    qs = ''
    self.render('event_main.html', page=page, epcount=epcount,
                qs=qs, edocs=edocs, udict=udict)


@app.route('/event/tag/{tag:[^/]*}', 'event_tag')
class EventTagHandler(base.Handler):
  EVENTS_PER_PAGE = 20

  @staticmethod
  def my_split(string, delim):
    return list(filter(lambda s: bool(s), map(lambda s: s.strip(), string.split(delim))))

  @staticmethod
  def build_query(query_string):
    tag_groups = EventTagHandler.my_split(query_string, ' ')
    if not tag_groups:
      return {}
    query = {'$or': []}
    for g in tag_groups:
      tags = EventTagHandler.my_split(g, ',')
      if not tags:
        continue
      sub_query = {'$and': []}
      for c in tags:
        sub_query['$and'].append({'tags': c})
      query['$or'].append(sub_query)
    return query

  @base.get_argument
  @base.route_argument
  @base.sanitize
  async def get(self, *, tag: str, page: int=1):
    query = EventTagHandler.build_query(tag)
    edocs, epcount, _ = await pagination.paginate(event.get_multi(**query).sort('_id', -1), page,
                                                  self.EVENTS_PER_PAGE)
    udict = await user.get_dict(set(edoc['creator_id'] for edoc in edocs))
    qs = ''
    page_title = tag or '所有赛事'
    path_components = self.build_path(
        (self.translate('event_main'), self.reverse_url('event_main')),
        (page_title, None))
    self.render('event_main.html', page=page, epcount=epcount,
                qs=qs, edocs=edocs, udict=udict, tag=tag,
                page_title=page_title, path_components=path_components)


@app.route('/event/{eid:\w{24}}', 'event_detail')
class EventDetailHandler(base.OperationHandler):
  REGISTRATIONS_PER_PAGE = 100
  RESULTS = 8

  @base.get_argument
  @base.route_argument
  @base.sanitize
  async def get(self, *, eid: objectid.ObjectId, page: int=1, page_approved: int=1):
    edoc = await event.inc(eid, num_view=1)
    begin_dt = pytz.utc.localize(edoc['begin_at']).astimezone(self.timezone)
    end_dt = pytz.utc.localize(edoc['end_at']).astimezone(self.timezone)
    fields = []
    if self.has_role(builtin.ROLE_USER):
      rdoc = await registration.get_by_ids(self.user['_id'], eid)
      if rdoc:
        rdict = {}
        for field in rdoc['fields']:
          rdict[field['name']] = field['value']
        for field in edoc['fields']:
          if field['name'] in rdict:
            fields.append({'name': field['name'], 'value': rdict[field['name']]})
          else:
            fields.append({'name': field['name']})
      else:
        for field in edoc['fields']:
          fields.append({'name': field['name']})
    else:
      rdoc = None
    if self.has_role(builtin.ROLE_ADMIN):
      rdocs, rpcount, _ = await pagination.paginate(
        registration.get_multi_by_event(eid), page, self.REGISTRATIONS_PER_PAGE)
      udict = await user.get_dict(set(rdoc['creator_id'] for rdoc in rdocs))
    else:
      rdocs = None
      rpcount = None
      udict = None
    qs = 'page_approved=' + str(page_approved)
    if self.has_role(builtin.ROLE_USER) and edoc['show_list']:
      rdocs_approved, rpcount_approved, _ = await pagination.paginate(
        registration.get_multi_by_event(eid, status=registration.STATUS_APPROVED),
        page_approved, self.REGISTRATIONS_PER_PAGE)
      udict_approved = await user.get_dict(set(rdoc['creator_id'] for rdoc in rdocs_approved))
    else:
      rdocs_approved = None
      rpcount_approved = None
      udict_approved = None
    qs_approved = 'page=' + str(page)
    result_rdocs = await registration.get_multi_by_event(eid, result={'$ne': ''}) \
                                     .sort('rank', 1).limit(self.RESULTS).to_list()
    result_udict = await user.get_dict(set(rdoc['creator_id'] for rdoc in result_rdocs))
    owner_udoc = await user.get(edoc['creator_id'])
    path_components = self.build_path(
        (self.translate('event_main'), self.reverse_url('event_main')),
        (edoc['name'], None))
    teammates = list()
    team_leader = self.user['username']
    team_leader_udoc = None
    if edoc['is_group'] and rdoc:
      team_ids = rdoc['team_ids']
      teammate_udict = await user.get_dict(team_ids)
      for team_id in team_ids:
        teammates.append(teammate_udict[team_id]['username'])
      team_leader_udoc = await user.get(rdoc['team_leader'])
      team_leader = team_leader_udoc['username']
    teammates = ','.join(teammates)
    self.render('event_detail.html', edoc=edoc, fields=fields, owner_udoc=owner_udoc,
                rdoc=rdoc, rdocs=rdocs, rpcount=rpcount, udict=udict, qs=qs,
                rdocs_approved=rdocs_approved, rpcount_approved=rpcount_approved,
                udict_approved=udict_approved, qs_approved=qs_approved,
                result_rdocs=result_rdocs, result_udict=result_udict,
                page_title=edoc['name'], page=page, page_approved=page_approved,
                path_components=path_components, teammates=teammates, team_leader=team_leader,
                team_leader_udoc=team_leader_udoc)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post_delete(self, *, eid: objectid.ObjectId):
    edoc = await event.get(eid)
    if edoc['begin_at'] <= self.now:
      raise error.EventStartedError(eid)
    await oplog.add(self.user['_id'], oplog.TYPE_DELETE_EVENT, edoc=edoc)
    await event.delete(eid)
    self.json_or_redirect(self.reverse_url('event_main'))


@app.route('/event/add', 'event_add')
class EventAddHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  async def get(self):
    self.render('event_edit.html')

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, name: str, intro: str,
                 begin_at_date: str, begin_at_time: str,
                 end_at_date: str, end_at_time: str,
                 place: str, time: str, register_limit: int,
                 tags: str, fields: str,
                 show_list: bool=False, is_group: bool=False,
                 member_lb: int=1, member_ub: int=1):
    try:
      begin_at = datetime.datetime.strptime(begin_at_date + ' ' + begin_at_time, '%Y-%m-%d %H:%M')
      begin_at = self.timezone.localize(begin_at).astimezone(pytz.utc).replace(tzinfo=None)
    except ValueError:
      raise error.ValidationError('开始日期', '开始时间', '格式不正确。')
    try:
      end_at = datetime.datetime.strptime(end_at_date + ' ' + end_at_time, '%Y-%m-%d %H:%M')
      end_at = self.timezone.localize(end_at).astimezone(pytz.utc).replace(tzinfo=None)
    except ValueError:
      raise error.ValidationError('结束日期', '结束时间', '格式不正确。')
    if tags:
      tags = tags.split(',')
    else:
      tags = []
    new_fields = []
    if fields:
      fields = fields.split(',')
      new_fields = []
      for field in fields:
        new_field = {}
        new_field['name'] = field
        new_field['type'] = event.TYPE_STRING
        new_fields.append(new_field)
    else:
      new_fields = []
    eid = await event.add(name, intro, self.user['_id'], begin_at, end_at,
                          place, time, register_limit,show_list, is_group,
                          member_lb, member_ub, tags, new_fields)
    self.json_or_redirect(self.reverse_url('event_detail', eid=eid))


@app.route('/event/{eid}/edit', 'event_edit')
class EventEditHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.sanitize
  async def get(self, *, eid: objectid.ObjectId):
    edoc = await event.get(eid)
    begin_dt = pytz.utc.localize(edoc['begin_at']).astimezone(self.timezone)
    end_dt = pytz.utc.localize(edoc['end_at']).astimezone(self.timezone)
    tags = edoc['tags']
    fields = edoc['fields']
    tags_text = ','.join(tags)
    fields_text = ','.join(field['name'] for field in fields)
    self.render('event_edit.html', edoc=edoc,
                begin_date_text=begin_dt.strftime('%Y-%m-%d'),
                begin_time_text=begin_dt.strftime('%H:%M'),
                end_date_text=end_dt.strftime('%Y-%m-%d'),
                end_time_text=end_dt.strftime('%H:%M'),
                tags_text=tags_text, fields_text=fields_text)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, eid: objectid.ObjectId, name: str,
                 intro: str, begin_at_date: str, begin_at_time: str,
                 end_at_date: str, end_at_time: str,
                 place: str, time: str, register_limit: int,
                 tags: str, fields: str,
                 show_list: bool=False, is_group: bool=False,
                 member_lb: int=1, member_ub: int=1):
    try:
      begin_at = datetime.datetime.strptime(begin_at_date + ' ' + begin_at_time, '%Y-%m-%d %H:%M')
      begin_at = self.timezone.localize(begin_at).astimezone(pytz.utc).replace(tzinfo=None)
    except ValueError:
      raise error.ValidationError('开始日期', '开始时间', '格式不正确。')
    try:
      end_at = datetime.datetime.strptime(end_at_date + ' ' + end_at_time, '%Y-%m-%d %H:%M')
      end_at = self.timezone.localize(end_at).astimezone(pytz.utc).replace(tzinfo=None)
    except ValueError:
      raise error.ValidationError('结束日期', '结束时间', '格式不正确。')
    if tags:
      tags = tags.split(',')
    else:
      tags=[]
    new_fields = []
    if fields:
      fields = fields.split(',')
      new_fields = []
      for field in fields:
        new_field = {}
        new_field['name'] = field
        new_field['type'] = event.TYPE_STRING
        new_fields.append(new_field)
    else:
      new_fields = []
    edoc = await event.edit(eid, name=name, intro=intro,
                            begin_at=begin_at, end_at=end_at,
                            place=place, time=time,
                            register_limit=register_limit,
                            show_list=show_list, is_group=is_group,
                            member_lb=member_lb, member_ub=member_ub,
                            tags=tags, fields=new_fields)
    self.json_or_redirect(self.reverse_url('event_detail', eid=eid))


@app.route('/event/{eid:\w{24}}/download', 'event_register_download')
class EventRegisterDownloadHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.sanitize
  async def get(self, *, eid: objectid.ObjectId):
    await generate_csv(self, eid)


@app.route('/event/{eid:\w{24}}/advanced', 'event_register_download_advanced')
class EventRegisterDownloadHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.sanitize
  async def get(self, *, eid: objectid.ObjectId):
    row_title = ['用户名', '姓名', *[f.name for f in user.FIELDS.values()],  '报名时间', '审核状态']
    edoc = await event.get(eid)
    if edoc['is_group']:
      row_title.extend(['队长用户名', '队长姓名', '队员用户名', '队员姓名'])
    for field in edoc['fields']:
      row_title.append(field['name'])
    path_components = self.build_path(
        (self.translate('event_main'), self.reverse_url('event_main')),
        (edoc['name'], self.reverse_url('event_detail', eid=edoc['_id'])),
        (self.translate('event_register_download_advanced'), None))
    self.render('event_register_download_advanced.html', eid=eid, row_title=row_title,
                edoc=edoc, path_components=path_components)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.route_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, *, eid: objectid.ObjectId, field: str=''):
    fields = (await self.request.post()).getall('field', [])
    field_filter = [int(field) - 1 for field in fields]
    await generate_csv(self, eid, field_filter)
