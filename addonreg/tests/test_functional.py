import os

from unittest2 import TestCase
import webtest


HERE = os.path.dirname(os.path.abspath(__file__))


class FunctionalTest(TestCase):

    def setUp(self):
        self.app = webtest.TestApp("config:tests.ini", relative_to=HERE)
        self.backend = self.app.app.registry.backend

    def tearDown(self):
        self.backend.empty()

    def test_get_registered_addon(self):
        addon_id = 'id@example.com'
        hash_ = '0c27ec47b62e20a20a563aaada9dfa663d76a76f'

        self.backend.register_hash(addon_id, hash_)

        resp = self.app.get('/addon/{addon_id}/{hash}'.format(
            addon_id=addon_id, hash=hash_))

        self.assertDictEqual(resp.json, {'registered': True,
                                         'sha256': hash_,
                                         'id': addon_id})

    def test_get_unregistered_addon(self):
        addon_id = 'id@example.com'
        hash_ = '0c27ec47b62e20a20a563aaada9dfa663d76a76f'

        # Here, the hash doesn't exist for this addon.
        resp = self.app.get('/addon/{addon_id}/{hash}'.format(
            addon_id=addon_id, hash=hash_))

        self.assertDictEqual(resp.json, {'registered': False,
                                         'sha256': hash_,
                                         'id': addon_id})