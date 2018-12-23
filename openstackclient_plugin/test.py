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
from openstackclient_plugin.pepper.pepper_utils import PepperExecutor
from oslo_utils import timeutils
import six

from openstackclient.i18n import _


def get_router(client_manager, router):
    return client_manager.get_router(router)


class PepperWrapper(object):
    def __init__(self):
        pass

    def execute(self, dest, *cmd):
        cmd_list = [dest, 'cmd.run'] + list(cmd)
        executor = PepperExecutor()
        res_list = executor.execute_return_exit_code(cmd_list)
        return "\n".join(res_list)


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
        host = "%s, %s" % (
            getattr(server, 'OS-EXT-SRV-ATTR:host', None),
            getattr(server, 'OS-EXT-SRV-ATTR:instance_name', None)
        )

        pepper_executor = PepperWrapper()
        logging.info(pepper_executor.execute('cmp001*', 'ovs-vsctl show'))

        # assume that server got single nic
        # and network got a single subnet
        ports, networks, dhcp_ports, dhcp_agents, routers = list(), list(), list(), list(), list()
        for port in network_client.ports(device_id=server.id):
            network = network_client.get_network(port.network_id)
            agents = network_client.network_hosting_dhcp_agents(network)
            dhcp_agents.append(','.join([i.host for i in agents]))

            # fixme generalize to multiple subnets situation
            dhcp_ports.extend([(i.binding_host_id, i.id, i.mac_address) for i in network_client.ports(**{
                "device_owner": "network:dhcp",
                "network_id": network.id
            })])

            # assume dvr mode
            router_ports = network_client.ports(**{
                "device_owner": "network:router_centralized_snat",
                "network_id": network.id
            })
            routers.extend([
                (get_router(network_client, i.device_id).id, getattr(i, 'binding_host_id')) for i in router_ports
            ])

            ports.append(port)
            logging.debug(dir(port))
            networks.append(network)

        colume_names = ('name', 'host', 'ip', 'nework', 'dhcp-ports', 'port', 'routers')
        return colume_names, (
            server.name,
            host,
            '\n'.join([','.join([j.get('ip_address') for j in i.fixed_ips]) for i in ports]),
            '\n'.join([i.id for i in networks]),
            '\n'.join([str(i) for i in dhcp_ports]),
            '\n'.join([i.id for i in ports]),
            '\n'.join([str(i) for i in routers])
        )
