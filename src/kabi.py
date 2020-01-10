# kabi.py - A simple yum plugin to aid enforcement of kernel ABI whitelists
#
# Author: Jon Masters <jcm@redhat.com>
#
# This plugin reads kernel ABI data files containing lists of known 'kABI'
# symbols that are approved for use by third party packages. These files are
# typically stored in /lib/modules/kabi and follow a yum-like config format.
# Since these files can be updated asynchronously, it is possible that the
# local version may be out of date, generating a false positive warning.
#
# /etc/yum/pluginconf.d/kabi.conf:
# 	[main]
# 	enabled=1
# 	whitelists=/lib/modules/kabi
#
# Enforcing mode (in which yum will generate an error and exit on any
# attempt to install a package using non-kABI kernel symbols) can be
# enabled by appending:
#	enforce=1
#
# The kernel kABI files typically follow this format:
#
# /lib/modules/kabi/kabi_whitelist_<arch>:
#	[rhel6_<arch>_whitelist]
#		kernel_symbol
#		kernel_symbol
#		kernel_symbol
#		etc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os, re, string
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)

enabled=True

whitelists_path=None
enforce=False

def load_whitelist(arch):
	"""Load a reference whitelist file."""

	whitelist = []

	whitelist_filename = whitelists_path+"/"+"kabi_whitelist_"+arch

	if not (os.path.isfile(whitelist_filename)):
		return None
	
	whitelist_file = open(whitelist_filename,"r")

	while True:
		in_line = whitelist_file.readline()
		if in_line == "":
			break
		if in_line == "\n":
			continue
		string.split(in_line)
		if in_line[0] == "[":
			continue
		symbol = in_line[1:-1]

		whitelist.append(symbol)

	return whitelist

def init_hook(conduit):
	conduit.info(2, 'Loading support for Red Hat kernel ABI')

def config_hook(conduit):
	global enabled, whitelists_path, enforce

	whitelists_path = conduit.confString('main','whitelists')
	if not whitelists_path:
		conduit.info(2, 'kABI checking will be disabled')
		enabled=False
		return

	enforce_tmp = conduit.confString('main','enforce')
	if enforce_tmp:
		enforce=enforce_tmp

def postresolve_hook(conduit):

	global enabled

	kmods_good = []
	kmods_good_ksyms = []
	kmods_bad = []
	kmods_bad_ksyms = []

	if not enabled:
		return

	ksym_regex = re.compile('^kernel\(([^\)]+)\)$')

	try:
		ts = conduit.getTsInfo()
		for tsmem in ts.getMembers():
			kmods = ts.getNewProvides("kernel-modules")

			for kmod in kmods:
				kmod_name = kmod.name
				kmod_arch = kmod.arch
				kmod_ksyms = []
				kmod_good_ksyms = []
				kmod_bad_ksyms = []
				kmod_is_bad = False

				for req in kmod.requires:
					m = ksym_regex.match(req[0])
					if m:
						kmod_ksyms.append(m.group(1))

				whitelist = load_whitelist(kmod_arch)
				if not whitelist:

					conduit.info(2, 'kABI data files are missing or corrupted - kABI checking disabled')
					enabled=False
					return

				for ksym in kmod_ksyms:
					if ksym in whitelist:
						if ksym not in kmod_good_ksyms:
							kmod_good_ksyms.append(ksym)
					else:
						kmod_is_bad = True
						if ksym not in kmod_bad_ksyms:
							kmod_bad_ksyms.append(ksym)

				for ksym in kmod_good_ksyms:
					if ksym not in kmods_good_ksyms:
						kmods_good_ksyms.append(ksym)
				for ksym in kmod_bad_ksyms:
					if ksym not in kmods_bad_ksyms:
						kmods_bad_ksyms.append(ksym)

				if not kmod_is_bad:
					if not kmod_name in kmods_good:
						kmods_good.append(kmod_name)
				else:
					if not kmod_name in kmods_bad:
						kmods_bad.append(kmod_name)

		for kmod in kmods_bad:
			conduit.info(2, 'WARNING: possible kABI issue with package: ' + kmod)

			if enforce:
				conduit.info(2, 'Aborting - kABI enforcing mode is set')
				raise PluginYumExit('Goodbye')

	except AttributeError:
		return

#DEBUG
#def pretrans_hook(conduit):
#	raise PluginYumExit('Debug Catch')
