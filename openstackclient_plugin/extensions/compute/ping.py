from osc_lib.command import command
from openstackclient.i18n import _
from osc_lib import utils
from openstackclient_plugin.pepper.pepper_utils import PepperWrapper


def get_dhcp_agent_host(manager, network_id):
    dhcp_ports = manager.ports(network_id=network_id, device_owner="network:dhcp")
    for port in dhcp_ports:
        return port.binding_host_id


class PingServer(command.Command):
    def get_parser(self, prog_name):
        parser = super(PingServer, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to add the port to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        """
        ping server from dhcp namespace
        :param parsed_args:
        :return:
        """

        compute_client = self.app.client_manager.compute
        network_client = self.app.client_manager.network
        server = utils.find_resource(compute_client.servers, parsed_args.server)
        executor = PepperWrapper()

        for port in network_client.ports(device_id=server.id):
            fixed_ips = port.fixed_ips
            network_id = port.network_id
            host = get_dhcp_agent_host(network_client, network_id)

            for ip in fixed_ips:
                address = ip.get('ip_address', None)
                if address:
                    print(executor.execute('%s*' % host, 'ip ntens exec qdhcp-%s ping -c 3 %s' % (network_id, address)))
