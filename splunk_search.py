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

import json

from splunkhelpers import SPLK as SPLK

if __name__ == '__main__':
    import time
    base_url = ''
    username = ''
    password = ''
    search_query = 'search index=zon affected_env{}=val_300 operation="*" change_event_id="*" earliest=-5h sourcetype=zmq_access| stats count'
    # output_mode can be either csv, raw or json
    #output_mode = 'csv'
    output_mode = 'json'
    #output_mode = 'xml'

    splunk = SPLK(url=base_url,
                  username=username,
                  password=password)
    splunk.requestsession()
    #print splunk.alljobsdetails()
    splunk.createjob(search_query)

    done = False

    while not done:
        splunk.jobdetails(splunk.job_id)
        # Raise an exception if job is zombie or failed state
        if splunk.jobstatus() == 'DONE':
            done = True
        if splunk.jobstatus() == 'FAILED':
            raise Exception('current search job failed due to a fatal error')

        if not done:
            print 'not done'
            time.sleep(2)

    results = splunk.getresults(splunk.job_id, 'json')
    results = json.loads(results)
    print results
    i = 0
    for result in results['results']:
        print result
    splunk.endsession()
