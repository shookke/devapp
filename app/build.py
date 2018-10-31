import time
import jenkins
from app import app

SERVER = jenkins.Jenkins(app.config['JENKINS_URL'], username='kevin', password=app.config['JENKINS_TOKEN'])

class Build:
    """Handles Jenkins Interactions"""
    def __init__(self, name, database, db_user, db_pw, url, prefix):
        self.name = name
        self.database = database
        self.db_user = db_user
        self.db_pw = db_pw
        self.prefix = prefix
        self.url = url

    def build(self, job, token):
        """Build Jenkins job and return build info"""
        data = {'token': token,
                'NAME': self.name,
                'DB': self.database,
                'DB_USER':self.db_user,
                'DB_PW': self.db_pw,
                'URL':self.url,
                'PREFIX':self.prefix
               }
        return SERVER.build_job(job, data)

    def status(self, job, item):
        """Updates status of Jenkins build"""
        timeout = 7
        while timeout != 0:
            last_build = SERVER.get_job_info(job)['lastBuild']['number']
            build_info = SERVER.get_build_info(job, last_build)
            if build_info['queueId'] == item:
                if build_info['result'] in ['SUCCESS', 'FAILURE']:
                    if job == 'down-container':
                        if build_info['result'] == 'FAILRUE':
                            return build_info['result']
                        else:
                            return 'DOWN'
                    else:
                        return build_info['result']
            time.sleep(5)
            timeout -= 1
        return 'ERROR'
