from er import app
from er import template
from er.model import builtin
from er.model import event
from er.model import registration
from er.handler import base
from er.util import pagination


@app.route('/', 'main')
class MainHandler(base.Handler):
  REGISTRATIONS_LIMIT = 20

  async def get(self):
    latest_edocs = await event.get_multi(end_at={'$gt': self.now}) \
                              .sort('begin_at', -1).limit(2).to_list()
    latest_rdocs = []
    for edoc in latest_edocs:
      rdoc = await registration.get_by_ids(self.user['_id'], edoc['_id'])
      latest_rdocs.append(rdoc)
    hottest_edocs = await event.get_multi().sort('num_view', -1).limit(2).to_list()
    hottest_rdocs = []
    for edoc in hottest_edocs:
      rdoc = await registration.get_by_ids(self.user['_id'], edoc['_id'])
      hottest_rdocs.append(rdoc)
    rdocs = await registration.get_multi_by_creator(self.user['_id']).limit(self.REGISTRATIONS_LIMIT).to_list()
    edict = await event.get_dict(set(rdoc['event_id'] for rdoc in rdocs))
    self.render('main.html', latest_edocs=latest_edocs,
                latest_rdocs=latest_rdocs,
                hottest_edocs=hottest_edocs,
                hottest_rdocs=hottest_rdocs,
                rdocs=rdocs,
                edict=edict)


@app.route('/slider', 'slider')
class SliderHandler(base.Handler):
  async def get(self):
    self.render('slider.html')
