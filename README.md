# **FTPHP** - **F**\*\*king **T**wisted **P**ython **H**oney**P**ot

## Description

A high-interaction FTP honeypot written in Python with [Twisted](https://twisted.org/).

## Goals
- Perfectly emulate an existing FTP server (indistinguishable from attacker's perspective).
- Perform more efficiently than an actual FTP server.
- Collect more verbose information on attackers than would normally be accessible from standard FTP servers.

### Additional Goals:
- The option to emulate a specific version/type of FTP server.
- Customize the emulated filesystem and create boobytraps with "hackback" files.
- Have well documented/readable code

## Checklist
- ~~Create a simple FTP server that users can connect to~~
- ~~Anonymous Login~~
- ~~Allow users to login with specified credentials~~
- ~~Alter the displayed FTP banner (check NMAP Signatures)~~
- ~~Add [configuration file support](https://towardsdatascience.com/from-novice-to-expert-how-to-write-a-configuration-file-in-python-273e171a8eb3)~~
- Configure file directory with [temporary file systems](https://www.pyfilesystem.org/page/tempfs/)
- Boobytrap file exports
- Save transfered files for analysis
- Log connections to FTP server
- [Log all actions](https://betterstack.com/community/guides/logging/how-to-start-logging-with-python/) taken by FTP users


## Notes

### Nmap Service Identification Details

[Nmap Serice Probes Documentation](https://nmap.org/book/vscan-fileformat.html)

`Probe <protocol> <probename> <probestring> [no-payload]`

`match <service> <pattern> [<versioninfo>]`

[Nmap Probes File](https://svn.nmap.org/nmap/nmap-service-probes)

```
Probe TCP GenericLines q|\r\n\r\n|
rarity 1
ports 21,23,35,43,79,98,110,113,119,199,214,264,449,505,510,540,587,616,628,666,731,771,782,1000,1010,1040-1043,1080,1212,1220,1248,1302,1400,1432,1467,1501,1505,1666,1687-1688,2010,2024,2600,3000,3005,3128,3310,3333,3940,4155,5000,5400,5432,5555,5570,6112,6432,6667-6670,7144,7145,7200,7780,8000,8138,9000-9003,9801,11371,11965,13720,15000-15002,18086,19150,26214,26470,31416,30444,34012,56667
sslports 989,990,992,995
```

`grep 'match ftp' nmap-service-probes > ~/ftp_probes.txt`

### FTP Details

https://datatracker.ietf.org/doc/html/rfc959

https://docs.twisted.org/en/latest/api/twisted.protocols.ftp.html
