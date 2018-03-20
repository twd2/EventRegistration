from er import app
from er import template
from er.handler import base
from er.util import misc
from er.util import options
from er.util import qrcode


@app.route('/preview', 'preview')
class PreviewHandler(base.Handler):
  @base.post_argument
  @base.sanitize
  async def post(self, *, text: str):
    self.response.content_type = 'text/html'
    self.response.text = misc.markdown(text)


@app.route('/qrcode', 'qrcode')
class QrcodeHandler(base.Handler):
  @base.get_argument
  @base.sanitize
  async def get(self, a: str):
    data = qrcode.generate(options.url_prefix + a)
    await self.binary(data, 'image/png')
