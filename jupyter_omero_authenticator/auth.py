from jupyterhub.auth import Authenticator
from traitlets import Unicode
import omero.clients


# https://github.com/jupyterhub/jupyterhub/blob/1.0.0/jupyterhub/auth.py
class OmeroAuthenticator(Authenticator):

    omero_host = Unicode(
        config=True,
        help='omero hostname or connection url')

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
        client = omero.client(self.omero_host)
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

        user = {
            'name': self.normalize_username(data['username']),
            'admin': isadmin,
            'auth_state': {
                'omero_host': self.omero_host,
                'omero_user': data['username'],
                'session_id': client.getSessionId(),
            }
        }
        self.log.debug(user)
        return user
