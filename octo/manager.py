import octo
import signal
import logging
from yapsy.PluginManager import PluginManager


def exit_handler(signal, frame):
	"""Called by `main` upon receiving SIGINT"""
	logging.info("Interrupt received, shutting down")


def main(plugin_dirs=[], block=False):
	"""
	Starts the ``octo`` application.

	Calling this function will initialize the `Manager` class and make it
	available as `octo.instance` so that plugins may import and interact with
	it.

	If block=True, this function will block until a SIGINT is received, either
	by the user hitting Ctrl+C or another process sending a SIGINT signal.
	"""
	if octo.instance is not None:
		raise Exception("main() can only be called once")
	octo.instance = Manager(plugin_dirs=plugin_dirs)
	if block:
		signal.signal(signal.SIGINT, exit_handler)
		signal.pause()


class Manager(object):
	"""
	This is the main ``octo`` application class.

	Normally, you would call `octo.main` instead of creating an instance of this
	class directly, as `octo.main` will make it available globally as `octo.instance`
	so plugins may interact with it.
	"""

	def __init__(self, plugin_dirs=[]):
		plugin_manager = PluginManager(directories_list=plugin_dirs, plugin_info_ext='plugin')
		self.plugin_manager = plugin_manager

		plugin_manager.collectPlugins()
		logging.info("Intializing with plugin directories {!r}".format(plugin_dirs))
		for plugin in plugin_manager.getAllPlugins():
			try:
				should_activate = plugin.details['Config']['Enable']
			except KeyError:
				should_activate = False
			if should_activate:
				logging.debug("Activating plugin {}".format(plugin.name))
				plugin_manager.activatePluginByName(plugin.name)
			else:
				logging.debug("Plugin {} not activated because config item Enable "
				              "is not True".format(plugin.name))

	def get_plugins(self, include_inactive=False):
		"""
		Return a list of loaded plugins

		When ``include_inactive`` is True, return all plugins, else return
		only activated plugins.
		"""
		if include_inactive:
			return self.plugin_manager.getAllPlugins()
		else:
			return [plugin for plugin in self.plugin_manager.getAllPlugins()
			        if hasattr(plugin, 'is_activated') and plugin.is_activated]
