import unittest

from er.util import pwhash


class Test(unittest.TestCase):
  def test_gen_salt(self):
    salt1 = pwhash.gen_salt()
    self.assertEqual(len(salt1), 40)
    salt2 = pwhash.gen_salt()
    self.assertNotEqual(salt1, salt2)
    salt3 = pwhash.gen_salt(16)
    self.assertEqual(len(salt3), 32)


if __name__ == '__main__':
  unittest.main()
