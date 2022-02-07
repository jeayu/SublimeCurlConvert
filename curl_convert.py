# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import json
import argparse
import shlex
from collections import namedtuple

ParsedArgsTuple = namedtuple('ParsedArgs', ['method', 'url', 'data', 'data_type', 'headers', 'verify', 'auth'])

settings = sublime.load_settings("CurlConvert.sublime-settings")

parser = argparse.ArgumentParser(prog="")
parser.add_argument('command')
parser.add_argument('url')
parser.add_argument('-X', '--request', default=None)
parser.add_argument('-d', '--data')
parser.add_argument('-b', '--data-binary', '--data-raw', default=None)
parser.add_argument('--user', '-u', default=())
parser.add_argument('-G', '--get', action='store_true', default=False)
parser.add_argument('-H', '--header', action='append', default=[])
parser.add_argument('-A', '--user-agent', default=None)
parser.add_argument('-k','--insecure', action='store_true')
parser.add_argument('-i','--include', action='store_true')
parser.add_argument('-s','--silent', action='store_true')
parser.add_argument('--compressed', action='store_true')


def parse_args(args=None, namespace=None):
    try:
        parsed_args, argv = parser.parse_known_args(args, namespace)
    except SystemExit:
        return None
    if argv:
        return None

    url = parsed_args.url

    method = 'get'
    if parsed_args.request:
        method = parsed_args.request

    post_data = parsed_args.data or parsed_args.data_binary or ''
    if post_data:
        if not parsed_args.request:
            method = 'post'

    data_type = 'data'
    headers_dict = {}
    for header in parsed_args.header:
        key, value = header.split(':', 1)
        if key.lower().strip() == 'content-type' and value.lower().strip() == 'application/json':
            data_type = 'json'
            post_data = json2pretty(post_data)
        else:
            headers_dict[key] = value.strip()
    if parsed_args.user_agent:
        headers_dict['User-Agent'] = parsed_args.user_agent

    if post_data and data_type == 'data':
        post_data = "'{}'".format(post_data)

    auth = ''
    if parsed_args.user:
        auth = tuple(parsed_args.user.split(':'))

    verify = ''
    if parsed_args.insecure:
        verify = 'False'

    headers = dict2pretty(headers_dict)

    return ParsedArgsTuple(
        method=method,
        url=url,
        data=post_data,
        data_type=data_type,
        headers=headers,
        verify=verify,
        auth=auth
    )

        
def dict2pretty(the_dict, indent=4):
    if not the_dict:
        return ''
    return ("\n" + " " * indent).join(
        json.dumps(the_dict, sort_keys=True, indent=indent, separators=(',', ': ')).splitlines())


def json2pretty(json_data, indent=4):
    if not json_data:
        return ''
    return ("\n" + " " * indent).join(
        json.dumps(json.loads(json_data), sort_keys=True, indent=indent).splitlines())


def double_quotes(text):
    return text.replace('"', '\\"')


class CurlPythonCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                text = self.convert2python(command_text)
                self.view.replace(edit, region, text)

    def convert2python(self, command_text):
        text = shlex.split(command_text)
        parsed_args_tuple = parse_args(text)
        if parsed_args_tuple is None:
            return command_text
            
        base_indent = ' ' * settings.get("base_indent")

        method, url, data, data_type, headers, verify, auth = parsed_args_tuple

        result = """requests.{method}('{url}'{headers}{data}{auth}{verify}\n)""".format(
            method=method.lower(),
            url=url,
            headers=",\n{}headers = {}".format(
                base_indent, headers) if headers else '',
            data=",\n{}{} = {}".format(
                base_indent, data_type, data) if data else '',
            auth=",\n{}auth = {}".format(
                base_indent, auth) if auth else '',
            verify=",\n{}verify = {}".format(
                base_indent, verify) if verify else ''
        )
        return result

