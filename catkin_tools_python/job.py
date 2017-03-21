# Copyright 2017 Clearpath Robotics Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pkginfo
import sys
import threading

from catkin_tools.jobs.cmake import copy_install_manifest
from catkin_tools.jobs.cmake import generate_env_file
from catkin_tools.jobs.cmake import generate_setup_file
from catkin_tools.jobs.cmake import get_python_install_dir

from catkin_tools.jobs.utils import copyfiles
from catkin_tools.jobs.utils import makedirs
from catkin_tools.utils import which

from catkin_tools.execution.jobs import Job
from catkin_tools.execution.stages import CommandStage
from catkin_tools.execution.stages import FunctionStage

import pip.commands.install
import pip.utils.logging
import pip.utils.ui

import logging


RSYNC_EXEC = which('rsync')

pip_logger = logging.getLogger('pip')
pip_logger.setLevel(logging.DEBUG)
pip_logger.propagate = False

pip.utils.ui.InteractiveSpinner = pip.utils.ui.NonInteractiveSpinner


class PipLogHandler(logging.Handler):
    _thread_loggers = {}

    @classmethod
    def emit(cls, record):
        cls._thread_loggers[threading.current_thread().ident].out(record.getMessage())

pip_logger.addHandler(PipLogHandler())


def renamepath(logger, event_queue, source_path, dest_path):
    """FunctionStage functor which renames a filesystem object."""
    os.rename(source_path, dest_path)
    return 0


def pip_install(logger, event_queue, source_path, build_path, install_path):
    """FunctionStage functor that calls pip."""

    # This has to be set on a per-thread basis.
    pip.utils.logging._log_state.indentation = 0
    PipLogHandler._thread_loggers[threading.current_thread().ident] = logger

    pip.commands.install.InstallCommand().main([
        '--no-cache-dir',
        source_path,
        '--build', build_path,
        '--force-reinstall',
        '--ignore-installed',
        '--no-binary=:all:',
        '--upgrade',
        '--no-deps',
        '--prefix=%s' % install_path])
    return 0


def create_python_build_job(context, package, package_path, dependencies, force_cmake, pre_clean):

    # Package source space path
    pkg_dir = os.path.join(context.source_space_abs, package_path)

    # Package build space path
    build_space = context.package_build_space(package)

    # Package metadata path
    metadata_path = context.package_metadata_path(package)

    # Environment dictionary for the job, which will be built
    # up by the executions in the loadenv stage.
    job_env = dict(os.environ)

    # Get actual staging path
    dest_path = context.package_dest_path(package)
    final_path = context.package_final_path(package)

    # Create job stages
    stages = []

    # Create package metadata dir
    stages.append(FunctionStage(
        'mkdir',
        makedirs,
        path=metadata_path
    ))

    # Copy source manifest
    stages.append(FunctionStage(
        'cache-manifest',
        copyfiles,
        source_paths=[os.path.join(context.source_space_abs, package_path, 'package.xml')],
        dest_path=os.path.join(metadata_path, 'package.xml')
    ))

    # Install package using pip into temporary staging area.
    stages.append(FunctionStage(
        'pip-install',
        pip_install,
        source_path=pkg_dir,
        build_path=build_space,
        install_path=os.path.join(build_space, 'install')
    ))

    # Special path rename required only on Debian.
    python_install_dir = get_python_install_dir()
    if 'dist-packages' in python_install_dir:
        python_install_dir_site = python_install_dir.replace('dist-packages', 'site-packages')
        stages.append(FunctionStage(
            'debian-fix',
            renamepath,
            source_path=os.path.join(build_space, 'install', python_install_dir_site),
            dest_path=os.path.join(build_space, 'install', python_install_dir)
        ))

    # Create package install space.
    stages.append(FunctionStage(
        'mkdir-install',
        makedirs,
        path=dest_path
    ))


    # Copy files from staging area into final install path, using rsync. Despite
    # having to spawn a process, this is much faster than copying one by one
    # with native Python.
    stages.append(CommandStage(
        'install',
        [RSYNC_EXEC, '-a',
            os.path.join(build_space, 'install', ''),
            dest_path],
        cwd=pkg_dir,
        locked_resource='installspace'))

    # Determine the location where the setup.sh file should be created
    stages.append(FunctionStage(
        'setupgen',
        generate_setup_file,
        context=context,
        install_target=dest_path
    ))

    stages.append(FunctionStage(
        'envgen',
        generate_env_file,
        context=context,
        install_target=dest_path
    ))

    return Job(
        jid=package.name,
        deps=dependencies,
        env={},
        stages=stages)


def create_python_clean_job(context, package, package_path, dependencies, dry_run,
                            clean_build, clean_devel, clean_install):
    stages = []

    # Package build space path
    build_space = context.package_build_space(package)

    # Package metadata path
    metadata_path = context.package_metadata_path(package)

    stages = []

    return Job(
        jid=package.name,
        deps=dependencies,
        env={},
        stages=stages)
