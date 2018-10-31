from SMWinservice import SMWinservice
from python_hosts import Hosts, HostsEntry
import requests
import time

class HostsManager(SMWinservice):
    _svc_name_ = "HostsManager"
    _svc_display_name_ = "Hosts Manager"
    _svc_description_ = "Adds and removes host entries"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        i = 0
        while self.isrunning:
            hosts = Hosts(path='C:\Windows\System32\drivers\etc\hosts')
            r = requests.get('http://dev.nsyncdata.net:9000/hosts')
            r = r.json()
            for item in r['Remove']:
                hosts.remove_all_matching(name=item['URL'])
            for item in r['Add']:
                new = HostsEntry(entry_type='ipv4', address=item['Address'], names=[item['URL']])
                hosts.add([new],force=True, allow_address_duplication=True)
            hosts.write() 
            time.sleep(30)

if __name__ == '__main__':
    HostsManager.parse_command_line()