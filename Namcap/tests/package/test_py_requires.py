# -*- coding: utf-8 -*-
#
# namcap tests - py_requires
# Copyright (C) 2019 Chih-Hsuan Yen <yan12125@archlinux.org>
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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
#   USA
#

import os
from Namcap.tests.makepkg import MakepkgTest
import Namcap.rules.py_requires


class PyRequiresTest(MakepkgTest):
	pkgbuild_template = """
pkgname=__namcap_test_py_requires
pkgver=1.0
pkgrel=1
depends=({depends})
makedepends=(python-setuptools)
arch=(any)

package() {{
	cat > setup.py <<EOF
from setuptools import setup
setup(name='foo', version='1.0', **{extra_setup_args})
EOF
	python setup.py install --root="$pkgdir" --optimize=1
}}
"""

	def _build_and_test_py_pkg(self, depends, extra_setup_args):
		pkgfile = "__namcap_test_py_requires-1.0-1-any.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_template.format(
				depends=depends,
				extra_setup_args=repr(extra_setup_args),
			))
		self.run_makepkg()
		pkg, rule = self.run_rule_on_tarball(
			os.path.join(self.tmpdir, pkgfile),
			Namcap.rules.py_requires.PythonRequiresRule
		)
		dep_errors, _, _ = Namcap.depends.analyze_depends(pkg)
		return pkg, rule.errors, dep_errors

	def test_simple(self):
		"Package with normal python dependency"
		pkg, rule_errors, dep_errors = self._build_and_test_py_pkg(
			depends='python-six',
			extra_setup_args={'install_requires': ['six']},
		)
		self.assertEqual(pkg.detected_deps['python-six'], [
			('python-package-needed %s %s', ('python-six', "{'foo'}"))
		])
		self.assertEqual(rule_errors, [])
		self.assertEqual(dep_errors, [])

	def test_multiple_times(self):
		"Package with a python dependency listeed multiple times"
		pkg, rule_errors, dep_errors = self._build_and_test_py_pkg(
			depends='python-six',
			extra_setup_args={
				'install_requires': ['six'],
				'extras_require': {'yolo': ['six']},
			},
		)
		self.assertEqual(pkg.detected_deps['python-six'], [
			('python-package-needed %s %s', ('python-six', "{'foo'}"))
		])
		self.assertEqual(rule_errors, [])
		self.assertEqual(dep_errors, [])

	def test_missing_dependency(self):
		"Package with missing dependency"
		pkg, rule_errors, dep_errors = self._build_and_test_py_pkg(
			depends='',
			extra_setup_args={'install_requires': ['six']},
		)
		self.assertEqual(pkg.detected_deps['python-six'], [
			('python-package-needed %s %s', ('python-six', "{'foo'}"))
		])
		self.assertEqual(rule_errors, [])
		self.assertEqual(dep_errors, [(
			'dependency-detected-not-included %s (%s)',
			('python-six', "package python-six needed in Python distributions {'foo'}"))
		])

	def test_missing_distribution(self):
		"Package with missing Python distribution"
		pkg, rule_errors, dep_errors = self._build_and_test_py_pkg(
			depends='',
			extra_setup_args={'install_requires': ['does_not_exist']},
		)
		self.assertEqual(rule_errors, [
			('python-distribution-not-found %s', 'does_not_exist'),
		])
		self.assertEqual(dep_errors, [])

	def test_version_mismatch(self):
		"Package with version-mismatched dependency"
		pkg, rule_errors, dep_errors = self._build_and_test_py_pkg(
			depends='python-six',
			extra_setup_args={'install_requires': ['six>=999999']},
		)
		self.assertEqual(len(rule_errors), 1)
		tag, (needed_version, found_version) = rule_errors[0]
		self.assertEqual(
			(tag, needed_version),
			('python-distribution-version-mismatch %s %s', 'six>=999999'),
		)
		self.assertEqual(dep_errors, [])

	# TODO: more tests
	# multiple distributions in an ALPM package (e.g., python-jaraco),

# vim: set ts=4 sw=4 noet:
