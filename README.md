# **FTPHP** - **F**\*\*king **T**wisted **P**ython **H**oney**P**ot

## Description

A high-interaction FTP honeypot written in the Python with Twisted library.

## Goals
- Perfectly emulate an existing FTP server (indistinguishable from attacker's perspective).
- Perform more efficiently than an actual FTP server.
- Collect more verbose information on attackers than would normally be accessible from standard FTP servers.


### Additional Goals:
- The option to emulate a specific version/type of FTP server.
- Customize the emulated filesystem and create boobytraps with "hackback" files.
- Have well documented/readable code