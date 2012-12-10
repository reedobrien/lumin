import unittest

import pyramid.testing

from lumin.testing import Connection


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.config = pyramid.testing.setUp()

    def tearDown(self):
        pyramid.testing.tearDown()

    def _includelumin(self):
        import lumin
        self.config.include(lumin)

    def _registerdb(self):
        conn = Connection()
        self.config.registry.settings['mongodb.db_name'] = 'frozznob'
        self.config.registry.settings['mongodb.connection_class'] = 'Connection'
        self.config.register_mongodb(conn=conn)

    def test_register_mongodb_directive(self):
        self._includelumin()

        from lumin.db import IMongoDBConnection
        connection = self.config.registry.queryUtility(IMongoDBConnection)
        self.assertTrue(connection is None)

        # Now, let's register a database connection
        self._registerdb()
        connection = self.config.registry.queryUtility(IMongoDBConnection)
        self.assertTrue(connection is not None)

    def test_get_mongodb(self):
        self._includelumin()
        self._registerdb()
        from lumin.db import get_mongodb
        from lumin.testing import Database
        conn = get_mongodb(self.config.registry)
        self.assertTrue(isinstance(conn, Database))

    def test_add_mongodb(self):
        self._includelumin()
        self._registerdb()
        import pyramid
        request = pyramid.testing.DummyRequest(
            path='/',
            )
        import pyramid
        # fire an event to call add_mongodb
        self.config.registry.handle(pyramid.events.NewRequest(request))
        self.assertTrue(hasattr(request, 'db'))


class TestIncludeMe(unittest.TestCase):
    def setUp(self):
        self.config = pyramid.testing.setUp()

    def tearDown(self):
        pyramid.testing.tearDown()

    def test_includeme(self):
        import lumin
        self.assertFalse(hasattr(self.config, 'register_mongodb'))
        lumin.includeme(self.config)
        self.assertTrue(hasattr(self.config, 'register_mongodb'))


class TestConnectionFromSettings(unittest.TestCase):
    def setUp(self):
        self.config = pyramid.testing.setUp()

    def tearDown(self):
        pyramid.testing.tearDown()

    def _call_fut(self):
        from lumin.db import connection_from_settings
        import mongomock
        settings = {"mongodb.connection_class": "Connection"}
        return connection_from_settings(settings, pymongo=mongomock)

    def test_it(self):
        inst = self._call_fut()
        from mongomock import Connection
        self.assertTrue(isinstance(inst, Connection))
