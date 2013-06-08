#!/usr/bin/env python

# Copyright (c) 2013, Nick Groenen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import argparse
import octo

if __name__ == "__main__":
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
