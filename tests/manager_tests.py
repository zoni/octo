import unittest
import octo
import octo.plugin
import octo.exceptions
import os
import signal
import yapsy
from nose.tools import raises
from mock import patch, Mock, MagicMock, create_autospec, call
try:
	from configparser import ConfigParser
except ImportError:
	from ConfigParser import SafeConfigParser as ConfigParser  # Python 2

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


def mockplugin(name="Mock plugin", enable=True, callback=None):
	"""Create and return mock plugin"""
	plugin = create_autospec(octo.plugin.OctoPlugin)
	plugin.name = name
	plugin.is_activated = False
	plugin.details = ConfigParser()
	plugin.details.add_section('Config')
	plugin.details.set('Config', 'Enable', str(enable))
	plugin.plugin_object = MagicMock()
	if callback is None:
		del plugin.plugin_object.callback
	else:
		plugin.plugin_object.callback = callback
	return plugin


class PluginManagerMock(Mock):
	"""Fake PluginManager class which returns predefined mock plugin objects"""

	def collectPlugins(self):
		self.plugin_list = [mockplugin('Plugin 0'),
		                    mockplugin('Plugin 1', callback=MagicMock(return_value="Called")),
		                    mockplugin('Plugin 2', enable=False),
		                    mockplugin('Plugin 3', callback=lambda: Exception("Boom!")),
		                    mockplugin('Plugin 4', callback=lambda *args, **kwargs: "{!r}\t{!r}".format(args, kwargs)),
		                    mockplugin('Plugin 5', callback=lambda: "Called")]

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

	def test_manager_enables_only_enabled_plugins(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		enabled = 0
		for plugin in manager.get_plugins().values():
			if plugin.is_activated:
				enabled += 1
		self.assertEqual(enabled, 5)

	def test_manager_get_plugins_returns_five_active(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=False)), 5)

	def test_manager_get_plugins_returns_six_total(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		self.assertEqual(len(manager.get_plugins(include_inactive=True)), 6)

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
		self.assertEqual(sorted(mock_method.mock_calls), sorted([call('Plugin 0'),
		                                                         call('Plugin 1'),
		                                                         call('Plugin 3'),
		                                                         call('Plugin 4'),
		                                                         call('Plugin 5')]))

	def test_manager_stop_calls_deactivate(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		with patch.object(manager.plugin_manager, 'deactivatePluginByName') as mock_method:
			manager.stop()
		self.assertEqual(sorted(mock_method.mock_calls), sorted([call('Plugin 0'),
		                                                         call('Plugin 1'),
		                                                         call('Plugin 3'),
		                                                         call('Plugin 4'),
		                                                         call('Plugin 5')]))

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

	def test_manager_call_many_calls_specified_function_on_active_plugins(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		manager.call_many('callback', args=[], kwargs={})
		plugin1 = manager.get_plugins()['Plugin 1']
		self.assertTrue(plugin1.plugin_object.callback.called)

	def test_manager_call_many_returns_dict_with_results(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		result = manager.call_many('callback')

		self.assertEqual(len(result), 4)
		self.assertEqual(result['Plugin 1'], "Called")
		self.assertTrue(isinstance(result['Plugin 3'], Exception))

	def test_manager_call_many_returns_exception_object_if_exception_occurred(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()
		result = manager.call_many('callback', kwargs={'one': 1, 'two': 2})
		self.assertTrue(isinstance(result['Plugin 5'], TypeError))

	def test_manager_call_many_passes_args_kwargs_correctly(self, plugin_manager_mock):
		manager = octo.Manager()
		manager.start()

		result = manager.call_many('callback', args=[1, 2, 3])
		self.assertEqual(result['Plugin 4'], "(1, 2, 3)\t{}")

		result = manager.call_many('callback', kwargs={'one': 1, 'two': 2})
		# Dictionaries aren't sorted so the keys may be represented with 'one' first or 'two' first depending
		# on various factors
		self.assertTrue(result['Plugin 4'] in ("()\t{'one': 1, 'two': 2}", "()\t{'two': 2, 'one': 1}"))

		result = manager.call_many('callback', args=[1, 2, 3], kwargs={'one': 1, 'two': 2})
		self.assertTrue(result['Plugin 4'] in ("(1, 2, 3)\t{'one': 1, 'two': 2}", "(1, 2, 3)\t{'two': 2, 'one': 1}"))


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
