# vCloud Air CLI 0.1
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
import json
from tabulate import tabulate


class VcaCliUtils:

    def _print(self, message, cmd_proc=None, fg='black'):
        click.secho(message, fg=fg)

    def print_warning(self, message, cmd_proc=None):
        self._print(message, cmd_proc, fg='yellow')

    def print_message(self, message, cmd_proc=None):
        self._print(message, cmd_proc, fg='blue')

    def print_error(self, message, cmd_proc=None):
        msg = message
        if cmd_proc is not None and \
                cmd_proc.vca is not None and \
                cmd_proc.vca.response is not None and \
                cmd_proc.vca.response.content is not None:
            if 'message' in cmd_proc.vca.response.content:
                json_message = json.loads(cmd_proc.vca.response.content)
                msg += ': ' + json_message.get('message')
            else:
                msg += ': ' + cmd_proc.vca.response.content
        self._print(msg, cmd_proc, fg='red')

    def print_table(self, message, obj, headers, table, cmd_proc=None):
        # if (ctx is not None and ctx.obj is not
        #         None and ctx.obj['json_output']):
        #     data = [dict(zip(headers, row)) for row in table]
        #     print(json.dumps(
        #         {"Errorcode": "0", "Details": msg, obj: data},
        #         sort_keys=True, indent=4, separators=(',', ': ')))
        # else:
        click.echo(click.style(message, fg='blue'))
        print(tabulate(table, headers=headers, tablefmt="orgtbl"))
