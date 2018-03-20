from os import path

import jinja2
import jinja2.ext
import jinja2.runtime

import er
from er.service import staticmanifest
from er.util import json
from er.util import misc
from er.util import options


class Undefined(jinja2.runtime.Undefined):
  def __getitem__(self, _):
    return self

  if options.debug:
    __str__ = jinja2.runtime.Undefined.__call__


class Environment(jinja2.Environment):
  def __init__(self):
    super(Environment, self).__init__(
        loader=jinja2.FileSystemLoader(path.join(path.dirname(__file__), 'ui/templates')),
        extensions=[jinja2.ext.with_],
        auto_reload=options.debug,
        autoescape=True,
        trim_blocks=True,
        undefined=Undefined)
    globals()[self.__class__.__name__] = lambda: self  # singleton

    self.globals['er'] = er
    self.globals['static_url'] = lambda s: '/' + staticmanifest.get(s)
    self.globals['paginate'] = misc.paginate

    self.filters['nl2br'] = misc.nl2br
    self.filters['markdown'] = misc.markdown
    self.filters['json'] = json.encode
    self.filters['gravatar_url'] = misc.gravatar_url
    self.filters['format_size'] = misc.format_size
    self.filters['format_duration'] = misc.format_duration
    self.filters['base64_encode'] = misc.base64_encode
