# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='openstackclient_plugin',
    version='0.1',
    description='test openstackclient plugin',
    install_requires=[
        "pecan",
        "sqlalchemy"
    ],
    entry_points={
        "openstack.identity.v3": [
            "get_server_networking=openstackclient_plugin.test:GetServerNetwork"
        ]
    },
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup'])
)