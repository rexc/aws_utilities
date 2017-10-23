# aws_utilities

Some useful scripts usually python to help when working with AWS

## Install/Uninstall

This should all you call these from the commandline or you can run them directly using python

* Install locally into activated virtualenv

  ```pip install .```

* Uninstall

  ```pip uninstall aws-utilities```

## Scripts

* assume_role - reads your credentials file and spits out temp credentials for that profile that are valid for an hour,
these can be exported to start a new shell, useful for ad-hoc work or when sdk/toolkits don't correctly assume roles.
* subnets base and prefix - in networks.py, calculate how many subnets and what CIDRs are
### Example

Sample credentials file
```
[default]
aws_access_key_id = <blah>
aws_secret_access_key = <blah>

[rex.chan]
aws_access_key_id = <blah>
aws_secret_access_key = <blah>

[apps-nonprod]
role_arn = arn:aws:iam::12346789:role/SuperDuper
mfa_serial = arn:aws:iam::123456727141:mfa/rex.chan
source_profile = rex.chan

```

Command line:
```
(venv_36) bash$ assume_role
Profiles/Roles from AWS credentials file
0: default
1: rex.chan
2: apps-nonprod
Enter number of role to assume: 2
Attempting to assume role "apps-nonprod"
Enter code for arn:aws:iam::123456727141:mfa/rex.chan: 123456
export AWS_ACCESS_KEY_ID=<blah>
export AWS_SECRET_ACCESS_KEY=<blah>
export AWS_SESSION_TOKEN=<blah>
```