import os
import sys
import re
from termcolor import cprint

profile_regex = re.compile(r'^\[(.*)\]$')


def creds():
    cprint('Paste AWS credentials:', 'yellow', attrs=['bold'])
    profile = sys.stdin.readline()
    access_key = sys.stdin.readline()
    secrete_key = sys.stdin.readline()
    session_token = sys.stdin.readline()

    if not profile_regex.match(profile):
        cprint('\nInvalid Credentials', 'red', attrs=['bold'])
        sys.exit(1)

    home_dir = os.path.expanduser('~')
    aws_dir = f'{home_dir}/.aws'
    credentials_filename = f'{aws_dir}/credentials'

    if not os.path.exists(aws_dir):
        os.makedirs(aws_dir)

    if not os.path.exists(credentials_filename):
        file = open(credentials_filename, 'w')
        file.close()

    credentials_file = open(credentials_filename, 'r+')
    items = credentials_file.readlines()

    replaced = False
    for index, item in enumerate(items):
        if item.startswith(profile):
            items[index+1] = access_key
            items[index+2] = secrete_key
            items[index+3] = session_token
            replaced = True
            break

    if not replaced:
        items.append(profile)
        items.append(access_key)
        items.append(secrete_key)
        items.append(session_token)

    with open(credentials_filename, 'w') as file:
        for line in items:
            file.write(line)
        if items[-1] != '\n':
            file.write('\n')

    cprint('\nCredentials saved', 'green', attrs=['bold'])
