import argparse
import shlex
import re
from .utils import APPLICATION_JSON, ParsedArgsTuple

__parser = argparse.ArgumentParser(prog="")
__parser.add_argument('command')
__parser.add_argument('url')
__parser.add_argument('-X', '--request', default=None)
__parser.add_argument('-d', '--data')
__parser.add_argument('-b', '--data-binary', '--data-raw', default=None)
__parser.add_argument('--user', '-u', default=())
__parser.add_argument('-G', '--get', action='store_true', default=False)
__parser.add_argument('-H', '--header', action='append', default=[])
__parser.add_argument('-A', '--user-agent', default=None)
__parser.add_argument('-k', '--insecure', action='store_true')
__parser.add_argument('-i', '--include', action='store_true')
__parser.add_argument('-s', '--silent', action='store_true')
__parser.add_argument('--compressed', action='store_true')


def parse_curl_command(command_text):
    if re.search(r'^\s*curl', command_text, re.I):
        text = shlex.split(command_text)
        return parse_args(text)


def parse_args(args):
    try:
        parsed_args, argv = __parser.parse_known_args(
            args=args, namespace=None)
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
        headers_dict[key] = value.strip()
        if key.lower().strip() == 'content-type' and value.lower().strip() == APPLICATION_JSON:
            data_type = 'json'
            
    if parsed_args.user_agent:
        headers_dict['User-Agent'] = parsed_args.user_agent

    if post_data:
        post_data = "'{}'".format(post_data)

    auth = ''
    if parsed_args.user:
        auth = tuple(parsed_args.user.split(':'))

    verify = ''
    if parsed_args.insecure:
        verify = 'False'

    return ParsedArgsTuple(
        method=method,
        url=url,
        data=post_data,
        data_type=data_type,
        headers=headers_dict,
        verify=verify,
        auth=auth
    )
