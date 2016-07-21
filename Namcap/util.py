#
# namcap rules - utility functions
# Copyright (C) 2009 Dan McGee <dan@archlinux.org>
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
import re
import stat

def _read_carefully(path, readcall):
	if not os.path.isfile(path):
		return False
	reset_perms = False
	if not os.access(path, os.R_OK):
		# don't mess with links we can't read
		if os.path.islink(path):
			return None
		reset_perms = True
		# attempt to make it readable if possible
		statinfo = os.stat(path)
		newmode = statinfo.st_mode | stat.S_IRUSR
		try:
			os.chmod(path, newmode)
		except IOError:
			return None
	fd = open(path, 'rb')
	val = readcall(fd)
	fd.close()
	# reset permissions if necessary
	if reset_perms:
		# set file back to original permissions
		os.chmod(path, statinfo.st_mode)
	return val

def _file_has_magic(fileobj, magic_bytes):
	length = len(magic_bytes)
	magic = fileobj.read(length)
	fileobj.seek(0)
	return magic == magic_bytes

def is_elf(fileobj):
	"Take file object, peek at the magic bytes to check if ELF file."
	return _file_has_magic(fileobj, b"\x7fELF")

def is_static(fileobj):
	"Take file object, peek at the magic bytes to check if static lib."
	return _file_has_magic(fileobj, b"!<arch>\n")

def is_script(fileobj):
	"Take file object, peek at the magic bytes to check if script."
	return _file_has_magic(fileobj, b"#!")

def script_type(path):
	firstline = _read_carefully(path, lambda fd: fd.readline())
	try:
		firstline = firstline.decode('utf-8', 'strict')
	except UnicodeDecodeError:
		return None
	if not firstline:
		return None
	script = re.compile('#!.*/(.*)')
	m = script.match(firstline)
	if m is None:
		return None
	cmd = m.group(1).split()
	name = cmd[0]
	if name == 'env':
		name = cmd[1]
	return name

clean_filename = lambda s: re.search(r"/tmp/namcap\.[0-9]*/(.*)", s).group(1)

# vim: set ts=4 sw=4 noet:
