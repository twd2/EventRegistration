import aiohttp
from email.mime import text
from urllib import parse

from er.util import argmethod
from er.util import options
from er.util import json

options.define('oauth_host', default='https://accounts.net9.org', help='OAuth server')
options.define('oauth_id', default='', help='OAuth client id')
options.define('oauth_secret', default='', help='OAuth client secret')


@argmethod.wrap
def get_auth_url(redirect: str):
  return options.oauth_host + '/api/authorize?' + parse.urlencode({
    'client_id': options.oauth_id,
    'redirect_uri': redirect})


@argmethod.wrap
async def get_access_token(code: str):
  url = options.oauth_host + '/api/access_token'
  data = {'client_id': options.oauth_id,
          'client_secret': options.oauth_secret,
          'code': code}
  async with aiohttp.ClientSession() as session:
    async with session.post(url, data=data) as res:
      doc = json.decode(await res.text())
      return doc['access_token']


@argmethod.wrap
async def get_userinfo(access_token: str):
  url = options.oauth_host + '/api/userinfo?' + parse.urlencode({
    'access_token': access_token})
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as res:
      doc = json.decode(await res.text())
      rawdoc = doc['user']
      del rawdoc['password'] # Oh my god.
      rawdoc['access_token'] = access_token
      return rawdoc


if __name__ == '__main__':
  argmethod.invoke_by_args()
