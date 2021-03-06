from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

username = input('User Name: ')
password = getpass()
enapw = getpass('Enable Password:')

core1 = {
    'device_type': 'cisco_ios',
    'ip': '172.30.50.1',
    'username': username,
    'password': password,
    'secret': enapw,
}

core2 = {
    'device_type': 'cisco_ios',
    'ip': '172.30.50.3',
    'username': username,
    'password': password,
    'secret': enapw,
}

devices =[core1, core2]

for device in devices:
    try:
        net_connect = ConnectHandler(**device)
    except (AuthenticationException):
        print('Auth failed: ' + device['ip'])
        continue
    except (NetMikoTimeoutException):
        print('Timeout to device: ' + device['ip'])
        continue
    except (EOFError):
        print('EoF at: ' + device['ip'])
        continue
    except (SSHException):
        print('SSH Issue: ' + device['ip'])
        continue
    except Exception as unknown_error:
        print('idk what when wrong: ' + str(unknown_error))
        continue
    net_connect.find_prompt()
    output = net_connect.send_command('show int status | in connected')
    iflist = list(enumerate(output.split('\n')))
    ifs = {}
    for index,line in iflist:
        inf = {}
        list = ' '.join(line.split()).split(' ')
        conf = net_connect.send_command('show run int '+list[0])
        inf = { 'Interfacename': list[0],}
        shint = net_connect.send_command('show int '+list[0]).split('\n')
        for speed in shint:
            if speed.find('duplex')>-1:
                inf = {'Speed' : speed,}
                break
        config = conf.split('\n',4)[4]
        inf = {'Config': config,}
        ifs = {list[0]: inf,}
    completeconfig = {}
    print('\n==============')
    print(device['ip'])
    print('==============\n')
    print('Interfaces:')
    print('===========\n')
    for interface in ifs.items():
        print(interface['Interfacename'])
        print(interface['speed'])
        completeconfig = {interface['Interfacename'] : interface['Config'],}
    print('\nConfig:')
    print('=========\n')
    for cfg in completeconfig.items():
        print(cfg)
