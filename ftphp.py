#!/usr/bin/python3
"""
An example FTP server with minimal user authentication from Twisted Documentation. 
"""
# Patched version of Twisted example. Patch is based on fixing bug in Twisted FTP creds check
# https://github.com/twisted/twisted/blob/1d439dd1d9c7d302641550a925705d479ea5457f/src/twisted/protocols/ftp.py
# https://github.com/twisted/twisted/tree/1d439dd1d9c7d302641550a925705d479ea5457f/src/twisted/cred

from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.cred.portal import Portal
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory, FTPRealm, FTP, AuthorizationError, IFTPShell
import pathlib as Path

# Required for Patched Login
from twisted.cred import credentials, error as cred_error


def main():
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

    # FTP Configuration Variables
    ftp_port = 2121
    ftp_banner = 'Fucking Twisted Python Honey Pot'

    # Path Variables
    cwd = Path.cwd()
    ftp_root = cwd / 'root'
    user_home = ftp_root
    anon_root = ftp_root / 'anonymous'
    pass_file = 'passwd'

    # Setup FTP FileSystem
    ftp_realm = FTPRealm(anonymousRoot=anon_root, userHome=user_home)

    # Setup FTP Authentication
    ftp_checkers = []
    ftp_checkers.append(AllowAnonymousAccess())
    ftp_checkers.append(FilePasswordDB(pass_file))

    # Putting it all together
    try:
        ftp_portal = Portal(realm=ftp_realm, checkers=ftp_checkers)
        ftp_factory = FTPFactory(portal=ftp_portal)
        ftp_factory.protocol = PatchedFtpProtocol
        ftp_factory.welcomeMessage = ftp_banner
        ftp_factory.timeout = 600

        # Starts the reactor loop on specified port and interface. Connections will be handled by the factory.
        reactor.listenTCP(port=ftp_port, factory=ftp_factory, backlog=50, interface='')
        reactor.run()
    except Exception as e:
        print(e)
        exit(-1)

if __name__ == '__main__':
    main()