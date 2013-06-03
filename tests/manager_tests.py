import unittest
import octo
import octo.plugin
import octo.exceptions
import os
import signal
import yapsy
from nose.tools import raises
from mock import patch, Mock, create_autospec, call

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


def mockplugin(name="Mock plugin", enable=True):
	"""Create and return mock plugin"""
	plugin = create_autospec(octo.plugin.OctoPlugin)
	plugin.name = name
	plugin.is_activated = False
	plugin.details = {'Config': {}}
	plugin.details['Config']['Enable'] = enable
	return plugin


class PluginManagerMock(Mock):
	"""Fake PluginManager class which returns predefined mock plugin objects"""

	def collectPlugins(self):
		self.plugin_list = [mockplugin('Plugin 1'), mockplugin('Plugin 2', enable=False)]

	def getAllPlugins(self):
		return self.plugin_list

	def activatePluginByName(self, name, category=None):
		if category is not None:
			raise NotImplementedError()
		for plugin in self.plugin_list:
			if plugin.name == name:
				plugin.activate()
				plugin.is_activated = True
				return plugin
		return None

	def deactivatePluginByName(self, name, category=None):
		if category is not None:
			raise NotImplementedError()
		for plugin in self.plugin_list:
			if plugin.name == name:
				plugin.deactivate()
				plugin.is_activated = False
				return plugin
		return None

	def getPluginByName(self, name, category=None):
		if category is not None:
			raise NotImplementedError()
		for plugin in self.plugin_list:
			if plugin.name == name:
				return plugin
		return None


@patch('octo.manager.PluginManager', new_callable=PluginManagerMock)
class ManagerTests(unittest.TestCase):
	def setUp(self):
		octo.instance = None
		self.mock_plugin_list = [mockplugin('Plugin 1'),
		                         mockplugin('Plugin 2', enable=False)]

	def test_manager_enables_only_enabled_plugins(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		enabled = 0
		for plugin in manager.get_plugins().values():
			if plugin.is_activated:
				enabled += 1
		self.assertEqual(enabled, 1)

	def test_manager_get_plugins_returns_one_active(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 1)

	def test_manager_get_plugins_returns_two_total(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 2)

	def test_manager_get_plugins_returns_plugins_as_name_pluginobject_dict(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		plugins = manager.get_plugins(include_inactive=True)
		self.assertTrue('Plugin 1' in plugins.keys())
		self.assertTrue('Plugin 2' in plugins.keys())

	def test_manager_start_calls_activate(self, plugin_manager_mock):
		manager = octo.Manager()
		with patch.object(manager.plugin_manager, 'activatePluginByName') as mock_method:
			manager.start()
		self.assertEqual(mock_method.mock_calls, [call('Plugin 1')])

	def test_manager_start_calls_deactivate(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		with patch.object(manager.plugin_manager, 'deactivatePluginByName') as mock_method:
			manager.stop()
		self.assertEqual(mock_method.mock_calls, [call('Plugin 1')])

	def test_start_initializes_manager(self, plugin_manager_mock):
		octo.start(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))

	@raises(octo.exceptions.AlreadyStartedError)
	def test_start_raises_exception_when_called_twice(self, plugin_manager_mock):
		octo.start(plugin_dirs=[])
		octo.start(plugin_dirs=[])

	@patch('signal.signal')
	@patch('signal.pause')
	def test_start_can_block_until_sigint_received(self, pause_mock, signal_mock, plugin_manager_mock):
		octo.start(plugin_dirs=[], block=True)
		signal_mock.assert_called_with(signal.SIGINT, octo.manager.exit_handler)
		self.assertTrue(pause_mock.called)

	def test_stop_deletes_manager(self, plugin_manager_mock):
		octo.start(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))
		octo.stop()
		self.assertEqual(octo.instance, None)

	def test_start_and_stop_sequence_with_plugins(self, plugin_manager_mock):
		octo.start(plugin_dirs=[PLUGIN_DIR])
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_before_start(self, plugin_manager_mock):
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_twice(self, plugin_manager_mock):
		octo.start(plugin_dirs=[])
		octo.stop()
		octo.stop()


class ManagerIntegrationTests(unittest.TestCase):
	def test_manager_has_no_plugins_when_pluginlist_empty(self):
		manager = octo.Manager().start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 0)

	def test_manager_has_two_plugins_when_pluginlist_contains_test_plugin_dir(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.plugin_manager.getAllPlugins()), 2)
