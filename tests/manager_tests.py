import unittest
import octo
import octo.plugin
import octo.exceptions
import os
import signal
import yapsy
from nose.tools import raises
from mock import patch, Mock, MagicMock, create_autospec, call

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


def mockplugin(name="Mock plugin", enable=True, omit_callback=False):
	"""Create and return mock plugin"""
	plugin = create_autospec(octo.plugin.OctoPlugin)
	plugin.name = name
	plugin.is_activated = False
	plugin.details = {'Config': {}}
	plugin.details['Config']['Enable'] = enable
	if not omit_callback:
		plugin.callback = MagicMock(return_value="Called")
	return plugin


class PluginManagerMock(Mock):
	"""Fake PluginManager class which returns predefined mock plugin objects"""

	def collectPlugins(self):
		self.plugin_list = [mockplugin('Plugin 0', omit_callback=True),
		                    mockplugin('Plugin 1'),
		                    mockplugin('Plugin 2', enable=False)]

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
		self.assertEqual(enabled, 2)

	def test_manager_get_plugins_returns_two_active(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 2)

	def test_manager_get_plugins_returns_three_total(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 3)

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
		self.assertEqual(sorted(mock_method.mock_calls), sorted([call('Plugin 1'), call('Plugin 0')]))

	def test_manager_stop_calls_deactivate(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		with patch.object(manager.plugin_manager, 'deactivatePluginByName') as mock_method:
			manager.stop()
		self.assertEqual(sorted(mock_method.mock_calls), sorted([call('Plugin 1'), call('Plugin 0')]))

	def test_start_initializes_manager_stop_resets_instance(self, plugin_manager_mock):
		self.assertEqual(octo.instance, None)
		octo.run(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))
		octo.stop()
		self.assertEqual(octo.instance, None)

	def test_start_calls_instance_start(self, plugin_manager_mock):
		with patch.object(octo.manager, 'Manager') as mock_method:
			octo.run(plugin_dirs=[])
		self.assertEqual(mock_method.mock_calls, [call(plugin_dirs=[]), call().start()])

	def test_stop_calls_instance_stop(self, plugin_manager_mock):
		octo.run(plugin_dirs=[])
		with patch.object(octo, 'instance') as mock_method:
			octo.stop()
		self.assertTrue(mock_method.stop.called)

	@raises(octo.exceptions.AlreadyStartedError)
	def test_start_raises_exception_when_called_twice(self, plugin_manager_mock):
		octo.run(plugin_dirs=[])
		octo.run(plugin_dirs=[])

	@patch('signal.signal')
	@patch('signal.pause')
	def test_start_can_block_until_sigint_received(self, pause_mock, signal_mock, plugin_manager_mock):
		octo.run(plugin_dirs=[], block=True)
		signal_mock.assert_called_with(signal.SIGINT, octo.manager.exit_handler)
		self.assertTrue(pause_mock.called)

	def test_stop_deletes_manager(self, plugin_manager_mock):
		octo.run(plugin_dirs=[])
		self.assertTrue(isinstance(octo.instance, octo.Manager))
		octo.stop()
		self.assertEqual(octo.instance, None)

	def test_start_and_stop_sequence_with_plugins(self, plugin_manager_mock):
		octo.run(plugin_dirs=[PLUGIN_DIR])
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_before_start(self, plugin_manager_mock):
		octo.stop()

	@raises(octo.exceptions.NotStartedError)
	def test_stop_raises_exception_when_called_twice(self, plugin_manager_mock):
		octo.run(plugin_dirs=[])
		octo.stop()
		octo.stop()

	@patch('octo.manager.stop')
	def test_exit_handler_calls_stop(self, stop_mock, plugin_manager_mock):
		signal = MagicMock()
		frame = MagicMock()
		octo.manager.exit_handler(signal, frame)
		self.assertTrue(stop_mock.called)

	@raises(octo.exceptions.NotStartedError)
	def test_exit_handler_raises_error_when_called_while_no_instance_active(self, plugin_manager_mock):
		signal = MagicMock()
		frame = MagicMock()
		octo.manager.exit_handler(signal, frame)

	def test_manager_call_calls_specified_function_on_active_plugins(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		manager.call('callback', args=[], kwargs={})
		plugin1 = manager.get_plugins()['Plugin 1']
		self.assertTrue(plugin1.callback.called)

	def test_manager_call_returns_dict_with_results(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		result = manager.call('callback', args=[], kwargs={})
		self.assertEqual(result, {'Plugin 1': "Called"})

class ManagerIntegrationTests(unittest.TestCase):
	def test_manager_has_no_plugins_when_pluginlist_empty(self):
		manager = octo.Manager().start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 0)

	def test_manager_get_plugins_returns_one_active(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 1)

	def test_manager_get_plugins_returns_two_total(self):
		manager = octo.Manager(plugin_dirs=[PLUGIN_DIR]).start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 2)
