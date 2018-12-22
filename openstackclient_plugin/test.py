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
        network_client = self.app.client_manager.network
        server = utils.find_resource(compute_client.servers, parsed_args.server)
        host = getattr(server, 'OS-EXT-SRV-ATTR:host', None)

        # assume that server got single nic
        ports, networks, dhcp_agents, routers = list(), list(), list(), list()
        for port in network_client.ports(device_id=server.id):
            network = network_client.get_network(port.network_id)
            agents = network_client.network_hosting_dhcp_agents(network)
            dhcp_agents.extend([i.host for i in agents])
            ports.append(port)
            logging.debug(dir(port))
            networks.append(network)

        colume_names = ('name', 'host', 'ip', 'nework', 'dhcp-agents', 'port')
        return colume_names, (
            server.name, host, '\n'.join([','.join([j.get('ip_address') for j in i.fixed_ips]) for i in ports]),
            '\n'.join([i.id for i in networks]), '\n'.join([i for i in dhcp_agents]),
            '\n'.join([i.id for i in ports]))
