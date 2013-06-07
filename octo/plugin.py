from yapsy.IPlugin import IPlugin


class OctoPlugin(IPlugin):
	def activate(self):
		"""
		Run plugin initialization code.

		Do not override this method in plugins. Instead, override the on_activation
		method instead.
		"""
		super(OctoPlugin, self).activate()
		self.on_activation()

	def deactivate(self):
		"""
		Run plugin de-initialization code.

		Do not override this method in plugins. Instead, override the on_deactivation
		method instead.
		"""
		self.on_deactivation()
		super(OctoPlugin, self).deactivate()

	def on_activation(self):
		"""
		Override this method to run code on plugin activation.

		This method may be safely overridden without calling Super.
		"""
		pass

	def on_deactivation(self):
		"""
		Override this method to run code on plugin deactivation.

		This method may be safely overridden without calling Super.
		"""
		pass
