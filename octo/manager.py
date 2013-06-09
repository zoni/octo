import octo
import octo.exceptions
import signal
import logging
from yapsy.PluginManager import PluginManager
try:
	import configparser
except ImportError:
	import ConfigParser as configparser  # Python 2

def exit_handler(signal, frame):
	"""Called by `run` upon receiving SIGINT"""
	logging.info("Interrupt received, shutting down")
	octo.manager.stop()


def run(plugin_dirs=[], block=False):
	"""
	Runs the ``octo`` application.

	Calling this function will initialize the `Manager` class and make it
	available as `octo.instance` so that plugins may import and interact with
	it.

	If block=True, this function will block until a SIGINT is received, either
	by the user hitting Ctrl+C or another process sending a SIGINT signal. If
	block=False then applications must ensure to call stop() appropriately
	themselves.
	"""
	if octo.instance is not None:
		raise octo.exceptions.AlreadyStartedError("main() can only be called once")
	octo.instance = Manager(plugin_dirs=plugin_dirs)
	octo.instance.start()
	if block:
		signal.signal(signal.SIGINT, exit_handler)
		signal.pause()


def stop():
	"""
	Stops the ``octo`` application.

	Calling this function will stop and cleanup `octo.instance`
	"""
	if octo.instance is None:
		raise octo.exceptions.NotStartedError("Octo does not seem to be started")
	octo.instance.stop()
	octo.instance = None


class Manager(object):
	"""
	This is the main ``octo`` application class.

	Normally, you would call `octo.main` instead of creating an instance of this
	class directly, as `octo.main` will make it available globally as `octo.instance`
	so plugins may interact with it.
	"""

	def __init__(self, plugin_dirs=[]):
		logging.info("Initializing with plugin directories: {!r}".format(plugin_dirs))
		self.plugin_manager = PluginManager(directories_list=plugin_dirs, plugin_info_ext='plugin')
		self.plugin_manager.collectPlugins()

	def get_plugins(self, include_inactive=False):
		"""
		Return a dictionary of loaded plugins

		Keys will consist of plugin names, with their values being the plugin
		instances (yapsy.PluginInfo.PluginInfo objects).

		When ``include_inactive`` is True, all collected plugins will be
		returned, otherwise only the activated plugins will be returned.
		"""
		if include_inactive:
			plugins = self.plugin_manager.getAllPlugins()
		else:
			plugins = [plugin for plugin in self.plugin_manager.getAllPlugins()
			           if hasattr(plugin, 'is_activated') and plugin.is_activated]
		return dict(zip([plugin.name for plugin in plugins], plugins))

	def activate_plugin(self, plugin_name):
		"""
		Activate the given plugin

		plugin_name should be the name of the plugin to be activated.
		"""
		self.plugin_manager.activatePluginByName(plugin_name)

	def deactivate_plugin(self, plugin_name):
		"""
		Deactivate the given plugin

		plugin_name should be the name of the plugin to be deactivated.
		"""
		self.plugin_manager.deactivatePluginByName(plugin_name)

	def call(self, plugin_name, func, args=[], kwargs={}):
		"""
		Call the given function on the given plugin object (specifed by plugin name)
		"""
		for plugin in self.get_plugins().values():
			if plugin.name == plugin_name:
				return getattr(plugin.plugin_object, func)(*args, **kwargs)
		raise octo.exceptions.NoSuchPluginError("The specified plugin isn't active or doesn't exist")

	def call_many(self, func, args=[], kwargs={}):
		"""
		Call the given function on all active plugins and return results as a dictionary

		The returned dictionary will have the form of {'plugin name': <function_result>}
		"""
		results = {}
		for plugin in self.get_plugins().values():
			try:
				logging.debug("Calling {} on plugin '{}'".format(func, plugin.name))
				results[plugin.name] = getattr(plugin.plugin_object, func)(*args, **kwargs)
			except AttributeError as e:
				logging.debug("'{}' has no attribute {}".format(plugin.name, func))
			except Exception as e:
				logging.exception("Exception while calling '{}' on '{}'".format(func, plugin.name))
				results[plugin.name] = e
		return results

	def start(self):
		"""Start and activate collected plugins

		A plugin will be activated when it has a config item 'Enable'
		under the section 'Config' with a value of True"""
		logging.debug("Activating plugins")
		for plugin in self.get_plugins(include_inactive=True).values():
			try:
				should_activate = plugin.details.getboolean('Config', 'Enable')
			except configparser.NoSectionError:
				should_activate = False
			if should_activate:
				logging.debug("Activating plugin {}".format(plugin.name))
				self.activate_plugin(plugin.name)
			else:
				logging.debug("Plugin {} not activated because config item Enable "
							  "is not True".format(plugin.name))
		logging.debug("Plugin activation done")
		return self

	def stop(self):
		"""Stop and deactivate loaded plugins"""
		logging.debug("Deactivating plugins")
		for plugin in self.get_plugins().values():
			logging.debug("Deactivating plugin {}".format(plugin.name))
			self.deactivate_plugin(plugin.name)
		logging.debug("Plugin deactivation done")
		return self

