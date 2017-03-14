#!/usr/bin/python
# encoding: utf-8
# Author: Bernardo Macias <bmacias@httpstergeek.com>
#
#
# All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Bernardo Macias '
__credits__ = ['Bernardo Macias']
__license__ = "ASF"
__version__ = "2.0"
__maintainer__ = "Bernardo Macias"
__email__ = 'bmacias@httpstergeek.com'
__status__ = 'Production'


import urllib, urllib2
import json


class SPLK():
    """
    Simple class for working with Splunk Search API. Use Splunk SDK if possible
    """
    def __init__(self, url, username, password):
        """
        :param url: string, http(s)://server.com:<port>
        :param username: string, username of Splunk user
        :param password: string, Splunk user password
        :return:
        """
        self.url = url
        self.username = username
        self.password = password
        self.session_key = None
        self.output_mode = 'json'
        self.auth_header = None
        self.job_id = None
        self.job_details = None

    def requestsession(self):
        """
        request session key
        :return:
        """
        data = dict(username=self.username, password=self.password, output_mode=self.output_mode)
        request = urllib2.Request('{0}{1}'.format(self.url, '/services/auth/login'),
                                  data=urllib.urlencode(data))
        connection = urllib2.urlopen(request)
        response = connection.read()
        self.session_key = json.loads(response)['sessionKey']
        self.auth_header = {'Authorization': 'Splunk {0}'.format(self.session_key)}
        connection.close()

    def savedsearches(self):
        data = dict(username=self.username, password=self.password, output_mode=self.output_mode)
        request = urllib2.Request('{0}{1}'.format(self.url, '/services/saved/searches'),
                                  data=urllib.urlencode(dict(output_mode=self.output_mode)),
                                  headers=self.auth_header)
        print self.auth_header
        connection = urllib2.urlopen(request)
        response = connection.read()
        print response

    def alljobsdetails(self):
        request = urllib2.Request('{0}{1}'.format(self.url,
                                                  '/servicesNS/splunk-system-user/search/search/jobs'),
                                  data=urllib.urlencode(dict(output_mode=self.output_mode)),
                                  headers=self.auth_header)
        connection = urllib2.urlopen(request)
        self.job_details = json.loads(connection.read())
        connection.close()
        return self.job_details




if __name__ == '__main__':
    import time
    base_url = ''
    username = ''
    password = ''
    # output_mode can be either csv, raw or json
    #output_mode = 'csv'
    output_mode = 'json'
    #output_mode = 'xml'

    splunk = SPLK(url=base_url,
                  username=username,
                  password=password)
    splunk.requestsession()
    print splunk.auth_header
    print splunk.savedsearches()

    exit()
