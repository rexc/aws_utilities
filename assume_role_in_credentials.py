import boto3
import configparser
import os.path
from pprint import pprint

# Some other SDKs/tools sometimes have poor support for assume roles/profiles
# This looks into your credentials file and will attempt to assume a role using the information inside
# the config file itself

def read_credentials_file():
    credentials_file = os.path.expanduser('~/.aws/credentials')
    exists = os.path.isfile(credentials_file)

    if exists:
        config = configparser.ConfigParser()
        config.read_file(open(credentials_file))
        # for section in config.sections():
        #     print(section)
        #     for k, v in config[section].items():
        #         print('{}:{}'.format(k, v))
        return config
    else:
        # print('No credentials file: {}'.format(credentials_file))
        return None


def assume_role(config, target_role, session_name="TestSession"):
    source = config[target_role]['source_profile']
    client = boto3.client('sts',
                          aws_access_key_id=config[source]['aws_access_key_id'],
                          aws_secret_access_key=config[source]['aws_secret_access_key'],
                          )

    print('Attempting to assume role "{}"'.format(target_role))
    if config.has_option(target_role, 'mfa_serial'):
        mfa = config[target_role]['mfa_serial']
        token = input('Enter code for {}: '.format(mfa))

        response = client.assume_role(
            RoleArn=config[target_role]['role_arn'],
            RoleSessionName=session_name,
            # Policy='string',
            DurationSeconds=3600,
            # ExternalId='string',
            SerialNumber=mfa,
            TokenCode=token
        )
    else:
        response = client.assume_role(
            RoleArn=config[target_role]['role_arn'],
            RoleSessionName=session_name,
            # Policy='string',
            DurationSeconds=3600,
            # ExternalId='string',
        )
    session_key_id = response['Credentials']['AccessKeyId']
    session_secret = response['Credentials']['SecretAccessKey']
    session_token = response['Credentials']['SessionToken']

    # print(response)
    print('export AWS_ACCESS_KEY_ID={}'.format(session_key_id))
    print('export AWS_SECRET_ACCESS_KEY={}'.format(session_secret))
    print('export AWS_SESSION_TOKEN={}'.format(session_token))

if __name__ == '__main__':
    credentials_config = read_credentials_file()
    profile_map = {}
    for i, section in enumerate(credentials_config.sections()):
        profile_map[str(i)] = section
    pprint(profile_map)
    option = input('Choose role to assume: ')
    assume_role(credentials_config, profile_map[option])
