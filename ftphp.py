#!/usr/bin/python3
"""
An example FTP server with minimal user authentication from Twisted Documentation. 
"""
# Logging
import colorlog, logging, sys, time

# Config File
from dataclasses import dataclass
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf, MISSING

# Twisted
from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB
from twisted.cred.portal import Portal
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory
from mytwisted import PatchedFtpProtocol, VirtualFTPRealm, DenyAllAccess, AllowAllAccess

# Filepaths
from pathlib import Path

config_path = '.'
config_name = "config.yaml"

# @dataclass(frozen=True) means they are read-only fields
@dataclass
class ftphp_config:
  ftp_port: int = 2121
  ftp_banner: str = "Fucking Twisted Python Honey Pot"
  allow_anonymous: bool = True
  allow_login: bool= True
  high_interaction: bool = True
  ftp_root: str = 'root'
  pass_file: str = 'passwd'

cs = ConfigStore.instance()
cs.store(name="ftphp_config", node=config_name)

@hydra.main(version_base=None, config_path=config_path, config_name=config_name)
def ftphp(cfg : DictConfig)-> None:
    timestamp = str(int(time.time()))
    logfile = "./"+timestamp+"_"+cfg.logging.logfile
    logging.basicConfig(
        filename=logfile, 
        level=cfg.logging.loglevel, 
        format = cfg.logging.format, 
        datefmt = cfg.logging.datefmt)
    log = logging.getLogger()
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(colorlog.ColoredFormatter('%(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s - %(message)s'))
    log.addHandler(handler)

    log.info(f"Logging to: {logfile}")
    log.debug(OmegaConf.to_yaml(cfg))

    # FTP Configuration Variables
    ftp_port = cfg.ftphp.port
    ftp_banner = cfg.ftphp.banner

    # Path Variables
    cwd = Path.cwd()
    ftp_root = Path(cfg.ftphp.root)
    anon_root = ftp_root / 'anonymous'
    pass_file = 'passwd'

    # Setup FTP Authentication
    ftp_checkers = []
    if cfg.ftphp.allow_login:
        if cfg.ftphp.allow_anonymous:
            ftp_checkers.append(AllowAnonymousAccess())
        if cfg.ftphp.restrict_login:
            ftp_checkers.append(FilePasswordDB(pass_file))
        else:
            ftp_checkers.append(AllowAllAccess())
    else:
        ftp_checkers.append(DenyAllAccess())
    log.debug(f"{ftp_checkers=}")

    # Putting it all together
    try:
        ftp_realm = VirtualFTPRealm(anonymousRoot=anon_root, userHome=ftp_root)
        ftp_portal = Portal(checkers=ftp_checkers, realm=ftp_realm)
        ftp_factory = FTPFactory(portal=ftp_portal)
        ftp_factory.protocol = PatchedFtpProtocol
        ftp_factory.welcomeMessage = ftp_banner
        ftp_factory.timeout = 600

        # Starts the reactor loop on specified port and interface. Connections will be handled by the factory.
        reactor.listenTCP(port=ftp_port, factory=ftp_factory, backlog=50, interface='')
        log.info("Starting Reactor...")
        reactor.run()
        ftp_realm.stop()
    except Exception as e:
        print(e)
        exit(-1)

if __name__ == '__main__':
    ftphp()