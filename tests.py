import os
import requests
import json
import datetime
__author__ = 'sekely'


class BotTestError(Exception):
    pass


class TestCase(object):
    test_types = ['pid', 'rest', 'file', 'custom']
    PASS = 'Pass!'
    FAILED = 'Failed!'

    def __init__(self, test_type, name=None, schedule=30):
        if test_type not in self.test_types:
            raise BotTestError("illegal test type")
        self.test_type = test_type
        self.name = name
        self.schedule = schedule
        self.last_run = None
        self.watch = True

    def test(self):
        raise BotTestError("test not implemented")

    def validate(self):
        if not self.watch:
            return False
        if self.last_run and datetime.datetime.now() - self.last_run < datetime.timedelta(seconds=self.schedule):
            return False
        return True

    def run(self):
        try:
            res = self.test()
        except Exception as e:
            res = False
        self.last_run = datetime.datetime.now()
        return self.PASS if res else self.FAILED


class PidTest(TestCase):
    PASS = 'Process running'
    FAILED = 'Not exist!'

    def __init__(self, pid, schedule=60):
        super(PidTest, self).__init__('pid', pid, schedule)
        self.pid = int(pid)

    def test(self):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(self.pid, 0)
            return True
        except OSError:
            return False


class RestTest(TestCase):

    def __init__(self, endpoint, schedule=60, params=None):
        super(RestTest, self).__init__('rest', endpoint, schedule)
        self.endpoint = endpoint
        self.params = params if params else {}

    def test(self):
        r = requests.get(self.endpoint, params=self.params, verify=False)
        resp = json.loads(r.text)
        return resp['status']


class FileTest(TestCase):

    def __init__(self, file_path, schedule=1):
        super(FileTest, self).__init__('rest', file_path, schedule)
        self.path = file_path


def test_factory(test_type):
    if test_type == 'pid':
        return PidTest
    if test_type == 'rest':
        return RestTest
    if test_type == 'file':
        return FileTest
    if test_type == 'custom':
        return TestCase
    raise BotTestError('test type %s not supported' % test_type)

test_list = {}

# you can create test instance and add it to the list here
# example:
# toll_road_test_1 = RestTest('http://localhost:5000/analyzer/describe')
# toll_road_test_1.name = 'analyzer_test'
# toll_road_test_2 = RestTest('http://localhost:5000/collector/describe')
# toll_road_test_2.name = 'collector_test'
#
# test_list = {
#     toll_road_test_1.name: toll_road_test_1,
#     toll_road_test_2.name: toll_road_test_2,
#     }
