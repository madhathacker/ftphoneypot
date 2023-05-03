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
- Alter the displayed FTP banner (check NMAP Signatures)
- Configure file directory
- Log connections to FTP server
- Log all actions taken by FTP users