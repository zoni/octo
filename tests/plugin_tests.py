import unittest
from yapsy.IPlugin import IPlugin
from yeller.plugin import YellerPlugin
from mock import patch

class YellerPluginTests(unittest.TestCase):
	def test_yellerplugin_is_subclass_of_yapsy_iplugin(self):
		self.assertTrue(issubclass(YellerPlugin, IPlugin))

	def test_activate_calls_super(self):
		with patch.object(IPlugin, 'activate', return_value=None) as mock_method:
			YellerPlugin().activate()
		mock_method.assert_called_once_with()

	def test_deactivate_calls_super(self):
		with patch.object(IPlugin, 'deactivate', return_value=None) as mock_method:
			YellerPlugin().deactivate()
		mock_method.assert_called_once_with()
