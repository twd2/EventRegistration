import re
from bson import objectid

from er import error


MAIL_RE = re.compile(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*')


def is_reply(s):
  return 0 <= len(s.strip()) <= 5000


def check_reply(s):
  if not is_reply(s):
    raise error.ValidationError('审核附言', '字数须介于0~5000之间。')


def is_field_value(s):
  return 0 < len(s.strip()) <= 5000


def check_team_ids(ss):
  for s in list(set(ss)):
    if not isinstance(s, objectid.ObjectId):
      raise error.ValidationError('团队成员', '非法的用户Id')


def check_fields(ss):
  for s in ss:
    if not is_field_value(str(s['value'])):
      raise error.ValidationError('附加字段', '内容须介于1~5000之间。')


def is_mail(s):
  return bool(MAIL_RE.fullmatch(s))


def check_mail(s):
  if not is_mail(s):
    raise error.ValidationError('电子邮件', '必须满足电子邮件的一般格式。')


def is_name(s):
  return 0 < len(s.strip()) <= 64


def check_name(s):
  if not is_name(s):
    raise error.ValidationError('姓名', '字数须介于1~64之间。')


def check_event_name(s):
  if not is_name(s):
    raise error.ValidationError('赛事名称', '字数须介于1~64之间。')


def is_title(s):
  return 0 < len(s.strip()) <= 64


def check_title(s):
  if not is_title(s):
    raise error.ValidationError('标题', '字数须介于1~64之间。')


def is_content(s):
  return isinstance(s, str) and 0 < len(s.strip()) < 65536


def check_content(s):
  if not is_content(s):
    raise error.ValidationError('内容', '字数须介于1~64K之间。')


def is_intro(s):
  return isinstance(s, str) and 0 < len(s.strip()) <= 5000


def check_intro(s):
  if not is_intro(s):
    raise error.ValidationError('简介', '字数须介于1~5000之间。')


def is_result(s):
  return isinstance(s, str) and 0 <= len(s) <= 500


def check_result(s):
  if not is_result(s):
    raise error.ValidationError('成绩', '成绩长度须介于0~500之间。')


def is_rank(i):
  return i >= 0


def check_rank(i):
  if not is_rank(i):
    raise error.ValidationError('名次', '名次须大于等于0。')


def check_fields_by_descriptor(fields, descriptor_dict):
  for k, v in fields.items():
    if k not in descriptor_dict:
      raise error.ValidationError(k, '未知的字段。')
    field = descriptor_dict[k]
    v = v.strip()
    if not field.length_min <= len(v) <= field.length_max:
      if field.length_min == field.length_max:
        raise error.ValidationError(field.name, '长度只能为{}。'.format(field.length_min))
      else:
        raise error.ValidationError(field.name,
                                    '长度需要介于{}~{}之间。'.format(field.length_min, field.length_max))
    fields[k] = v
