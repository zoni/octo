import unittest
import octo
import octo.plugin
import octo.exceptions
import os
import signal
import yapsy
from nose.tools import raises
from mock import patch, MagicMock, create_autospec, call

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


def mockplugin(name="Mock plugin", enable=True):
	plugin = create_autospec(octo.plugin.OctoPlugin)
	plugin.name = name
	plugin.is_activated = False
	plugin.details = {'Config': {}}
	plugin.details['Config']['Enable'] = enable
	return plugin


class PluginMocksMixin(object):
	def mock_enable_plugin(self, name):
		for plugin in self.mock_plugin_list:
			if plugin.name == name:
				plugin.is_activated = True

	def mock_disable_plugin(self, name):
		for plugin in self.mock_plugin_list:
			if plugin.name == name:
				plugin.is_activated = False

	def mock_getPluginByName(self, name):
		for plugin in self.mock_plugin_list:
			if plugin.name == name:
				return plugin


class ManagerTests(unittest.TestCase, PluginMocksMixin):
	def setUp(self):
		octo.instance = None
		self.mock_plugin_list = [mockplugin('Plugin 1'),
		                         mockplugin('Plugin 2', enable=False)]

	def test_manager_has_no_plugins_when_pluginlist_empty(self):
		manager = octo.Manager().start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 0)

	def test_manager_has_two_plugins_when_pluginlist_contains_test_plugin_dir(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 2)

	def test_manager_enables_only_enabled_plugins(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(octo.Manager, 'activate_plugin', new_callable=lambda: self.mock_enable_plugin) as mock_method_1:
			manager.start()
		enabled = 0
		for plugin in manager.get_plugins().values():
			if plugin.is_activated:
				enabled += 1
		self.assertEqual(enabled, 1)

	def test_manager_get_plugins_returns_one_active(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(octo.Manager, 'activate_plugin', new_callable=lambda: self.mock_enable_plugin) as mock_method_1:
			manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 1)

	def test_manager_get_plugins_returns_two_total(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(octo.Manager, 'activate_plugin', new_callable=lambda: self.mock_enable_plugin) as mock_method_1:
			manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 2)

	def test_manager_get_plugins_returns_plugins_as_name_pluginobject_dict(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(octo.Manager, 'activate_plugin', new_callable=lambda: self.mock_enable_plugin) as mock_method_1:
			manager.start()
		plugins = manager.get_plugins(include_inactive=True)
		self.assertTrue('Plugin 1' in plugins.keys())
		self.assertTrue('Plugin 2' in plugins.keys())

	def test_manager_start_calls_activate(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(manager.plugin_manager, 'activatePluginByName') as mock_method:
			manager.start()
		self.assertEqual(mock_method.mock_calls, [call('Plugin 1')])

	def test_manager_start_calls_deactivate(self):
		manager = octo.Manager()
		manager.plugin_manager.getAllPlugins = lambda: self.mock_plugin_list
		with patch.object(octo.Manager, 'activate_plugin', new_callable=lambda: self.mock_enable_plugin) as mock_method_1:
			manager.start()
		with patch.object(manager.plugin_manager, 'deactivatePluginByName') as mock_method_2:
			manager.stop()
		self.assertEqual(mock_method_2.mock_calls, [call('Plugin 1')])

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

	def test_start_and_stop_sequence_with_plugins(self):
		octo.start(plugin_dirs=[PLUGIN_DIR])
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_before_start(self):
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_twice(self):
		octo.start(plugin_dirs=[])
		octo.stop()
		octo.stop()

