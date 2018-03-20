import base64
import binascii
import functools
import hashlib
import os

from er import error
from er.util import argmethod


def _md5(s):
  return hashlib.md5(s.encode()).hexdigest()


def _sha1(s):
  return hashlib.sha1(s.encode()).hexdigest()


def _b64encode(s):
  return base64.b64encode(s.encode()).decode()


def _b64decode(s):
  return base64.b64decode(s.encode()).decode()


@argmethod.wrap
def gen_salt(byte_length: int=20):
  return binascii.hexlify(os.urandom(byte_length)).decode()


@argmethod.wrap
def gen_secret(byte_length: int=20):
  return _sha1(gen_salt(byte_length))


if __name__ == '__main__':
  argmethod.invoke_by_args()
