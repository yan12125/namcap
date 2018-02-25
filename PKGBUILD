# Maintainer: Kyle Keen <keenerd@gmail.com>
# Contributor: sudokode <sudokode@gmail.com>
# Contributor: Jason Chu <jason@archlinux.org>
# Contributor: Jesse Young <jesse.young@gmail.com>

pkgname=namcap
pkgver=3.2.8
pkgrel=1
pkgdesc="A Pacman package analyzer (git)"
arch=('any')
url="http://projects.archlinux.org/namcap.git/"
license=('GPL')
depends=('python' 'pyalpm' 'licenses' 'binutils' 'elfutils' 'python-pyelftools'
         'python-importlib-metadata')
makedepends=('git' 'python-setuptools')
source=("$pkgname::git+file:///$(pwd)#branch=wip-python")
sha256sums=('SKIP')

check() {
  cd $pkgname

  env PARSE_PKGBUILD_PATH="$srcdir/${pkgname}" \
      PATH="$srcdir/${pkgname}:$PATH" \
      python3 setup.py test
}

package() {
  cd $pkgname

  python ./setup.py install --root="$pkgdir"

  find "$pkgdir" -type d -name '.git' -exec rm -r '{}' +
}

# vim:set ts=2 sw=2 et:
