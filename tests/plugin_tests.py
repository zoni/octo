import unittest
from yapsy.IPlugin import IPlugin
from octo.plugin import OctoPlugin
from mock import patch


class OctoPluginTests(unittest.TestCase):
	def test_octoplugin_is_subclass_of_yapsy_iplugin(self):
		self.assertTrue(issubclass(OctoPlugin, IPlugin))

	def test_activate_calls_super(self):
		with patch.object(IPlugin, 'activate', return_value=None) as mock_method:
			OctoPlugin().activate()
		mock_method.assert_called_once_with()

	def test_deactivate_calls_super(self):
		with patch.object(IPlugin, 'deactivate', return_value=None) as mock_method:
			OctoPlugin().deactivate()
		mock_method.assert_called_once_with()
