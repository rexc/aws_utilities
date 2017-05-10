# aws_utilities

Some useful scripts usually python to help in when dealing with AWS

## Install/Uninstall

This should all you call these from the commandline or you can run them directly using python

* Install locally into activated virtualenv

  ```pip install .```

* Uninstall

  ```pip uninstall aws-utilities```

## Scripts

* assume_role - reads your credentials file and spits out temp credentials for that profile that are valid for an hour,
these can be exported to start a new shell

### Example
```
(venv_36) bash$ assume_role
Profiles/Roles from AWS credentials file
0: default
1: rex.chan
2: apps-nonprod
3: apps-prod
4: services-nonprod
5: services-nonprod-ro
6: services-prod
7: services-prod-ro
Enter number of role to assume: 2
Attempting to assume role "apps-nonprod"
Enter code for arn:aws:iam::123456727141:mfa/rex.chan: 123456
export AWS_ACCESS_KEY_ID=<blah>
export AWS_SECRET_ACCESS_KEY=<blah>
export AWS_SESSION_TOKEN=<blah>
```