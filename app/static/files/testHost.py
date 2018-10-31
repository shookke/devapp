from python_hosts import Hosts, HostsEntry
import requests


hosts = Hosts(path='C:\Windows\System32\drivers\etc\hosts')
r = requests.get('http://dev.nsyncdata.net:9000/hosts')
r = r.json()
#print (r['Add'][0]['Address'])
for item in r['Remove']:
    print (item['URL'])
    hosts.remove_all_matching(name=item['URL'])
for item in r['Add']:
    print (item['URL'])
    new = HostsEntry(entry_type='ipv4', address=item['Address'], names=[item['URL']])
    hosts.add([new],force=True, allow_address_duplication=True)
hosts.write()
print (hosts)