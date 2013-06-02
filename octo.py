#!/usr/bin/env python

import logging
import argparse
import octo

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--log-level',
	                    help="Log level to use. Valid values are NONE, "
	                         "DEBUG, INFO, WARNING, ERROR and CRITICAL",
	                    default="INFO")
	parser.add_argument('-p', '--plugin-dir',
	                    help="Directory from which to load plugins. This option "
	                         "may be specified more than once in order to load "
	                         "from multiple places.",
	                    action='append')
	args = parser.parse_args()

	log_level = args.log_level.upper()
	if log_level != "NONE":
		logging.basicConfig(level=getattr(logging, log_level))

	octo.start(plugin_dirs=args.plugin_dir, block=True)
