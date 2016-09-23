import urllib
import urllib2
from xml.dom import minidom
import json
import time
import logging

USERNAME = '<username>'
PASSWORD = '<password>'
WEB_PORT = 8089
SERVER_LIST = ['lyn-del-spl-101',
               'lyn-del-spl-102',
               'lyn-del-spl-103',
               'lyn-del-spl-104',
               'lyn-del-spl-201',
               'lyn-del-spl-202',
               'lyn-del-spl-203',
               'lyn-del-spl-204',
               'lyn-del-spl-205',
               'lyn-del-spl-206',
               'lyn-del-spl-301',
               'lyn-del-spl-302',
               'lyn-del-spl-303',
               'lyn-del-spl-304',
               'lyn-del-spl-305',
               'lyn-del-spl-306',
               'lyn-del-spl-307',
               'wfc-zit-spl-201',
               'wfc-zit-spl-202']

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%m-%d-%YT%H:%M:%S%Z')
ch.setFormatter(formatter)
logger.addHandler(ch)


def stringkey(jsonstring):
    msg = ' '.join(['%s="%s"' % (key, value) for key, value in jsonstring.items() if not key in ['sessionkey', 'sid', 'webport', 'isDone']])
    return msg


def startjob(server, port, username, password):
    OUTPUT_MODE = 'json'
    SEARCH_QUERY = 'search index=_internal earliest=-10m | stats count by host'
    AUTH_ENDPOINT = '/services/auth/login'
    JOB_ENDPOINT = '/servicesNS/admin/search/search/jobs/'
    SEARCH_QUERY = 'search index=_internal earliest=-10m | stats count by host'
    info = {
            'server': server,
            'webport': port,
            'sessionkey': None,
            'isFailed': False,
            'runDuration': None,
            'eventCount': None,
            'sid': None,
            'scanCount': None,
            'isDone': False
            }
    request = urllib2.Request('https://{}:{}{}'.format(server, port, AUTH_ENDPOINT),
                              data=urllib.urlencode({'username': username, 'password': password}))
    try:
        response = urllib2.urlopen(request)
        sessionkey = minidom.parseString(response.read()).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue if response else None
        info['sessionkey'] = sessionkey
        request = urllib2.Request('https://{}:{}{}'.format(server, WEB_PORT, JOB_ENDPOINT),
                                  data=urllib.urlencode({'search': SEARCH_QUERY, 'output_mode': OUTPUT_MODE}),
                                  headers = { 'Authorization': ('Splunk %s' % sessionkey)})
        response = urllib2.urlopen(request)
        info['sid'] = json.loads(response.read())['sid']
    except Exception as e:
        info['sid'] = None
        info['isFailed'] = True
    return info

def checkjob(info):
    OUTPUT_MODE = 'json'
    JOB_ENDPOINT = '/servicesNS/admin/search/search/jobs/'
    if info['sessionkey'] and (not info['isDone'] or not info['isFailed']):
        request = urllib2.Request('https://{}:{}{}{}'.format(info['server'], info['webport'], JOB_ENDPOINT, info['sid']),
                                  data=urllib.urlencode({'output_mode': OUTPUT_MODE}),
                                  headers={'Authorization': ('Splunk %s' % info['sessionkey'])})
        try:
            response = urllib2.urlopen(request)
            status = json.loads(response.read())
        except Exception as e:
            status = None
            info['isFailed'] = True
        info['isDone'] = status['entry'][0]['content']['isDone'] if status else False
        if info['isDone']:
            info['isFailed'] = status['entry'][0]['content']['isFailed']
            info['eventCount'] = status['entry'][0]['content']['eventCount']
            info['scanCount'] = status['entry'][0]['content']['scanCount']
            info['scanCount'] = status['entry'][0]['content']['scanCount']
            info['runDuration'] = status['entry'][0]['content']['runDuration']
    return info


if __name__ == "__main__":
    jobs = []
    for server in SERVER_LIST:
        job = startjob(server, WEB_PORT, USERNAME, PASSWORD)
        jobs.append(job)
    while len(jobs) > 0:
        for i, item in enumerate(jobs):
            jobstatus = checkjob(item)
            if jobstatus['isDone'] or jobstatus['isFailed']:
                msg = stringkey(jobstatus)
                logger.info(msg)
                del jobs[i]
        time.sleep(3)



