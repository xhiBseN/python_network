import sys, socket, struct
from netaddr import IPNetwork, IPAddress, IPSet

# Read Zone Subnets from argv[1]
zonefn = sys.argv[1]
with open(zonefn) as zp:
    subnet = list(enumerate(zp.read().splitlines()))
zones = {}
#Expect smth like: SomeZone,1.2.3.0/24
for index,net in subnet:
    n = net.split(',')
    ip = IPNetwork(n[1])
    zones.update({ip : n[0], })
# Read FW CSV from argv[2]
rulefn = sys.argv[2]
#Expect smth like: "SomeInterface","Rule#","Enabled","Sources","User","Security Group","Service","Action","Hits","Description","Logging","Time"
with open(rulefn) as fp:
    rulelist = list(enumerate(fp.read().splitlines()))
bigrulebook = []
for bigrule in rulelist[1:]:
    brsplit = bigrule[1].split('\",\"')
    # Interface of rule
    brif = brsplit[0]
    # No. of rule in Interface
    brrno = brsplit[1]
    # All Sources of rule
    brsrcs = list(brsplit[3].split(','))
    # All Destionations of rule
    brdsts = list(brsplit[6].split(','))
    # All Ports of rule
    brports = list(brsplit[8].split(','))
    # Comment
    brcmt = brsplit[11]
    if brsplit[2].strip('\"') == 'True':
        if brsplit[9].strip('\"') == 'Permit':
            for src in brsrcs:
                for dst in brdsts:
                    for port in brports:
                        bigrule = { 'IF' : brsplit[0],
                                    'RuleNo' : brsplit[1],
                                    'Src' : IPNetwork(src),
                                    'Dst': IPNetwork(dst),
                                    'Port' : port,
                                    'Comment' : brcmt }
                        bigrulebook.append(bigrule)
shadowed, overlapped, allowed, denied = [], [], [], []
intra = {}
for sr in bigrulebook:
    # Check for Source zone
    for i, (network,zone) in enumerate(zones.items()):
        if sr['Src'] in IPSet([network]):
            srczone = zone
            # Put Intrazone Traffic away
            if sr['Dst'] in IPSet([network]):
                intra.update({sr : zone})
            break
    # Check for Destionation zone
    for i, (network,zone) in enumerate(zones.items()):
        if sr['Dst'] in IPSet([network]):
            dstzone = zone
            break
