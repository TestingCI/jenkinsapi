'''
System tests for `jenkinsapi.jenkins` module.
'''
import os
import time
import gzip
import shutil
import tempfile
import unittest

from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import JOB_WITH_ARTIFACTS
from jenkinsapi_tests.test_utils.random_strings import random_string


class TestPingerJob(BaseSystemTest):

    def test_invoke_job(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, JOB_WITH_ARTIFACTS)
        job.invoke(block=True)

        b = job.get_last_build()

        while b.is_running():
            time.sleep(1)

        artifacts = b.get_artifact_dict()
        self.assertIsInstance(artifacts, dict)

        text_artifact = artifacts['out.txt']
        binary_artifact = artifacts['out.gz']

        tempDir = tempfile.mkdtemp()

        try:
            # Verify that we can handle text artifacts
            text_artifact.save_to_dir(tempDir)
            readBackText = open(os.path.join(
                tempDir, text_artifact.filename), 'rb').read().strip()
            self.assertTrue(readBackText.startswith('PING localhost'))
            self.assertTrue(readBackText.endswith('ms'))

            # Verify that we can hande binary artifacts
            binary_artifact.save_to_dir(tempDir)
            readBackText = gzip.open(os.path.join(
                tempDir, 
                binary_artifact.filename,
                ), 'rb' ).read().strip()
            self.assertTrue(readBackText.startswith('PING localhost'))
            self.assertTrue(readBackText.endswith('ms'))
        finally:
            shutil.rmtree(tempDir)

if __name__ == '__main__':
    unittest.main()
