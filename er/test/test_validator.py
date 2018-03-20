import collections
import functools
import unittest

from er import error
from er.util import validator


class Test(unittest.TestCase):
  def test_mail(self):
    self.assertTrue(validator.is_mail('ex@example.com'))
    self.assertTrue(validator.is_mail('1+e-x@example.com'))
    self.assertTrue(validator.is_mail('example.net@example.com'))
    self.assertFalse(validator.is_mail('example:net@example.com'))
    self.assertFalse(validator.is_mail('ex@examplecom'))
    self.assertFalse(validator.is_mail('example.com'))
    self.assertFalse(validator.is_mail('examplecom'))
    self.assertFalse(validator.is_mail('1+e=x@example.com'))
    validator.check_mail('ex@example.com')
    with self.assertRaises(error.ValidationError):
      validator.check_mail('1+e=x@example.com')

  def test_name(self):
    self.assertTrue(validator.is_name('d'))
    self.assertTrue(validator.is_name('dummy_name'))
    self.assertTrue(validator.is_name('x' * 30))
    self.assertTrue(validator.is_name('江泽民'))
    self.assertFalse(validator.is_name(''))
    self.assertFalse(validator.is_name(' '))
    self.assertFalse(validator.is_name('g' * 501))
    self.assertFalse(validator.is_name('x' * 700000))
    validator.check_name('江泽民')
    with self.assertRaises(error.ValidationError):
      validator.check_name(' ')

  def test_event_name(self):
    self.assertTrue(validator.is_name('d'))
    self.assertTrue(validator.is_name('dummy_name'))
    self.assertTrue(validator.is_name('x' * 30))
    self.assertTrue(validator.is_name('江泽民'))
    self.assertFalse(validator.is_name(''))
    self.assertFalse(validator.is_name(' '))
    self.assertFalse(validator.is_name('g' * 501))
    self.assertFalse(validator.is_name('x' * 700000))
    validator.check_event_name('江泽民')
    with self.assertRaises(error.ValidationError):
      validator.check_event_name(' ')

  def test_title(self):
    self.assertTrue(validator.is_title('d'))
    self.assertTrue(validator.is_title('dummy_name'))
    self.assertTrue(validator.is_title('x' * 30))
    self.assertFalse(validator.is_title(''))
    self.assertFalse(validator.is_title('g' * 501))
    self.assertFalse(validator.is_title('x' * 700000))
    validator.check_title('dummy')
    with self.assertRaises(error.ValidationError):
      validator.check_title(' ')

  def test_content(self):
    self.assertTrue(validator.is_content('dummy_name'))
    self.assertTrue(validator.is_content('x' * 300))
    self.assertFalse(validator.is_content(''))
    self.assertTrue(validator.is_content('c'))
    self.assertFalse(validator.is_content('x' * 700000))
    validator.check_content('dummy')
    with self.assertRaises(error.ValidationError):
      validator.check_content(' ')

  def test_intro(self):
    self.assertTrue(validator.is_intro('d'))
    self.assertTrue(validator.is_intro('dummy_name'))
    self.assertTrue(validator.is_intro('x' * 300))
    self.assertFalse(validator.is_intro(''))
    self.assertFalse(validator.is_intro('g' * 5001))
    self.assertFalse(validator.is_intro('x' * 700000))
    validator.check_intro('dummy')
    with self.assertRaises(error.ValidationError):
      validator.check_intro(' ')

  def test_result(self):
    self.assertTrue(validator.is_result('d'))
    self.assertTrue(validator.is_result('dummy_name'))
    self.assertTrue(validator.is_result('x' * 300))
    self.assertTrue(validator.is_result(''))
    self.assertFalse(validator.is_result('g' * 501))
    self.assertFalse(validator.is_result('x' * 700000))
    validator.check_result('dummy')
    with self.assertRaises(error.ValidationError):
      validator.check_result('g' * 501)

  def test_rank(self):
    self.assertTrue(validator.is_rank(5))
    self.assertTrue(validator.is_rank(1))
    self.assertFalse(validator.is_rank(-1))
    self.assertTrue(validator.is_rank(0))
    validator.check_rank(6)
    with self.assertRaises(error.ValidationError):
      validator.check_rank(-1)

  def test_check_fields_by_descriptor(self):
    Field = functools.partial(
      collections.namedtuple('Field', ['key', 'name', 'length_min', 'length_max']),
      length_min=1, length_max=500)
    FIELDS = [Field('student_id', '学号'),
              Field('birthday', '生日', length_min=8, length_max=8)]
    FIELDS = collections.OrderedDict((f.key, f) for f in FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'dummy': 'dummy'}, FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'birthday': 'dummy'}, FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'birthday': ''}, FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'birthday': 'ggggggggg'}, FIELDS)
    validator.check_fields_by_descriptor({'birthday': '19260817'}, FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'student_id': ' '}, FIELDS)
    with self.assertRaises(error.ValidationError):
      validator.check_fields_by_descriptor({'student_id': '2' * 501}, FIELDS)
    validator.check_fields_by_descriptor({'student_id': '2015022222'}, FIELDS)

  def test_reply(self):
    self.assertTrue(validator.is_reply('d'))
    self.assertTrue(validator.is_reply('dummy_name'))
    self.assertTrue(validator.is_reply('x' * 300))
    self.assertTrue(validator.is_reply(''))
    self.assertFalse(validator.is_reply('g' * 5001))
    self.assertFalse(validator.is_reply('x' * 700000))
    validator.check_reply('dummy')
    with self.assertRaises(error.ValidationError):
      validator.check_reply('g' * 5001)

  def test_team_ids(self):
    with self.assertRaises(error.ValidationError):
      validator.check_team_ids([1, 2, 3])

  def test_fields(self):
    with self.assertRaises(error.ValidationError):
      validator.check_fields([{'key': '1', 'value': 'aaaaa'},
                              {'key': '2', 'value': 'dummy'},
                              {'key': '3', 'value': ''}])
    with self.assertRaises(error.ValidationError):
      validator.check_fields([{'key': '1', 'value': 'a' * 5001},
                              {'key': '2', 'value': 'dummy'},
                              {'key': '3', 'value': '1'}])


if __name__ == '__main__':
  unittest.main()
