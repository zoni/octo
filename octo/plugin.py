from yapsy.IPlugin import IPlugin


class OctoPlugin(IPlugin):
	def activate(self):
		"""
		Override this method to run custom code on plugin activation
		"""
		super(OctoPlugin, self).activate()

	def deactivate(self):
		"""
		Override this method to run custom code on plugin deactivation
		"""
		super(OctoPlugin, self).deactivate()
