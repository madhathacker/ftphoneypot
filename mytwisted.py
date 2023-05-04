
"""
Patched version of Twisted example. 
Patch is based on fixing bug in Twisted FTP creds check
"""

# https://github.com/twisted/twisted/blob/1d439dd1d9c7d302641550a925705d479ea5457f/src/twisted/protocols/ftp.py
# https://github.com/twisted/twisted/tree/1d439dd1d9c7d302641550a925705d479ea5457f/src/twisted/cred

from twisted.protocols.ftp import FTP, BaseFTPRealm, FTPRealm, IFTPShell, AuthorizationError
from twisted.cred.checkers import ICredentialsChecker
# Required for Patched Login
from twisted.cred import credentials, error as cred_error
from zope.interface import implementer
from twisted.python import filepath, failure
from twisted.internet import defer

# GENERATE VIRTUAL FILESYSTEM FOR USER HERE?
class VirtualFTPRealm(FTPRealm):
    def __init__(self, anonymousRoot, userHome):
        BaseFTPRealm.__init__(self, anonymousRoot)
        self.userHome = filepath.FilePath(userHome)

    def getHomeDirectory(self, avatarId):
        return self.userHome.child(avatarId)

@implementer(ICredentialsChecker)
class DenyAllAccess:
    credentialInterfaces = (credentials.IAnonymous, credentials.IUsernamePassword)

    def requestAvatarId(self, credentials):
        return failure.Failure(cred_error.UnauthorizedLogin())

@implementer(ICredentialsChecker)
class AllowAllAccess:
    credentialInterfaces = (credentials.IUsernamePassword,)

    def requestAvatarId(self, credentials):
        return defer.succeed(credentials.username)

GUEST_LOGGED_IN_PROCEED = "230.2"
USR_LOGGED_IN_PROCEED = "230.1"
AUTH_FAILURE = "530.2"

class PatchedFtpProtocol(FTP):
    # patching login to convert username and password to bytes
    def ftp_PASS(self, password):
        """
        Second part of login.  Get the password the peer wants to
        authenticate with.
        """
        if self.factory.allowAnonymous and self._user == self.factory.userAnonymous:
            # anonymous login
            creds = credentials.Anonymous()
            reply = GUEST_LOGGED_IN_PROCEED
        else:
            # user login
            # THIS IS THE PATCH! CONVERT USER & PASSW TO BYTES STRING BEFORE CREATING CRED OBJECT!
            creds = credentials.UsernamePassword(self._user.encode('utf-8'), password.encode('utf-8'))
            reply = USR_LOGGED_IN_PROCEED
        del self._user

        def _cbLogin(result):
            (interface, avatar, logout) = result
            assert interface is IFTPShell, "The realm is busted, jerk."
            self.shell = avatar
            self.logout = logout
            self.workingDirectory = []
            self.state = self.AUTHED
            return reply

        def _ebLogin(failure):
            failure.trap(cred_error.UnauthorizedLogin, cred_error.UnhandledCredentials)
            self.state = self.UNAUTH
            raise AuthorizationError

        d = self.portal.login(creds, None, IFTPShell)
        d.addCallbacks(_cbLogin, _ebLogin)
        return d