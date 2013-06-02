import unittest
import octo
import octo.exceptions
import os
import signal
from nose.tools import raises
from mock import patch

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


class ManagerTests(unittest.TestCase):
	def setUp(self):
		octo.instance = None

	def test_manager_has_no_plugins_when_pluginlist_empty(self):
		manager = octo.Manager().start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 0)

	def test_manager_has_two_plugins_when_pluginlist_contains_test_plugin_dir(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 2)

	def test_manager_enables_only_enabled_plugins(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		enabled = 0
		for plugin in manager.plugin_manager.getAllPlugins():
			if plugin.is_activated:
				enabled += 1
		self.assertEqual(enabled, 1)

	def test_manager_get_plugins_returns_one_active(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 1)

	def test_manager_get_plugins_returns_two_total(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 2)

	def test_start_initializes_manager(self):
		octo.start(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))

	@raises(octo.exceptions.AlreadyStartedError)
	def test_start_raises_exception_when_called_twice(self):
		octo.start(plugin_dirs=[])
		octo.start(plugin_dirs=[])

	@patch('signal.signal')
	@patch('signal.pause')
	def test_start_can_block_until_sigint_received(self, pause_mock, signal_mock):
		octo.start(plugin_dirs=[], block=True)
		signal_mock.assert_called_with(signal.SIGINT, octo.manager.exit_handler)
		self.assertTrue(pause_mock.called)

	def test_stop_deletes_manager(self):
		octo.start(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))
		octo.stop()
		self.assertEqual(octo.instance, None)

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_twice(self):
		octo.start(plugin_dirs=[])
		octo.stop()
		octo.stop()

