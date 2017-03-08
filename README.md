catkin_tools_python
===================

This is a buildtype plugin for [catkin_tools][1] which allows building plain Python packages
as part of the isolated catkin workspace. Because catkin_tools is not able to see a package
or resolve dependencies without a `package.xml` file in the package directory, there is also
included a script which can be used before the build to spider the workspace, and create
the missing `package.xml` files for Python packages, based on the `PKG-INFO` file which is
standard with the Python sdist archive format.

This package is experimental and incomplete.

[1]: https://catkin-tools.readthedocs.io
