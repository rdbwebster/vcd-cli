# vCloud CLI 0.1
#
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the
# Apache License, Version 2.0 (the "License").
# You may not use this product except in compliance with the License.
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file.
#

import click
from vcd_cli.vcd import cli
from vcd_cli.vcd import API_CURRENT_VERSIONS
from vcd_cli.vcd import CONTEXT_SETTINGS
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import _WellKnownEndpoint
from pyvcloud.vcd.extension import Extension
from vcd_cli.utils import stderr
from vcd_cli.utils import stdout
from vcd_cli.profiles import Profiles
from vcd_cli.utils import as_metavar
from vcd_cli.utils import restore_session
import requests
import traceback


@cli.command(short_help='login to vCD')
@click.pass_context
@click.argument('host',
                metavar='host')
@click.argument('org',
                metavar='organization')
@click.argument('user',
                metavar='user')
@click.option('-p',
              '--password',
              prompt=True,
              metavar='<password>',
              confirmation_prompt=False,
              envvar='VCD_PASSWORD',
              hide_input=True,
              help='Password')
@click.option('-V',
              '--version',
              'api_version',
              default=API_CURRENT_VERSIONS[-1],
              metavar=as_metavar(API_CURRENT_VERSIONS),
              type=click.Choice(API_CURRENT_VERSIONS),
              help='API version')
@click.option('-s/-i',
              '--verify-ssl-certs/--no-verify-ssl-certs',
              required=False,
              default=True,
              help='Verify SSL certificates')
@click.option('-w',
              '--disable-warnings',
              is_flag=True,
              required=False,
              default=False,
              help='Do not display warnings when not verifying SSL ' + \
                   'certificates')
def login(ctx, user, host, password, api_version, org,
          verify_ssl_certs, disable_warnings):
    """Login to vCloud Director

    """
    if not verify_ssl_certs:
        if disable_warnings:
            pass
        else:
            click.secho('InsecureRequestWarning: '
                        'Unverified HTTPS request is being made. '
                        'Adding certificate verification is strongly '
                        'advised.', fg='yellow', err=True)
        requests.packages.urllib3.disable_warnings()
    client = Client(host,
                    api_version=api_version,
                    verify_ssl_certs=verify_ssl_certs,
                    log_file='vcd.log',
                    log_headers=True,
                    log_bodies=True
                   )
    try:
        client.set_credentials(BasicLoginCredentials(user, org, password))
        wkep = {}
        for endpoint in _WellKnownEndpoint:
            if endpoint in client._session_endpoints:
                wkep[endpoint.name] = client._session_endpoints[endpoint]
        profiles = Profiles.load()
        profiles.update(host, org, user,
            client._session.headers['x-vcloud-authorization'],
            api_version,
            wkep,
            verify_ssl_certs,
            disable_warnings,
            debug=True)
        stdout('%s logged in' % (user), ctx)
    except Exception as e:
        if not ctx.find_root().params['json_output']:
            click.secho('can\'t log in', fg='red', err=True)
        stderr(e, ctx)


@cli.command(short_help='logout from vCD')
@click.pass_context
def logout(ctx):
    """Logout from vCloud Director
    """
    profiles = Profiles.load()
    profiles.set('token', '')
    stdout('%s logged out' % (profiles.get('user')), ctx)
