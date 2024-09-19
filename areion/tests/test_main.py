import unittest
from unittest.mock import Mock
from areion import AreionServerBuilder, HttpRequestFactory, AreionServer

## TODO: Implement tests for the AreionServer class

class TestAreionServerBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = AreionServerBuilder()

    def test_with_host(self):
        self.builder.with_host("127.0.0.1")
        self.assertEqual(self.builder.host, "127.0.0.1")

    def test_with_host_invalid(self):
        with self.assertRaises(ValueError):
            self.builder.with_host(123)

    def test_with_port(self):
        self.builder.with_port(9090)
        self.assertEqual(self.builder.port, 9090)

    def test_with_port_invalid(self):
        with self.assertRaises(ValueError):
            self.builder.with_port("not_a_port")

    def test_with_router(self):
        router = Mock()
        router.add_route = Mock()
        router.get_handler = Mock()
        self.builder.with_router(router)
        self.assertEqual(self.builder.router, router)

    def test_with_router_empty(self):
        router = Mock()
        self.builder.with_router(router)

    def test_with_orchestrator(self):
        orchestrator = Mock()
        orchestrator.start = Mock()
        orchestrator.submit_task = Mock()
        orchestrator.run_tasks = Mock()
        orchestrator.shutdown = Mock()
        self.builder.with_orchestrator(orchestrator)
        self.assertEqual(self.builder.orchestrator, orchestrator)

    def test_with_orchestrator_invalid(self):
        orchestrator = Mock()
        del orchestrator.start
        with self.assertRaises(ValueError):
            self.builder.with_orchestrator(orchestrator)

    def test_with_logger(self):
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()
        logger.debug = Mock()
        self.builder.with_logger(logger)
        self.assertEqual(self.builder.logger, logger)

    def test_with_logger_invalid(self):
        logger = Mock()
        del logger.info
        with self.assertRaises(ValueError):
            self.builder.with_logger(logger)

    def test_with_engine(self):
        engine = Mock()
        engine.render = Mock()
        self.builder.with_engine(engine)
        self.assertEqual(self.builder.engine, engine)

    def test_with_engine_invalid(self):
        engine = Mock()
        del engine.render
        with self.assertRaises(ValueError):
            self.builder.with_engine(engine)

    def test_with_static_dir(self):
        static_dir = "/tmp"
        self.builder.with_static_dir(static_dir)
        self.assertEqual(self.builder.static_dir, static_dir)

    def test_with_static_dir_invalid(self):
        with self.assertRaises(ValueError):
            self.builder.with_static_dir(123)

        with self.assertRaises(ValueError):
            self.builder.with_static_dir("/non_existent_dir")

    def test_build(self):
        router = Mock()
        self.builder.with_router(router)

        server = self.builder.build()
        self.assertIsInstance(server, AreionServer)
        self.assertEqual(server.host, self.builder.host)
        self.assertEqual(server.port, self.builder.port)
        self.assertEqual(server.router, self.builder.router)
        self.assertEqual(server.orchestrator, self.builder.orchestrator)
        self.assertEqual(server.logger, self.builder.logger)
        self.assertEqual(server.engine, self.builder.engine)
        self.assertEqual(server.static_dir, self.builder.static_dir)

    def test_build_without_router(self):
        with self.assertRaises(ValueError):
            self.builder.build()


if __name__ == "__main__":
    unittest.main()
