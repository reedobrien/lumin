import unittest
import pyramid.testing


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.config = pyramid.testing.setUp()

    def tearDown(self):
        pyramid.testing.tearDown()

    def test_register_mongodb_directive(self):
        import lumin
        self.config.include(lumin)

        from lumin.db import IMongoDBConnection
        connection = self.config.registry.queryUtility(IMongoDBConnection)
        self.assertTrue(connection is None)

        # Now, let's register a database connection
        self.config.register_mongodb('mongodb://localhost/')
        connection = self.config.registry.queryUtility(IMongoDBConnection)
        self.assertTrue(connection is not None)

    def test_register_memcached_directive(self):
        import lumin
        self.config.include(lumin)

        from lumin.db import IMemcachedClient
        client = self.config.registry.queryUtility(IMemcachedClient)
        self.assertTrue(client is None)

        # Now, let's register a memcached client
        self.config.register_memcached('http://localhost/')
        client = self.config.registry.queryUtility(IMemcachedClient)
        self.assertTrue(client is not None)
