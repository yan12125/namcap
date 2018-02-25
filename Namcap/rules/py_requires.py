import site
import tempfile

import importlib.metadata
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

		for requirement_str in distribution.requires:
			# parse it
			requirement = Requirement(requirement_str)

			# Skipping requirements with incompatible markers
			# (e.g., 'enum34 ; python_version<"3.4"')
			if requirement.marker:
				marker_env = default_environment()
				marker_env['extra'] = _NO_EXTRA
				if not requirement.marker.evaluate(marker_env):
					continue

			try:
				needed_dist = importlib.metadata.distribution(requirement.name)
				if not requirement.specifier.contains(needed_dist.version):
					self.errors.append((
						"python-distribution-version-mismatch %s %s",
						(str(requirement), needed_dist.version)
					))
				# TODO: propose an API instead using PathDistribution._path
				needed_files.setdefault(str(needed_dist._path), set()).add(
					distribution.metadata['Name'])
			except importlib.metadata.PackageNotFoundError:
				self.errors.append(("python-distribution-not-found %s", requirement.name))

	def analyze(self, pkginfo, tar):
		with tempfile.TemporaryDirectory() as tmpdir:
			tar.extractall(tmpdir)

			for site_package_path in site.getsitepackages():
				current_root = tmpdir + site_package_path
				needed_files = {}
				for distribution in importlib.metadata.distributions(path=[current_root]):
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
