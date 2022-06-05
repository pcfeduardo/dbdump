#!/usr/bin/env python

''''
REQUIREMENTS:
- linux/freebsd/openbsd/netbsd/macOS
- mysqldump
- python3
- pyyaml

HOW TO USE:
1 - Run this commands to use this script:
# python -m venv .venv
# source .venv/bin/activate

2 - Install python dependencies
# pip install pyyaml

3 - Configure config.yaml
4 - Run ./dbdump.py

NOTES:
If at some point you are going to restore the database and need to remove DEFINER from your exports, please use the following command:

sed 's/\sDEFINER=`[^`]*`@`[^`]*`//g' -i db_file.sql
'''
__program__ = 'dbdump'
__author__ = 'pcfeduardo'
__version__ = 'v1.0.0'

import yaml
import subprocess
import sys
import datetime

config_file = open('config.yaml', 'r')
configs = yaml.full_load(config_file)
databases = configs['databases']
prefix = datetime.datetime.now().strftime("%Y/%Y_%m/%Y_%m_%d/")

def prepare_excluded_tables(db_name, excluded_tables):
    for table in excluded_tables:
        dump_data_cmd.append(f"--ignore-table={db_name}.{table}")
    return True

def dump_db_schema(db_name, dump_schema_cmd):
    print(f'[*] Dumping schemas from database {db_name} ...')
    dump_schema = subprocess.run(dump_schema_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if dump_schema.returncode != 0:
        print('[*] An error occurred while dumping the database schema!\n')
        print(dump_schema.stderr.decode("utf-8"))
        sys.exit(dump_schema.returncode)
    else:
        return dump_schema.stdout.decode('utf-8')

def compress_backup(dumped_file):
    dir = dumped_file.rsplit('/', 1)[0]
    file_sql = dumped_file.rsplit('/', 1)[-1]
    file_zip = file_sql.rsplit('.', 1)[0].__add__('.zip')
    print(f'[*] Compressing {dumped_file}')
    compress = subprocess.run(['zip', f'{dir}/{file_zip}', f'{dir}/{file_sql}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if compress.returncode != 0:
        print('[*] An error occurred while compressing file!\n')
        print(compress.stderr.decode("utf-8"))
        sys.exit(compress.returncode)
    return True

def dump_db_data(db_name, dump_data_cmd):
    print(f'[*] Dumping data from database {db_name} ...')
    dump_data = subprocess.run(dump_data_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if dump_data.returncode != 0:
        print('[*] An error occurred while dumping the database data!\n')
        print(dump_data.stderr.decode("utf-8"))
        sys.exit(dump_data.returncode)
    else:
        return dump_data.stdout.decode('utf-8')

def create_dump_dir(dump_dir, prefix, db_name):
    backup_dir = "%s/%s/%s"
    mkdir = subprocess.run(['mkdir', '-p', backup_dir %(dump_dir, prefix, db_name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if mkdir.returncode != 0:
        print('[*] There was an error creating the following folder: ' + backup_dir %(dump_dir, prefix, db_name))
        print(mkdir.stderr.decode('utf-8'))
        sys.exit(1)
    return True

def write_dump(dump_dir, prefix, db_name, dump_schema, dump_data):
    create_dump_dir(dump_dir, prefix, db_name)
    dump_file = '%s/%s/%s/%s.sql'
    file = dump_file %(dump_dir, prefix, db_name, db_name)
    file = file.replace('//', '/')
    print('[*] Dumping to '+ file)
    with open(file, 'w') as dumped_file:
        dumped_file.write(dump_schema)
        dumped_file.write(dump_data)
    return file

print(f'[*] Starting {__program__} {__version__}')
for config in databases:
    for cfg in config:
        db_config = config[cfg]
        db_host = db_config.get('db_host')
        db_name = db_config.get('db_name')
        db_username = db_config.get('db_username')
        db_password = db_config.get('db_password')
        dump_dir = db_config.get('dump_dir')
        excluded_tables = db_config.get('excluded_tables')
        print(f'\n[*] Connecting to {db_username}@{db_host} ...')
        print(f'[*] Preparing to dump the database {db_name} ...')
        
        dump_schema_cmd = ['mysqldump', '--column-statistics=0', '--force', '--host='+db_host, '--user='+db_username, '--password='+db_password, db_name, '--triggers', '--routines', '--no-data', '--single-transaction']
        dump_data_cmd = ['mysqldump', '--column-statistics=0', '--force', '--host='+db_host, '--user='+db_username, '--password='+db_password, db_name, '--no-create-info', '--skip-triggers', '--single-transaction']

        if excluded_tables != None:
            prepare_excluded_tables(db_name, excluded_tables)
        dump_schema = dump_db_schema(db_name, dump_schema_cmd)
        dump_data = dump_db_data(db_name, dump_data_cmd)
        dumped_file = write_dump(dump_dir, prefix, db_name, dump_schema, dump_data)
        compress_backup(dumped_file)