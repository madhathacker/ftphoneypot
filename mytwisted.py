
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
import time, uuid
from colorama import Fore, Style
from myfactories import TempFSFactory

# GENERATE VIRTUAL FILESYSTEM FOR USER HERE?
class VirtualFTPRealm(FTPRealm):
    def __init__(self, anonymousRoot, userHome):
        print("Initializing FTP Realm...")
        BaseFTPRealm.__init__(self, anonymousRoot)
        self.userHome = filepath.FilePath(userHome)
        self.TempFS_factory = TempFSFactory()
        self.TempFS_factory.start()

    def stop(self):
        self.TempFS_factory.stop()

    # This function is called after user passes crednetial checker
    def getHomeDirectory(self, avatarId): 
        temp_home = self.TempFS_factory.get_temp_fs()
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

class PatchedFtpProtocol(FTP):
    def __init__(self):
        self.proto_instance = str(uuid.uuid1())
        #print(f"New FTP Protocol Instance: {self.proto_instance}")
    def connectionMade(self):
        ms_time = int(round(time.time() * 1000))
        self.connected_client = self.transport.getPeer()
        print(f'[{ms_time}] {Fore.GREEN}New client connected!{Style.RESET_ALL} {Fore.BLUE}[{self.connected_client.host}:{self.connected_client.port}]{Style.RESET_ALL} {Fore.MAGENTA}{self.proto_instance}{Style.RESET_ALL}')
        FTP.connectionMade(self)
    def lineReceived(self, line):
        ms_time = int(round(time.time() * 1000))
        print(f'[{ms_time}]   {Fore.BLUE}[{self.connected_client.host}:{self.connected_client.port}]{Style.RESET_ALL} {Fore.MAGENTA}{self.proto_instance}{Style.RESET_ALL} Command Received: {line}')
        FTP.lineReceived(self, line)
    def connectionLost(self, reason):
        ms_time = int(round(time.time() * 1000))
        print(f'[{ms_time}] {Fore.RED}Client disconnected!{Style.RESET_ALL} {Fore.BLUE}[{self.connected_client.host}:{self.connected_client.port}]{Style.RESET_ALL} {Fore.MAGENTA}{self.proto_instance}{Style.RESET_ALL}')
        FTP.connectionLost(self, reason)

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