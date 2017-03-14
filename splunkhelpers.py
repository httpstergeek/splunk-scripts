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

import urllib
import urllib2
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

    def createjob(self, search_query):
        """
        creates a search job
        :param search_query: string
        :return:
        """
        data = dict(search=search_query, output_mode=self.output_mode, count='-1')
        search_url = '/servicesNS/{0}/search/search/jobs/'.format(self.username)
        request = urllib2.Request('{0}{1}'.format(self.url, search_url),
                                  data=urllib.urlencode(data),
                                  headers=self.auth_header)
        connection = urllib2.urlopen(request)
        self.job_id = json.loads(connection.read())['sid']
        connection.close()

    def jobdetails(self, job_id):
        """
        requests job details based on job_id. Can be any of QUEUED, PARSING, RUNNING, PAUSED, FINALIZING, FAILED, DONE.
        :param job_id: string
        :return:
        """
        request = urllib2.Request('{0}{1}{2}'.format(self.url,
                                                     '/servicesNS/{0}/search/search/jobs/'.format(self.username),
                                                     job_id),
                                  data=urllib.urlencode(dict(output_mode=self.output_mode)),
                                  headers=self.auth_header)
        connection = urllib2.urlopen(request)
        self.job_details = json.loads(connection.read())
        connection.close()
        return self.job_details

    def alljobsdetails(self):
        request = urllib2.Request('{0}{1}'.format(self.url,
                                                  '/servicesNS/splunk-system-user/search/search/jobs'),
                                  data=urllib.urlencode(dict(output_mode=self.output_mode)),
                                  headers=self.auth_header)
        connection = urllib2.urlopen(request)
        self.job_details = json.loads(connection.read())
        connection.close()
        return self.job_details

    def jobstatistics(self, job_details):
        job_statistics = dict()
        job_statistics['disk_usage'] = int(job_details['entry'][0]['content']['diskUsage']) / 1024
        job_statistics['run_duration'] = job_details['entry'][0]['content']['runDuration']
        job_statistics['performance'] = job_details['entry'][0]['content']['performance']
        job_statistics['resultCount'] = job_details['entry'][0]['content']['resultCount']
        return job_statistics

    def jobstatus(self):
        """
        Parses jobdetails. Can be any of QUEUED, PARSING, RUNNING, PAUSED, FINALIZING, FAILED, DONE.
        :return:
        """
        return self.job_details['entry'][0]['content']['dispatchState']

    def getresults(self, job_id, outputmode):
        """
        Retrieves search results from Splunk
        :param job_id:
        :param outputmode:
        :return:
        """
        search_url = '/servicesNS/{0}/search/search/jobs/'.format(username)
        request = urllib2.Request('{0}{1}{2}{3}'.format(self.url,
                                                        search_url,
                                                        job_id,
                                                        '/results?output_mode={0}&count=0'.format(outputmode)),
                                  headers=self.auth_header)
        connection = urllib2.urlopen(request)
        results = connection.read()
        connection.close()
        return results

    def endsession(self):
        """
        Deletes session key from Splunk
        :return:
        """
        request = urllib2.Request('{0}{1}{2}'.format(self.url, '/services/authentication/httpauth-tokens/', self.session_key),
                                  headers=self.auth_header)
        request.get_method = lambda: 'DELETE'
        connection = urllib2.urlopen(request)
        connection.close()
