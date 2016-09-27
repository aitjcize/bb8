#!/bin/bash
#
# bb8 Python package upgrade script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Copyright 2016 bb8 Authors

upgrade_packages() {
  local requirements=$1
  local tmpdir=$(mktemp -d)

  virtualenv $tmpdir
  source $tmpdir/bin/activate
  pip install $(cat $requirements | cut -f 1 -d '=') --upgrade

  # We want pre-release version of SQLAlchemy
  if grep SQLAlchemy $requirements; then
    pip install --pre --upgrade SQLAlchemy
  fi

  pip freeze | grep -v 'pkg-resources' > $requirements
  deactivate
}

cd $(dirname $0)/..

for target in $(find -name requirements.txt); do
  echo "Upgrading packages for $target ..."
  upgrade_packages $target
done
