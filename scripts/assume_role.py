import boto3
import configparser
import os.path
import sys

# Some other SDKs/tools sometimes have poor support for assume roles/profiles
# This looks into your credentials file and will attempt to assume a role using the information inside
# the config file itself
CREDENTIALS_LOCATION = '~/.aws/credentials'


def read_credentials_file():
    credentials_file = os.path.expanduser(CREDENTIALS_LOCATION)
    config = configparser.ConfigParser()
    config.read_file(open(credentials_file))
    return config


def assume_role(config, profile_role, session_name="TestSession", duration=3600):
    if not config.has_option(profile_role, 'role_arn') or not config.has_option(profile_role, 'source_profile'):
        print('"{}" does not have a "role_arn" set to assume or a "source_profile" set'.format(profile_role))
        sys.exit(-1)

    source = config[profile_role]['source_profile']
    client = boto3.client('sts',
                          aws_access_key_id=config[source]['aws_access_key_id'],
                          aws_secret_access_key=config[source]['aws_secret_access_key'],
                          )

    print('Attempting to assume role "{}"'.format(profile_role))

    if config.has_option(profile_role, 'mfa_serial'):
        mfa = config[profile_role]['mfa_serial']
        token = input('Enter code for {}: '.format(mfa))

        response = client.assume_role(
            RoleArn=config[profile_role]['role_arn'],
            RoleSessionName=session_name,
            DurationSeconds=duration,
            SerialNumber=mfa,
            TokenCode=token
        )
    else:
        response = client.assume_role(
            RoleArn=config[profile_role]['role_arn'],
            RoleSessionName=session_name,
            DurationSeconds=duration,
        )
    session_key_id = response['Credentials']['AccessKeyId']
    session_secret = response['Credentials']['SecretAccessKey']
    session_token = response['Credentials']['SessionToken']

    # print(response)
    print('export AWS_ACCESS_KEY_ID={}'.format(session_key_id))
    print('export AWS_SECRET_ACCESS_KEY={}'.format(session_secret))
    print('export AWS_SESSION_TOKEN={}'.format(session_token))
    sys.exit(0)


def main():
    try:
        credentials_config = read_credentials_file()
        profile_map = {}

        for i, section in enumerate(credentials_config.sections()):
            profile_map[str(i)] = section
        print("Profiles/Roles from AWS credentials file")
        for k, v in profile_map.items():
            print('{}: {}'.format(k, v))

        option = input('Enter number of role to assume: ')
        assume_role(credentials_config, profile_map[option])

    except (configparser.MissingSectionHeaderError, configparser.NoSectionError, configparser.NoOptionError) as e:
        print('Not a valid crdentials file')
        print(str(e))
        sys.exit(-1)
    except (IsADirectoryError, FileNotFoundError) as e:
        print(str(e))
        sys.exit(-1)


if __name__ == '__main__':
    main()
