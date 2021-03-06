import os
from unittest2 import TestCase

from addonreg.backends import RawSQLBackend, MemcachedBackend, PythonBackend


class BackendBase(object):

    def setUp(self):
        self.backend = self.get_backend()

        self.guids = (u'{9c51bd27-6ed8-4000-a2bf-36cb95c0c947}',
                      u'id@example.com')
        self.hashes = (u'31f7a65e315586ac198bd798b6629ce4903d0899476d5741a9f32'
                       'e2e521b6a66', u'15586ac198bd798b6629ce4903d0899476d57',
                       '41a9f3231f7a65e31')

    def _register_hash(self, idx):
        self.backend.register_hash(self.guids[idx], self.hashes[idx])

    def test_read(self):
        self._register_hash(0)
        self.assertTrue(self.backend.hash_exists(self.guids[0],
                                                 self.hashes[0]))
        self.assertFalse(self.backend.hash_exists(self.guids[1],
                                                  self.hashes[1]))

    def test_write(self):
        self.backend.register_hash(self.guids[0], self.hashes[0])
        self.assertTrue(self.backend.hash_exists(self.guids[0],
                        self.hashes[0]))

    def test_hashes_exists(self):
        [self._register_hash(idx) for idx in range(len(self.guids))]
        resp = self.backend.hashes_exists(zip(self.guids, self.hashes))

        self.assertEquals(len(resp), 2)
        self.assertIn((self.guids[0], self.hashes[0]), resp)
        self.assertIn((self.guids[1], self.hashes[1]), resp)


class TestSQLBackend(BackendBase, TestCase):
    # By default, the tests are using SQLite in order to be faster.
    # You can change that (if you want to run the tests against a real database
    # for instance) by changing the SQLURI environment variable.
    _SQLURI = os.environ.get('SQLURI', 'sqlite:////tmp/wimms')

    def get_backend(self):
        backend = RawSQLBackend(sqluri=self._SQLURI, create_tables=True)
        self._sqlite = backend._engine.driver == 'pysqlite'
        return backend

    def tearDown(self):
        if self._sqlite:
            filename = self.backend.sqluri.split('sqlite://')[-1]
            if os.path.exists(filename):
                os.remove(filename)
        else:
            self.backend._safe_execute('drop table hashes;')

    def _register_hash(self, idx):
        # Let's create a hash to test if we're able to read it back.
        self.backend._safe_execute(
            """INSERT INTO hashes (addonid, sha256, registered)
               VALUES ("%s", "%s", 1)""" % (self.guids[idx], self.hashes[idx]))


class TestPythonBackend(BackendBase, TestCase):
    def get_backend(self):
        return PythonBackend()


class TestMemcachedBackend(BackendBase, TestCase):
    def get_backend(self):
        server = 'localhost:11211'
        return MemcachedBackend({'memcached_server': server})

    def tearDown(self):
        for guid, sha in zip(self.guids, self.hashes):
            self.backend._client.delete(self.backend._key(guid, sha))
