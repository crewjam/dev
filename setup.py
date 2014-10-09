# Copyright (c) 2014 Ross Kinder. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import os
import shutil
from os.path import basename, join as pathjoin

from setuptools import setup, Extension

setup(
  name="dev",
  description="...",
  version="0.9",
  license="...",
  url="https://github.com/crewjam/dev",
  author="Ross Kinder",
  author_email="ross+czNyZXBv@kndr.org",
  package_dir={'': 'src'},
  packages=['dev', 'dev.cloudformation', 'dev.units'],
)
