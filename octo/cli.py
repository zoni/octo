import logging
import argparse
import octo


def main():
	"""
	Main entry point for octo CLI script.

	Normally, setuptools packaging will create a script which uses this function
	as it's entry point. (See entry_points in setup.py).
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--log-level',
	                    help="Log level to use. Valid values are NONE, "
	                         "DEBUG, INFO, WARNING, ERROR and CRITICAL",
	                    default="INFO")
	parser.add_argument('plugin_dirs',
	                    metavar='plugin-directory',
	                    help="Directory from which to load plugins",
	                    nargs='+')
	args = parser.parse_args()

	log_level = args.log_level.upper()
	if log_level != "NONE":
		logging.basicConfig(level=getattr(logging, log_level))

	octo.run(plugin_dirs=args.plugin_dirs, block=True)