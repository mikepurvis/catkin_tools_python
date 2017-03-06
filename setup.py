from setuptools import setup

setup(
    name='catkin_tools_python',
    packages=['catkin_tools_python'],
    version='0.0.0',
    author='Mike Purvis',
    author_email='mpurvis@clearpath.ai',
    maintainer='Mike Purvis',
    maintainer_email='mpurvis@clearpath.ai',
    url='http://catkin-tools-python.readthedocs.org/',
    keywords=['catkin'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description="Python buildtype plugin for catkin_tools.",
    long_description="Plugin for catkin_tools to build plain Python packages.",
    license='Apache 2.0',
    entry_points={
        'catkin_tools.jobs': [
            'python = catkin_tools_python:description',
        ]
    },
    install_requires=[
        'catkin_tools'
    ]
)
