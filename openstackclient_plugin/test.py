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


class GetServerNetwork(command.ShowOne):

    def get_parser(self, prog_name):
        parser = super(GetServerNetwork, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to add the port to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(compute_client.servers, parsed_args.server)
        network_client = self.app.client_manager.network
        print(server.name)
        for port in network_client.ports(device_id=server.id):
            logging.debug(dir(port))

        colume_names = ('name', 'port')
        return colume_names, (server.name, port.fixed_ips)
