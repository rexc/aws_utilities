from requests import get
from pprint import pprint
import os
from time import time
from json import load, dump
import configparser
from functools import partial
import ipaddress

import requests_cache

# See https://github.com/CloudHealth/cht_api_guide for more details about Cloudhealth API


WEEK = 604800
DAY = 86400
HOUR = 3600

CHAPI_BASE = 'https://chapi.cloudhealthtech.com'
requests_cache.install_cache('cloudhealth api', expire_after=HOUR)

API_MAP = {
    'available': 'api.json',
    'search': 'api/search.json'
}

API_URL = {k: CHAPI_BASE + '/' + v for k, v in API_MAP.items()}


class Credential(object):
    def __init__(self, key_path='~/.cloudhealth'):
        self.api_key = None
        with open(os.path.expanduser(key_path)) as f:
            config = configparser.ConfigParser()
            config.read_file(f)
            self.api_key = {'api_key': config.get('default', 'api_key')}


class NetworkEntity(object):
    def __init__(self, id, name, cidr):
        """

        :param id: uniquely aws id ie `vpc-<id>` or `i-<id>`
        :param name:
        :param cidr:
        """

        self.id = id
        self.name = name
        self.cidr = cidr

    def __repr__(self):
        return ' '.join(['{}:{}'.format(k, v) for k, v in self.__dict__.items() if type(k) == str and type(v) == str])


credential = Credential()


def get_available_objects():
    r = get(API_URL['available'], params=credential.api_key)
    return r.json()


def get_object_info(asset_name):
    url = CHAPI_BASE + '/api/' + asset_name + '.json'
    r = get(url, params=credential.api_key)
    return r.json()


def search(asset_name, include='', cache_ttl_sec=DAY):
    payload = {
        'name': asset_name,
        'include': include
    }

    payload.update(credential.api_key)
    r = get(API_URL['search'], payload)
    return r.json()


# Search functions built using partial below, otherwise we can use revert back to querying them raw
search_aws_security_group = partial(search, asset_name='AwsSecurityGroup', include='vpc')
search_aws_security_group_rule = partial(search, asset_name='AwsSecurityGroupRule', include='security_group')
search_aws_account = partial(search, asset_name='AwsAccount', cache_ttl_sec=WEEK)
search_aws_vpc_subnet = partial(search, asset_name='AwsVpcSubnet')
search_aws_vpc = partial(search, asset_name='AwsVpc', cache_ttl_sec=WEEK)
search_aws_nat_gateway = partial(search, asset_name='AwsNatGateway', cache_ttl_sec=WEEK)
search_aws_region = partial(search, asset_name='AwsRegion', cache_ttl_sec=WEEK)
search_aws_eip = partial(search, asset_name='AwsElasticIp', )
search_aws_cfn_stack = partial(search, asset_name='AwsCloudFormationStack')
search_aws_az = partial(search, asset_name='AwsAvailabilityZone')
search_aws_lb = partial(search, asset_name='AwsLoadBalancer', cache_ttl_sec=HOUR)
search_aws_image = partial(search, asset_name='AwsImage', )
search_aws_instance_status = partial(search, asset_name='AwsInstanceStatus', include='instance', cache_ttl_sec=HOUR)
search_aws_tag = partial(search, asset_name='AwsTag')
search_aws_user = partial(search, asset_name='AwsUser')
search_azure_subscription = partial(search, asset_name='AzureSubscription')


def get_all_objects_info(starts_with=''):
    return [get_object_info(x) for x in get_available_objects() if x.lower().startswith(starts_with)]


get_all_aws_objects_info = partial(get_all_objects_info, starts_with='aws')
get_all_azure_objects_info = partial(get_all_objects_info, starts_with='azure')


def save_to_file(filename, api_func):
    with open(filename, 'w') as f:
        dump(api_func, f, indent=2)


def get_networks_from_aws():
    vpcs = search_aws_vpc()
    subnets = search_aws_vpc_subnet()
    sg_rules = search_aws_security_group_rule()
    entities = []
    seen = set()
    for vpc in vpcs:
        network = vpc['cidr_block']
        if network not in seen:
            seen.add(network)
            entities.append(NetworkEntity(vpc['vpc_id'], vpc['name'], network))

    for subnet in subnets:
        network = subnet['cidr_block']
        if network not in seen:
            entities.append(NetworkEntity(subnet['subnet_id'], subnet['name'], network))
            seen.add(network)

    for rule in sg_rules:
        cidr_ips = [ip.strip(',') for ip in rule['ip_ranges'].split(' ')]
        sg_id = rule['security_group']['group_id']
        name = rule['security_group']['name']

        for cidr in cidr_ips:
            if cidr != 'All' and cidr != 'None':
                if cidr not in seen:
                    entities.append(NetworkEntity(sg_id, name, cidr))
                    seen.add(cidr)

    return entities

def scratch():
    aws_networks = get_networks_from_aws()
    pprint(aws_networks)
    print(len(aws_networks))


def main():
    scratch()


if __name__ == '__main__':
    main()
