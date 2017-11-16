from ipaddress import ip_network
import click


def generate_desired_subnets(base_network, desired_prefix):
    return list(ip_network(base_network).subnets(new_prefix=desired_prefix))


@click.command()
@click.argument('base_network', nargs=1)
@click.argument('desired_prefix', nargs=1)
def print_subnets(base_network, desired_prefix):
    """
    Example:  subnets 10.0.0.0/23 25

    \b
    Number of /25 subnets: 4, each subnet size: 128
    10.0.0.0/25
    10.0.0.128/25
    10.0.1.0/25
    10.0.1.128/25

    """
    list_networks = generate_desired_subnets(base_network, int(desired_prefix))
    print('Number of /{} subnets: {}, each subnet size: {}'.format(desired_prefix, str(len(list_networks)),
                                                                   list_networks[0].num_addresses))
    for network in list_networks:
        print('{} '.format(str(network)))


if __name__ == '__main__':
    print_subnets()
