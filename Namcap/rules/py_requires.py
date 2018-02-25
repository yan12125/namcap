import site
import tempfile
import sys

import importlib_metadata
from packaging.requirements import Requirement
from packaging.markers import default_environment

import Namcap.package
from Namcap.ruleclass import TarballRule

_NO_EXTRA = object()


class PythonRequiresRule(TarballRule):
	name = "pythonrequires"
	description = "Checks dependencies using Python distribution requirements"

	def _analyze_python_distribution(self, distribution, needed_files):
		if not distribution.requires:
			return
		# XXX: get_all() is not a public API; it's part of
		# email.message.Message, which is an implementation detail
		# of importlib_metadata
		extras = distribution.metadata.get_all('Provides-Extra') or []
		for requirement_str in distribution.requires:
			requirement = Requirement(requirement_str)
			# Skipping requirements with incompatible markers
			# (e.g., 'enum34 ; python_version<"3.4"')
			matched_extra = None
			if requirement.marker:
				# Don't attempt to parse markers! There might be complex cases
				# like (python_version >= "2.7" or python_version >= "3.4") and extra == "yolo"'
				# XXX: is it slow?
				for extra in [_NO_EXTRA] + extras:
					marker_env = default_environment()
					marker_env['extra'] = extra
					if requirement.marker.evaluate(marker_env):
						matched_extra = extra
						break
				if matched_extra is None:
					# markers for incompatible environments (e.g., python_version < "3.4")
					continue
			try:
				needed_dist = importlib_metadata.distribution(requirement.name)
				if not requirement.specifier.contains(needed_dist.version):
					self.errors.append((
						"python-package-version-mismatch %s %s",
						('%s%s' % (requirement.name, requirement.specifier), needed_dist.version)
					))
				needed_files.setdefault(str(needed_dist._path), set()).add(
					distribution.metadata['Name'])
			except importlib_metadata.PackageNotFoundError:
				# TODO: is it a good idea? dependencies are environment-dependent
				if requirement.marker and matched_extra != _NO_EXTRA:
					continue
				self.errors.append(("python-package-not-found %s", requirement.name))

	# TODO: use public API instead of importlib_metadata.PathDistribution._path
	def analyze(self, pkginfo, tar):
		with tempfile.TemporaryDirectory() as tmpdir:
			tar.extractall(tmpdir)
			for site_package_path in site.getsitepackages():
				old_sys_path = list(sys.path)
				current_root = tmpdir + site_package_path
				# XXX: hack sys.path before importlib_metadata.distributions()
				# support path argument
				sys.path = [current_root]
				# use list() to run the search now
				distributions = list(importlib_metadata.distributions())
				sys.path = old_sys_path
				needed_files = {}
				for distribution in distributions:
					self._analyze_python_distribution(distribution, needed_files)
			for pkg in Namcap.package.get_installed_packages():
				for j, fsize, fmode in pkg.files:
					full_path = '/' + j
					if full_path.endswith('/'):
						full_path = full_path[:-1]
					if full_path in needed_files:
						reasons = pkginfo.detected_deps.setdefault(pkg.name, [])
						reasons.append((
							"python-package-needed %s %s",
							(pkg.name, str(needed_files[full_path]))
						))

# vim: set ts=4 sw=4 noet:
