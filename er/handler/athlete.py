from bson import objectid

from er import app
from er import template
from er.model import builtin
from er.model import document
from er.util import pagination
from er.util import validator
from er.handler import base


@app.route('/athlete', 'athlete_main')
class AthleteMainHandler(base.Handler):
  DOCUMENTS_PER_PAGE = 20

  @base.get_argument
  @base.sanitize
  async def get(self, page: int=1):
    ddocs, dpcount, _ = await pagination.paginate(document.get_multi(document.TYPE_ATHLETE) \
                                                          .sort([('year', -1), ('_id', -1)]),
                                                  page, self.DOCUMENTS_PER_PAGE)
    self.render('athlete_main.html', ddocs=ddocs, page=page, qs='', dpcount=dpcount)


@app.route('/athlete/add', 'athlete_add')
class AthleteAddHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  async def get(self):
    self.render('athlete_edit.html')

  @base.require_role(builtin.ROLE_ADMIN)
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self):
    pdict = await self.request.post()
    fields = dict((f.key, pdict.get(f.key, '')) for f in document.ATHLETE_FIELDS.values())
    validator.check_fields_by_descriptor(fields, document.ATHLETE_FIELDS)
    did = await document.add(document.TYPE_ATHLETE, **fields)
    self.json_or_redirect(self.reverse_url('athlete_detail', did=did))


@app.route('/athlete/{did:\w{24}}', 'athlete_detail')
class AthleteDetailHandler(base.Handler):
  @base.route_argument
  @base.sanitize
  async def get(self, did: objectid.ObjectId):
    ddoc = await document.inc(did, document.TYPE_ATHLETE, num_view=1)
    images = list(filter(lambda s: bool(s), ddoc.get('images_text', '').split(',')))
    path_components = self.build_path(
      (self.translate('athlete_main'), self.reverse_url('athlete_main')),
      (ddoc['name'], None))
    self.render('athlete_detail.html', ddoc=ddoc, images=images,
                path_components=path_components, page_title=ddoc['name'])


@app.route('/athlete/{did}/edit', 'athlete_edit')
class AthleteEditHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.sanitize
  async def get(self, did: objectid.ObjectId):
    ddoc = await document.get(did, document.TYPE_ATHLETE)
    self.render('athlete_edit.html', ddoc=ddoc)

  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, did: objectid.ObjectId):
    pdict = await self.request.post()
    fields = dict((f.key, pdict.get(f.key, '')) for f in document.ATHLETE_FIELDS.values())
    validator.check_fields_by_descriptor(fields, document.ATHLETE_FIELDS)
    ddoc = await document.edit(did, document.TYPE_ATHLETE, **fields)
    self.json_or_redirect(self.reverse_url('athlete_detail', did=ddoc['_id']))


@app.route('/athlete/{did}/delete', 'athlete_delete')
class AthleteDeleteHandler(base.Handler):
  @base.require_role(builtin.ROLE_ADMIN)
  @base.route_argument
  @base.post_argument
  @base.require_csrf_token
  @base.sanitize
  async def post(self, did: objectid.ObjectId):
    ddoc = await document.get(did, document.TYPE_ATHLETE)
    await oplog.add(self.user['_id'], oplog.TYPE_DELETE_DOCUMENT, ddoc=ddoc)
    await document.delete(did, document.TYPE_ATHLETE)
    self.json_or_redirect(self.reverse_url('athlete_main'))
