import sys, socket, struct
from netaddr import IPNetwork, IPAddress, IPSet

# Read Zone Subnets from argv[1]
# Expect smth like: SomeZone,1.2.3.0/24
with open(sys.argv[1]) as zp:
    subnet = list(enumerate(zp.read().splitlines()))
zones = {}
for index,net in subnet:
    n = net.split(',')
    ip = IPNetwork(n[1])
    zones.update({ip : n[0], })

# Read FW Interface Setup
# Excpect smth like: SomeInterface, IPNet - Maybe we add vlan here just for christ sake
with open(sys.argv[2]) as zp:
    subnet = list(enumerate(zp.read().splitlines()))
interface = {}

# Read FW CSV from argv[2]
# Expect smth like: "SomeInterface","Rule#","Enabled","Sources","User","Security Group","Service","Action","Hits","Description","Logging","Time"
with open(sys.argv[3]) as fp:
    rulelist = list(enumerate(fp.read().splitlines()))
br = []
for bigrule in rulelist[1:]:
    brsplit = bigrule[1].split('\",\"')
    # brif: Interface of rule, brrno: No. of rule in Interface, brsrcs: All Sources of rule,
    # brdsts: All Destionations of rule, brports: All Ports of rule, brcmt: Remark
    brif = brsplit[0]
    brrno = brsplit[1]
    brsrcs = list(brsplit[3].split(','))
    brdsts = list(brsplit[6].split(','))
    brports = list(brsplit[8].split(','))
    brcmt = brsplit[11]
	# Only work with enabled rules
    if brsplit[2].strip('\"') == 'True':
	    #split into 1 to 1 relations
        for src in brsrcs:
            for dst in brdsts:
                for port in brports:
                    bigrule = { 'IF' : brsplit[0],
                                'RuleNo' : brsplit[1],
                                'Src' : ('any', IPNetwork(src))[src == 'any'],
                                'Dst': ('any', IPNetwork(dst))[dst == 'any'],
                                'Port' : port,
                                'Action' : brsplit[9].strip('\"'),
                                'Comment' : brcmt }
					# Create List of all Interfaces
                    intdict = { brsplit[0] : 'Interface', }
                    br.append(bigrule)
# Create Rulebook for each Interface
for z,i in enumerate(intdict.items()):
    rbook = { z : [] }
# Sort Rules into dict by Interface
for r in br:
    rbook = { r['IF'] : rbook[r['IF']].append(r) }
print(rbook)
shadowed, overlapped, allowed, denied = [], [], [], []
intra = {}
for sr in br:
    # Check for Source zone
    for i, (network,zone) in enumerate(zones.items()):
        if sr['Src'] in IPSet([network]):
            srczone = zone
            break
    # Check for Destionation zone
    for i, (network,zone) in enumerate(zones.items()):
        if sr['Dst'] in IPSet([network]):
            dstzone = zone
            break
    # Put Intrazone Traffic away
    if srczone == dstzone:
        intra.update({sr : zone})
        continue
	# Classify Permit/Deny
    if sr['Action'] == "Deny":
        # Add rule to denied Traffic:
        denied.append(sr)
        continue
	# Permit Traffic:
	# Check if Src Dst Port combination is denied already -> Shadowed
    for dr in denied:
        if dr['Src'] == 'any' | sr['Src'] in IPSet([dr['Src']]):
            if sr['Dst'] in IPSet([dr['Dst']]):
                if  dr['Port'] == 'ip' | sr['Port'] == dr['Port']:
                    shadowed.append(sr)
                    continue
	# Check if Src Dst Port combination is allowed already -> Overlapped
    for dr in allowed:
        if sr['Src'] in IPSet([dr['Src']]):
            if sr['Dst'] in IPSet([dr['Dst']]):
                if  dr['Port'] == 'ip' | sr['Port'] == dr['Port']:
                    overlapped.append(sr)
                    continue
	# If not shadowed or overlapped -> Add to allowed
    allowed.append(sr)
# build ruleset from allowed small rules
print('Allow: '+allow+'\\nDenied: '+denied+'\\n Shadowed: '+shadowed+'Overlapped: '+overlapped)
