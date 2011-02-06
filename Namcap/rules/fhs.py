# 
# namcap rules - fhs
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
# 
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 

import os
import tarfile
from Namcap.ruleclass import *

class FHSRule(TarballRule):
	name = "directoryname"
	description = "Checks for standard directories."
	def prereq(self):
		return "tar"
	def analyze(self, pkginfo, tar):
		valid_paths = [
				'bin/', 'etc/', 'lib/', 'sbin/', 'opt/', 'srv/',
				'usr/bin/', 'usr/include/', 'usr/lib/', 'usr/lib32/',
				'usr/sbin/', 'usr/share/',
				'var/cache/', 'var/lib/', 'var/lock/', 'var/log/', 'var/opt/',
				'var/run/', 'var/spool/', 'var/state/',
				'.PKGINFO', '.INSTALL', '.CHANGELOG',
		]
		ret = [[], [], []]
		for i in tar.getnames():
			# Replace multiple /'s at the end of a string with a single /
			# Not sure if this is a python bug or a makepkg bug
			if i.endswith('/'):
				i = i.rstrip('/') + '/'
			fileok = 0
			for j in valid_paths:
				# matches directory names (j, filename) or parent directories (filename, j)
				if i[0:len(j)] == j or j[0:len(i)] == i:
					fileok = 1
			if not fileok:
				ret[1].append(("file-in-non-standard-dir %s", i))
		return ret

class FHSManpagesRule(TarballRule):
	name = "fhs-manpages"
	description = "Verifies correct installation of man pages"
	def prereq(self):
		return "tar"
	def analyze(self, pkginfo, tar):
		gooddir = 'usr/share/man'
		bad_dir = 'usr/man'
		ret = [[], [], []]
		for i in tar.getmembers():
			if not i.isfile():
				continue
			if i.name.startswith(bad_dir):
				ret[0].append(("non-fhs-man-page %s", i.name))
			elif not i.name.startswith(gooddir):
				#Check everything else to see if it has a 'man' path component
				for part in i.name.split(os.sep):
					if part == "man":
						ret[1].append(("potential-non-fhs-man-page %s", i.name))

		return ret

class FHSInfoPagesRule(TarballRule):
	name = "fhs-infopages"
	description = "Verifies correct installation of info pages"
	def prereq(self):
		return "tar"
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		for i in tar.getmembers():
			if not i.isfile():
				continue
			if i.name.startswith('usr/info'):
				ret[0].append(("non-fhs-info-page %s", i.name))
			elif not i.name.startswith('usr/share/info'):
				for part in i.name.split(os.sep):
					if part == "info":
						ret[1].append(("potential-non-fhs-info-page %s", i.name))

		return ret

# vim: set ts=4 sw=4 noet: