import collections
import datetime
import functools
import itertools

from er.util import version


# Roles.
ROLE_ROOT = 0
ROLE_ADMIN = 100
ROLE_USER = 1000
ROLE_GUEST = 10000


UID_GUEST = 1
USERNAME_GUEST = 'guest'
USER_GUEST = {
  '_id': UID_GUEST,
  'username': USERNAME_GUEST,
  'role': ROLE_GUEST,
  'name': '游客',
  'mail': 'guest@example.org',
  'enable_at': None
}

# Footer extra HTMLs.
FOOTER_EXTRA_HTMLS = ['© 2017 - 2019 mfmfmf team', '<a href="https://github.com/twd2/EventRegistration" target="_blank">Fork me on GitHub</a>', version.get()]
