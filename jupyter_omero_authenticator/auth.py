from jupyterhub.auth import Authenticator
from jupyterhub.handlers.base import BaseHandler
from tornado import gen
from tornado.escape import url_escape
from tornado.httputil import url_concat
from traitlets import Bool, List, Unicode
import omero.clients
from omero.rtypes import unwrap


class OmeroLoginHandler(BaseHandler):
    """Render the login page."""

    def initialize(self, omero_servers):
        self.omero_servers = omero_servers

    def _render(self, login_error=None, server=None, username=None):
        return self.render_template(
            'omero_authenticator/omerologin.html',
            omero_servers=self.omero_servers,
            next=url_escape(self.get_argument('next', default='')),
            server=server,
            username=username,
            login_error=login_error,
            login_url=self.settings['login_url'],
            authenticator_login_url=url_concat(
                self.authenticator.login_url(self.hub.base_url),
                {'next': self.get_argument('next', '')},
            ),
        )

    async def get(self):
        self.statsd.incr('login.request')
        user = self.current_user
        if user:
            # set new login cookie
            # because single-user cookie may have been cleared or incorrect
            self.set_login_cookie(user)
            self.redirect(self.get_next_url(user), permanent=False)
        else:
            server = self.get_argument('server', default='')
            username = self.get_argument('username', default='')
            self.finish(self._render(server=server, username=username))

    async def post(self):
        # parse the arguments dict
        data = {}
        for arg in self.request.arguments:
            data[arg] = self.get_argument(arg, strip=False)

        auth_timer = self.statsd.timer('login.authenticate').start()
        user = await self.login_user(data)
        auth_timer.stop(send=False)

        if user:
            # register current user for subsequent requests to user
            # (e.g. logging the request)
            self._jupyterhub_user = user
            self.redirect(self.get_next_url(user))
        else:
            html = self._render(
                login_error='Invalid username or password',
                server=data['server'],
                username=data['username'],
            )
            self.finish(html)


# https://github.com/jupyterhub/jupyterhub/blob/1.0.0/jupyterhub/auth.py
class OmeroAuthenticator(Authenticator):

    omero_servers = List(
        trait=Unicode,
        config=True,
        help='OMERO hostnames or connection URLs')

    export_omero_env = Bool(
        False,
        config=True,
        help='Pass OMERO session environment variables to spawner')

    def normalize_username(self, username):
        """
        https://github.com/jupyterhub/jupyterhub/blob/1.0.0/jupyterhub/auth.py#L317
        """
        def escape_nonalpha(c):
            """
            Replace non-alphanumeric characters with bytes converted to _hex
            """
            if c.isalnum():
                return c
            return ''.join('_{:x}'.format(b) for b in c.encode())

        username = ''.join(escape_nonalpha(c) for c in username)
        return username

    async def authenticate(self, handler, data):
        """
        https://github.com/jupyterhub/jupyterhub/blob/1.0.0/jupyterhub/auth.py#L474
        """
        self.log.debug('data: %s', dict(
            (k, v if k != 'password' else '********')
            for (k, v) in data.items()))
        server = data['server']
        if server not in self.omero_servers:
            self.log.error('Invalid server: %s', server)
            # TODO: Return a HTTP Error instead of an exception
            raise Exception('Invalid server')
        client = omero.client(data['server'])
        try:
            session = client.createSession(data['username'], data['password'])
        except Exception as e:
            self.log.warning(e)
            return None

        adminsvc = session.getAdminService()
        experimenter = adminsvc.lookupExperimenter(data['username'])

        # https://github.com/ome/omero-gateway-java/blob/v5.5.4/src/main/java/omero/gateway/facility/AdminFacility.java#L512
        available_privs = session.getTypesService().allEnumerations(
            'AdminPrivilege')
        privs = adminsvc.getAdminPrivileges(experimenter)
        isadmin = len(available_privs) == len(privs)
        username = self.normalize_username(unwrap(experimenter.omeName))

        user = {
            'name': username,
            'admin': isadmin,
            'auth_state': {
                'omero_host': server,
                'omero_user': username,
                'session_id': client.getSessionId(),
            },
            'client': client,
        }
        self.log.debug(user)
        return user

    async def refresh_user(self, user, handler=None):
        """
        https://github.com/jupyterhub/jupyterhub/blob/1.0.0/jupyterhub/auth.py#L429

        If enable_auth_state is disabled we can't refresh since we don't have
        the session-id to check
        """
        if not self.enable_auth_state:
            self.log.error('auth_state is disabled, not refreshing')
            return True

        auth_state = await user.get_auth_state()
        if not all([
            auth_state.get('session_id'),
            auth_state.get('omero_host') in self.omero_servers,
        ]):
            self.log.warning('auth_state does not match')
            return False

        client = omero.client(auth_state['omero_host'])
        try:
            session = client.joinSession(auth_state['session_id'])
            session.detachOnDestroy()
            client.closeSession()
            self.log.debug('refreshed user %s', user)
            return True
        except Exception as e:
            self.log.warning(e)
            return False

    # TODO: Is gen.coroutine needed?
    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        if self.export_omero_env:
            auth_state = yield user.get_auth_state()
            self.log.debug('pre_spawn_start auth_state:%s' % auth_state)
            if not auth_state:
                return
            # setup environment
            spawner.environment['OMERO_HOST'] = auth_state['omero_host']
            spawner.environment['OMERO_USER'] = auth_state['omero_user']
            spawner.environment['OMERO_SESSION'] = auth_state['session_id']

    def get_handlers(self, app):
        return [('/login', OmeroLoginHandler, {
            'omero_servers': self.omero_servers})]
