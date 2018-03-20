from er.model import builtin


class Error(Exception):
  pass


class HashError(Error):
  pass


class InvalidStateError(Error):
  pass


class UserFacingError(Error):
  """Error which faces end user."""

  def to_dict(self):
    return {'name': self.__class__.__name__, 'args': self.args}

  @property
  def http_status(self):
    return 500

  @property
  def template_name(self):
    return 'error.html'

  @property
  def message(self):
    return '发生了一个错误。'


class BadRequestError(UserFacingError):
  @property
  def http_status(self):
    return 400


class ForbiddenError(UserFacingError):
  @property
  def http_status(self):
    return 403


class NotFoundError(UserFacingError):
  @property
  def http_status(self):
    return 404

  @property
  def message(self):
    return '路径 {0} 未找到。'


class ValidationError(ForbiddenError):
  @property
  def message(self):
    if len(self.args) == 2:
      return '字段 {0} 验证失败。{1}'
    elif len(self.args) == 3:
      return '字段 {0} 或 {1} 验证失败。{2}'
    return '字段 {0} 验证失败。'


class InvalidTokenError(ForbiddenError):
  pass


class PermissionError(ForbiddenError):
  @property
  def message(self):
    return '您没有所需的权限。'


class UserNotEnabledError(ForbiddenError):
  @property
  def message(self):
    return '您没有激活。请前往 个人信息 激活。'


class CsrfTokenError(ForbiddenError):
  pass


class InvalidOperationError(ForbiddenError):
  pass


class InvalidTokenDigestError(ForbiddenError):
  pass


class UnknownArgumentError(BadRequestError):
  @property
  def message(self):
    return '未知的参数 {0} 。'


class InvalidArgumentError(BadRequestError):
  @property
  def message(self):
    return '无效的参数 {0} 。'


class OAuthDeniedError(UserFacingError):
  @property
  def message(self):
    return 'OAuth 访问被拒绝。'


class EventStartedError(UserFacingError):
  @property
  def message(self):
    return '该赛事报名已经开始或者已截止，无法删除。'


class EventClosedError(UserFacingError):
  @property
  def message(self):
    return '该赛事报名还未开始或者已截止。'


class EventQuotaFulledError(UserFacingError):
  @property
  def message(self):
    return '该赛事报名已满。'


class UserNotFoundError(UserFacingError):
  @property
  def message(self):
    if len(self.args) == 2:
      return '用户 {0} 不存在。{1}'
    return '用户 {0} 不存在。'


class MessageNotFoundError(UserFacingError):
  @property
  def message(self):
    return '消息 {0} 不存在。'


class TeammateNumberBelowRangeError(UserFacingError):
  @property
  def message(self):
    return '队员人数不应少于{0}人。'


class TeammateNumberAboveRangeError(UserFacingError):
  @property
  def message(self):
    return '队员人数不应多于{0}人。'


class RegistrationNotFoundError(UserFacingError):
  @property
  def message(self):
    if len(self.args) == 2:
      return '{0} 对 {1} 提交的报名表不存在。'
    return '报名表 {0} 不存在。'


class DuplicateRegistrationError(UserFacingError):
  @property
  def message(self):
    return '不能对同一赛事发起多次报名。'


class DuplicateTeammateError(UserFacingError):
  @property
  def message(self):
    return '不能将队长同时添加为队员。'


class DuplicateTeamRegistrationError(UserFacingError):
  @property
  def message(self):
    return '该队员已在别的队伍报名。'


class EventNotFoundError(UserFacingError):
  @property
  def message(self):
    return '赛事 {0} 不存在。'


class RegistrationApprovedError(UserFacingError):
  @property
  def message(self):
    return '报名已通过审核，无法修改或取消。'


class DocumentNotFoundError(UserFacingError):
  @property
  def message(self):
    return '文档 {0} 不存在。'
