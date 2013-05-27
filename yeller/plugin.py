from yapsy.IPlugin import IPlugin


class YellerPlugin(IPlugin):
	def activate(self):
		"""
		Override this method to run custom code on plugin activation
		"""
		super(YellerPlugin, self).activate()

	def deactivate(self):
		"""
		Override this method to run custom code on plugin deactivation
		"""
		super(YellerPlugin, self).deactivate()
