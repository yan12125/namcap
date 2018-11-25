#
# namcap rules - makedepends
# Copyright (C) 2018 Michael Straube <michael.straube at posteo.de>
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

from Namcap.ruleclass import *

class RedundantMakedepends(PkgbuildRule):
	"""
	This rule checks for make dependencies that are already
	included as dependencies.
	"""
	name = "redundant_makedepends"
	description = "Check for redundant make dependencies"

	def analyze(self, pkginfo, pkgbuild):
		redundant_makedeps = []

		if 'makedepends' not in pkginfo:
			return
		if 'depends' not in pkginfo:
			return
		redundant_makedeps.extend(set(pkginfo["makedepends"]) & set(pkginfo["depends"]))

		for i in redundant_makedeps:
			self.warnings.append(("redundant-makedep %s", i))
