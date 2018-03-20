import unittest

from er.handler import base

ROLE_DUMMY = 1


class DummyHandler(object):
  def __init__(self):
    self.role_checked = None

  def check_role(self, role, require_enable=True):
    self.role_checked = role


class DecoratorTest(unittest.TestCase, DummyHandler):
  def setUp(self):
    DummyHandler.__init__(self)

  @base.require_role(ROLE_DUMMY)
  def assert_role_checked(self, role):
    self.assertEqual(self.role_checked, role)

  def test_require_role_func(self):
    self.assertIsNone(self.role_checked)
    self.assert_role_checked(ROLE_DUMMY)


if __name__ == '__main__':
  unittest.main()
