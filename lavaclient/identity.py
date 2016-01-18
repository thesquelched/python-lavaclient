import six
import requests
import logging
from figgis import Config, Field, FiggisError
from dateutil.parser import parse as dateparse

from lavaclient.log import NullHandler
from lavaclient import constants
from lavaclient.error import AuthenticationError, AuthorizationError

if six.PY2:
    import urlparse
else:
    import urllib.parse as urlparse


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


class Token(Config):

    token = Field(six.text_type, key='id', required=True)
    expires = Field(dateparse, required=True)


class KeystoneAuth(object):

    def __init__(self, username, api_key=None, password=None, region=None,
                 auth_url=None):
        if auth_url is None:
            auth_url = constants.DEFAULT_AUTH_URL

        self.region = region.upper() if region is not None else None
        self.username = username
        self.api_key = api_key
        self.password = password

        parts = urlparse.urlparse(auth_url)
        token_url = urlparse.urlunparse((parts.scheme,
                                         parts.netloc,
                                         '/v2.0/tokens',
                                         None, None, None))
        self.token_url = token_url

    @property
    def request_data(self):
        if self.api_key:
            return {
                'auth': {
                    'RAX-KSKEY:apiKeyCredentials': {
                        'username': self.username,
                        'apiKey': self.api_key,
                    }
                }
            }
        else:
            return {
                'auth': {
                    'passwordCredentials': {
                        'username': self.username,
                        'password': self.password,
                    },
                    'RAX-AUTH:domain': {
                        'name': 'Rackspace',
                    },
                },
            }

    @property
    def request_headers(self):
        return {'Accept': 'application/json'}

    @property
    def auth_token(self):
        return self.token.token

    def parse_error_message(self, resp, default=None):
        try:
            data = resp.json()
            return six.next(iter(data.values())).get('message', default)
        except Exception:
            return default

    def authenticate(self, session):
        try:
            resp = session.post(self.token_url, json=self.request_data,
                                headers=self.request_headers)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            if exc.response.status_code == requests.codes.unauthorized:
                message = self.parse_error_message(exc.response,
                                                   'Invalid credentials')
                six.raise_from(AuthorizationError(message), exc)

            message = self.parse_error_message(exc.response,
                                               'Unable to authenticate')
            six.raise_from(AuthenticationError(message), exc)
        except requests.RequestException as exc:
            message = self.parse_error_message(exc.response,
                                               'Unable to authenticate')
            six.raise_from(AuthenticationError(message), exc)

        data = resp.json()['access']

        try:
            self.token = Token(data['token'])
        except FiggisError as exc:
            six.raise_from(
                AuthenticationError('Unable to parse authentication token'),
                exc)

        self.endpoint = self.parse_endpoint(data)

        return self

    def parse_endpoint(self, data):
        try:
            cbd = six.next(item for item in data['serviceCatalog']
                           if item['type'] == constants.CBD_SERVICE_TYPE and
                           item['name'] == constants.CBD_SERVICE_NAME)
            endpoint = six.next(item for item in cbd['endpoints']
                                if item['region'].upper() == self.region and
                                item.get('versionId') == '2')
        except StopIteration:
            return None

        return endpoint['publicURL']
