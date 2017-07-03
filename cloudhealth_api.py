from requests import get
from pprint import pprint
import os
from time import time
from json import load, dump
import configparser
from functools import partial

# See https://github.com/CloudHealth/cht_api_guid for more details about Cloudhealth API


WEEK = 604800
DAY = 86400
HOUR = 3600

CACHE_PATH = 'ch_cache'

def read_chapi_key(key_path='~/.cloudhealth'):
    with open(os.path.expanduser(key_path)) as f:
        config = configparser.ConfigParser()
        config.read_file(f)
        return config.get('default', 'api_key')


chapi_key = read_chapi_key()
chapi_api_key_name = 'api_key'

api_payload = {chapi_api_key_name: chapi_key}

CHAPI_BASE = 'https://chapi.cloudhealthtech.com'

apis_map = {
    'available': 'api.json',
    'search': 'api/search.json'
}

api_url = {k: CHAPI_BASE + '/' + v for k, v in apis_map.items()}


def cached(cachefile, cache_ttl_sec):
    """
    Decorator to persist calls to disk
    :param cachefile: name of file with json
    :param cache_ttl_sec: If the file is older than this, ignore cache
    :return: 
    """

    def decorator(func):
        def wrapped(*args, **kwargs):
            if os.path.exists(cachefile):
                cur_time_epoch = time()
                if cur_time_epoch - os.stat(cachefile).st_mtime < cache_ttl_sec:
                    with open(cachefile, 'rb') as cachehandle:
                        print("using cached result from '%s'" % cachefile)
                        return load(cachehandle)

            # execute the function with all arguments passed
            res = func(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'w') as cachehandle:
                print("saving result to cache '%s'" % cachefile)
                dump(res, cachehandle, indent=2)
            return res

        return wrapped

    return decorator


@cached(CACHE_PATH + '/' + 'AvailableObjects.json', WEEK)
def get_available_objects():
    r = get(api_url['available'], params=api_payload)
    return r.json()


def get_object_info(asset_name, cache_ttl_sec=WEEK):
    cachefile = CACHE_PATH + '/' + asset_name + 'Info.json'
    if os.path.exists(cachefile):
        cur_time_epoch = time()
        if cur_time_epoch - os.stat(cachefile).st_mtime < cache_ttl_sec:
            with open(cachefile, 'rb') as cachehandle:
                print("using cached result from '%s'" % cachefile)
                return load(cachehandle)

    url = CHAPI_BASE + '/api/' + asset_name + '.json'
    r = get(url, params=api_payload)
    with open(cachefile, 'w') as cachehandle:
        print("saving result to cache '%s'" % cachefile)
        dump(r.json(), cachehandle, indent=2)
    return r.json()


def search(asset_name, include='', cache_ttl_sec=DAY):
    cachefile = CACHE_PATH + '/' + asset_name + '.json'
    if os.path.exists(cachefile):
        cur_time_epoch = time()
        if cur_time_epoch - os.stat(cachefile).st_mtime < cache_ttl_sec:
            with open(cachefile, 'rb') as cachehandle:
                print("using cached result from '%s'" % cachefile)
                return load(cachehandle)

    payload = {
        'name': asset_name,
        'include': include
    }

    payload.update(api_payload)

    r = get(api_url['search'], payload)

    with open(cachefile, 'w') as cachehandle:
        print("saving result to cache '%s'" % cachefile)
        dump(r.json(), cachehandle, indent=2)
    return r.json()


# Search functions built using partial below, otherwise we can use revert back to querying them raw
search_aws_security_group = partial(search, asset_name='AwsSecurityGroup', include='vpc')
search_aws_security_group_rule = partial(search, asset_name='AwsSecurityGroupRule')
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


def get_all_aws_objects_info():
    all_objects = [x for x in get_available_objects() if x.lower().startswith('aws')]
    for obj in all_objects:
        get_object_info(obj, cache_ttl_sec=WEEK)


def get_all_azure_objects_info():
    all_objects = [x for x in get_available_objects() if x.lower().startswith('azure')]
    for obj in all_objects:
        get_object_info(obj, cache_ttl_sec=WEEK)


def main():
    pass


if __name__ == '__main__':
    main()
