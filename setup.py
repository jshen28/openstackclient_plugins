# -*- coding: utf-8 -*-
import random
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='openstackclient_plugin',
    description='test openstackclient plugin',
    version=str(random.randint(10, 1000)),
    install_requires=[
        "openstackclient",
        "salt-pepper==0.5.2"
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