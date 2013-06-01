import unittest
import os
from yeller import Manager

PLUGIN_DIR = os.sep.join([os.path.dirname(os.path.realpath(__file__)), 'plugins'])


class BaseTests(unittest.TestCase):
	def test_yeller_has_no_plugins_when_pluginlist_empty(self):
		app = Manager()
		self.assertEqual(len(app.plugin_manager.getAllPlugins()), 0)

	def test_yeller_has_two_plugins_when_pluginlist_contains_test_plugin_dir(self):
		app = Manager(plugin_dirs=[PLUGIN_DIR])
		self.assertEqual(len(app.plugin_manager.getAllPlugins()), 2)

	def test_yeller_enables_only_enabled_plugins(self):
		app = Manager(plugin_dirs=[PLUGIN_DIR])
		enabled = 0
		for plugin in app.plugin_manager.getAllPlugins():
			if plugin.is_activated:
				enabled += 1

		self.assertEqual(enabled, 1)

	def test_yeller_get_plugins_returns_one_active(self):
		app = Manager(plugin_dirs=[PLUGIN_DIR])
		self.assertEqual(len(app.get_plugins(include_inactive=False)), 1)

	def test_yeller_get_plugins_returns_two_total(self):
		app = Manager(plugin_dirs=[PLUGIN_DIR])
		self.assertEqual(len(app.get_plugins(include_inactive=True)), 2)
