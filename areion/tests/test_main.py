import unittest
from unittest.mock import Mock, patch, AsyncMock
from .. import (
    AreionServerBuilder,
    AreionServer,
    DEFAULT_HOST,
    DEFAULT_PORT,
    AREION_LOGO,
)


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


class TestAreionServer(unittest.TestCase):
    def setUp(self):
        self.router = Mock()
        self.orchestrator = Mock()
        self.logger = Mock()
        self.engine = Mock()
        self.static_dir = "/tmp"
        self.request_factory = Mock()
        self.server = AreionServer(
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            router=self.router,
            orchestrator=self.orchestrator,
            logger=self.logger,
            engine=self.engine,
            static_dir=self.static_dir,
            request_factory=self.request_factory,
        )

    @patch("asyncio.run")
    @patch.object(AreionServer, "start", new_callable=AsyncMock)
    def test_run(self, mock_start, mock_asyncio_run):
        self.server.run()
        mock_asyncio_run.assert_called_once()

    @patch("asyncio.run", side_effect=KeyboardInterrupt)
    def test_run_keyboard_interrupt(self, mock_asyncio_run):
        self.server.stop = Mock()
        self.server.run()
        self.server.stop.assert_called_once()

    @patch("asyncio.run", side_effect=SystemExit)
    def test_run_system_exit(self, mock_asyncio_run):
        self.server.stop = Mock()
        self.server.run()
        self.server.stop.assert_called_once()

    @patch("builtins.print")
    @patch("asyncio.Event.wait", new_callable=AsyncMock)
    @patch("..main.HttpServer.run", new_callable=AsyncMock)
    async def test_start(self, mock_http_server_run, mock_event_wait, mock_print):
        self.logger.info = Mock()
        self.logger.debug = Mock()
        self.server._start_orchestrator_in_thread = Mock()
        self.server.http_server = Mock()
        self.server.http_server.run = mock_http_server_run

        await self.server.start()

        mock_print.assert_called_once_with(AREION_LOGO)
        self.logger.info.assert_any_call(
            f"Starting server on {self.server.host}:{self.server.port}"
        )
        self.logger.info.assert_any_call(
            f"Server running on http://{self.server.host}:{self.server.port}"
        )
        self.logger.debug.assert_called_once_with(
            f"Available Routes and Handlers: {self.router.routes}"
        )
        self.server._start_orchestrator_in_thread.assert_called_once()
        mock_event_wait.assert_called_once()

    @patch("asyncio.get_event_loop")
    @patch("..main.HttpServer.stop", new_callable=AsyncMock)
    async def test_shutdown(self, mock_http_server_stop, mock_get_event_loop):
        server_task = AsyncMock()
        self.server.http_server = Mock()
        self.server.http_server.stop = mock_http_server_stop
        self.orchestrator.shutdown = Mock()
        mock_get_event_loop.return_value.run_in_executor = AsyncMock()

        await self.server.shutdown(server_task)

        mock_http_server_stop.assert_called_once()
        server_task.assert_awaited_once()
        mock_get_event_loop.return_value.run_in_executor.assert_awaited_once_with(
            None, self.orchestrator.shutdown
        )
        self.logger.info.assert_any_call("Orchestrator shutdown complete.")

    def test_stop(self):
        self.server._loop.call_soon_threadsafe = Mock()
        self.server.stop()
        self.server._loop.call_soon_threadsafe.assert_called_once_with(
            self.server._shutdown_event.set
        )

    def test_start_orchestrator_in_thread(self):
        self.server._start_orchestrator = Mock()
        self.server._start_orchestrator_in_thread()
        self.assertTrue(self.server._start_orchestrator.called)

    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch(
        "builtins.open", new_callable=unittest.mock.mock_open, read_data=b"file content"
    )
    @patch("mimetypes.guess_type", return_value=("text/plain", None))
    async def test_static_file_handler(
        self, mock_guess_type, mock_open, mock_isfile, mock_exists
    ):
        request = Mock()
        filename = "test.txt"
        response = await self.server._static_file_handler(request, filename)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"file content")
        self.assertEqual(response.headers["Content-Type"], "text/plain")

    @patch("os.path.exists", return_value=False)
    async def test_static_file_handler_file_not_found(self, mock_exists):
        request = Mock()
        filename = "test.txt"
        response = await self.server._static_file_handler(request, filename)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, "File Not Found")


if __name__ == "__main__":
    unittest.main()
