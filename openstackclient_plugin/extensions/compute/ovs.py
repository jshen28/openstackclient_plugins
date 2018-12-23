from osc_lib.command import command
from openstackclient.i18n import _
from osc_lib import utils
from openstackclient_plugin.pepper.pepper_utils import PepperWrapper


def get_dhcp_agent_host(manager, network_id):
    dhcp_ports = manager.ports(network_id=network_id, device_owner="network:dhcp")
    for port in dhcp_ports:
        return port.binding_host_id


class TestOvs(command.Command):
    def get_parser(self, prog_name):
        parser = super(TestOvs, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to add the port to (name or ID)"),
        )
        parser.add_argument(
            "--dest-port",
            required=False,
            help=_("test this port, use dhcp port by default")
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

        # test arp
        arp_test = 'ovs-appctl ofproto/trace br-int arp,in_port=%s,arp_spa=%s,arp_tpa=%s,dl_src=%s,' \
                   'dl_dst=ff:ff:ff:ff:ff:ff'
        ip_test = 'ovs-appctl ofproto/trace br-int in_port=%s,dl_src=%s,dl_dst=%s'

        dest_port = None
        if parsed_args.dest_port:
            dest_port = network_client.get_port(parsed_args.dest_port)

        for port in network_client.ports(device_id=server.id):
            fixed_ips = port.fixed_ips
            host = port.binding_host_id

            if dest_port is None:
                for dp in network_client.ports(network_id=port.network_id, device_owner='network:dhcp'):
                    dest_port = dp
                    break

            for ip in fixed_ips:
                address = ip.get('ip_address', None)
                if address:
                    dest_address = dest_port.fixed_ips[0].get('ip_address')
                    in_port = executor.execute('%s*' % host, 'ovs-vsctl get interface qvo%s ofport' % port.id[0:11])
                    print(executor.execute('%s*' % host, arp_test % (
                        in_port, address, dest_address, port.mac_address)))
                    print(executor.execute('%s*' % host,
                                           ip_test % (in_port, address, dest_address)))
