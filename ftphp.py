#!/usr/bin/python3
"""
An example FTP server with minimal user authentication from Twisted Documentation. 
"""
# Patched version of Twisted example. Patch is based on fixing bug in Twisted FTP creds check
# https://github.com/twisted/twisted/blob/1d439dd1d9c7d302641550a925705d479ea5457f/src/twisted/protocols/ftp.py

from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.cred.portal import Portal
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory, FTPRealm, FTP, AuthorizationError, IFTPShell

# Required for Patched Login
from twisted.cred import credentials, error as cred_error

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
            # THIS IS THE PATCH! CONVER PASSWORD TO BYTES STRING BEFORE CREATING CRED OBJECT!
            print(f"{self._user=}:{password=}")
            creds = credentials.UsernamePassword(bytes(self._user, 'utf-8'), bytes(password, 'utf-8'))
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

p = Portal(FTPRealm("./"), [AllowAnonymousAccess(), FilePasswordDB("passwd")])
f = FTPFactory(p)
f.protocol = PatchedFtpProtocol
reactor.listenTCP(2121, f)
reactor.run()