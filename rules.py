import sys, socket, struct
from netaddr import IPNetwork, IPAddress

# Read Zone Subnets
zonefn = sys.argv[1]
with open(zonefn) as zp:
    subnet = list(enumerate(zp.read().splitlines()))
subnetdict = {}
for index,net in subnet:
    n = net.split('\",\"')
    ip = IPNetwork(n[1])
    subnetdict = { n[2] : ip, }
print(subnetdict)
