import argparse
import getpass
import io
import logging
import os

from novaclient import api_versions
from novaclient.v2 import servers
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import timeutils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common as network_common


class GetServerNetwork(command.Command):

    def take_action(self, parsed_args):
        print("Hello World")
