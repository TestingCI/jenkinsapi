import mock
import unittest

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job
from jenkinsapi.build import Build
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.exceptions import NoBuildData

class TestJob(unittest.TestCase):
    JOB_DATA = {"actions": [],
            "description": "test job",
            "displayName": "foo",
            "displayNameOrNull": None,
            "name": "foo",
            "url": "http://halob:8080/job/foo/",
            "buildable": True,
            "builds": [{"number": 3, "url": "http://halob:8080/job/foo/3/"},
           {"number": 2, "url": "http://halob:8080/job/foo/2/"},
                {"number": 1, "url": "http://halob:8080/job/foo/1/"}],
            "color": "blue",
            "firstBuild": {"number": 1, "url": "http://halob:8080/job/foo/1/"},
            "healthReport": [{"description": "Build stability: No recent builds failed.",
                             "iconUrl": "health-80plus.png", "score": 100}],
            "inQueue": False,
            "keepDependencies": False,
            "lastBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
            "lastCompletedBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
            "lastFailedBuild": None,
            "lastStableBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
            "lastSuccessfulBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
            "lastUnstableBuild": None,
            "lastUnsuccessfulBuild": None,
            "nextBuildNumber": 4,
            "property": [],
            "queueItem": None,
            "concurrentBuild": False,
            "downstreamProjects": [],
            "scm": {},
            "upstreamProjects": []}

    URL_DATA = {'http://halob:8080/job/foo/api/python/':JOB_DATA}

    BUILD_DATA = {
        'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
                                 'userId': None,
                                 'userName': 'anonymous'}]}],
        'artifacts': [],
        'building': False,
        'builtOn': '',
        'changeSet': {'items': [], 'kind': None},
        'culprits': [],
        'description': None,
        'duration': 106,
        'estimatedDuration': 106,
        'executor': None,
        'fullDisplayName': 'foo #1',
        'id': '2013-05-31_23-15-40',
        'keepLog': False,
        'number': 1,
        'result': 'SUCCESS',
        'timestamp': 1370042140000,
        'url': 'http://localhost:8080/job/foo/1/'}

    def fakeGetData(self, url, *args):
        try:
            return TestJob.URL_DATA[url]
        except KeyError:
            raise Exception("Missing data for %s" % url)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def setUp(self):

        self.J = mock.MagicMock()  # Jenkins object
        self.j = Job('http://halob:8080/job/foo/', 'foo', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        self.assertEquals(repr(self.j), '<jenkinsapi.job.Job foo>')

    def testName(self):
        with self.assertRaises(AttributeError):
            self.j.id()
        self.assertEquals(self.j.name, 'foo')

    def testNextBuildNumber(self):
        self.assertEquals(self.j.get_next_build_number(), 4)

    def test_special_urls(self):
        self.assertEquals(self.j.baseurl, 'http://halob:8080/job/foo')

        self.assertEquals(
            self.j.get_delete_url(), 'http://halob:8080/job/foo/doDelete')

        self.assertEquals(
            self.j.get_rename_url(), 'http://halob:8080/job/foo/doRename')

    def test_get_description(self):
        self.assertEquals(self.j.get_description(), 'test job')

    def test_get_build_triggerurl(self):
        self.assertEquals(
            self.j.get_build_triggerurl(), 'http://halob:8080/job/foo/build')

    def test_wrong__mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j._mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            ar.exception.message, 'Build parameters must be a dict')

    def test__mk_json_from_build_parameters(self):
        params = {'param1': 'value1', 'param2': 'value2'}
        ret = self.j.mk_json_from_build_parameters(build_params=params)
        self.assertTrue(isinstance(ret, str))
        self.assertEquals(ret,
                          '{"parameter": [{"name": "param2", "value": "value2"}, {"name": "param1", "value": "value1"}]}')

    def test_wrong_mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j.mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            ar.exception.message, 'Build parameters must be a dict')

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_wrong_field__build_id_for_type(self):
        with self.assertRaises(AssertionError):
            self.j._buildid_for_type('wrong')

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_good_buildnumber(self):
        ret = self.j.get_last_good_buildnumber()
        self.assertTrue(ret, 3)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_failed_buildnumber(self):
        with self.assertRaises(NoBuildData):
            self.j.get_last_failed_buildnumber()

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_buildnumber(self):
        ret = self.j.get_last_buildnumber()
        self.assertEquals(ret, 3)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_completed_buildnumber(self):
        ret = self.j.get_last_completed_buildnumber()
        self.assertEquals(ret, 3)

    def test_get_build_dict(self):
        ret = self.j.get_build_dict()
        self.assertTrue(isinstance(ret, dict))
        self.assertEquals(len(ret), 3)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_build_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_build_dict()

    def test_get_build_ids(self):
        # We don't want to deal with listreverseiterator here
        # So we convert result to a list
        ret = list(self.j.get_build_ids())
        self.assertTrue(isinstance(ret, list))
        self.assertEquals(len(ret), 3)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_revision_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_revision_dict()

    @mock.patch.object(Job, '_poll')
    @mock.patch.object(JenkinsBase, '_poll')
    def test_last_good_build(self, _poll_j, _poll):
        _poll.return_value = TestJob.JOB_DATA
        _poll_j.return_value = TestJob.BUILD_DATA
        build = self.j.get_last_good_build()
        self.assertIsInstance(build, Build)
        self.assertTrue(build.get_number(), 3)

    @mock.patch.object(Job, '_poll')
    @mock.patch.object(JenkinsBase, '_poll')
    def test_last_completed_build(self, _poll_j, _poll):
        _poll.return_value = TestJob.JOB_DATA
        _poll_j.return_value = TestJob.BUILD_DATA
        build = self.j.get_last_completed_build()
        self.assertIsInstance(build, Build)
        self.assertTrue(build.get_number(), 3)
if __name__ == '__main__':
    unittest.main()
