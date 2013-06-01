from yapsy.PluginManager import PluginManager


class Manager(object):
	"""
	This is the main ``octo`` application class.
	"""

	def __init__(self, plugin_dirs=[]):
		plugin_manager = PluginManager(directories_list=plugin_dirs, plugin_info_ext='plugin')
		self.plugin_manager = plugin_manager

		plugin_manager.collectPlugins()
		for plugin in plugin_manager.getAllPlugins():
			try:
				should_activate = plugin.details['Config']['Enable']
			except KeyError:
				should_activate = False
			if should_activate:
				plugin_manager.activatePluginByName(plugin.name)

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
