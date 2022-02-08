# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import json
import argparse
import shlex
from collections import namedtuple

ParsedArgsTuple = namedtuple('ParsedArgs', ['method', 'url', 'data', 'data_type', 'headers', 'verify', 'auth'])

INDENT=4
BASE_INDENT = ' ' * INDENT

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


def parse_args(args, convert_json=False):
    try:
        parsed_args, argv = parser.parse_known_args(args=args, namespace=None)
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
            if convert_json:
                post_data = json2pretty(post_data)
            else:
                headers_dict[key] = value.strip()
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

    return ParsedArgsTuple(
        method=method,
        url=url,
        data=post_data,
        data_type=data_type,
        headers=headers_dict,
        verify=verify,
        auth=auth
    )

def parse_curl_command(command_text, convert_json=False):
    text = shlex.split(command_text)
    return parse_args(text, convert_json)

        
def dict2pretty(the_dict):
    if not the_dict:
        return ''
    return ("\n" + " " * INDENT).join(
        json.dumps(the_dict, sort_keys=True, indent=INDENT, separators=(',', ': ')).splitlines())


def json2pretty(json_data):
    if not json_data:
        return ''
    return ("\n" + " " * INDENT).join(
        json.dumps(json.loads(json_data), sort_keys=True, indent=INDENT).splitlines())


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
        parsed_args_tuple = parse_curl_command(command_text, True)
        if parsed_args_tuple is None:
            return command_text

        method, url, data, data_type, headers, verify, auth = parsed_args_tuple
        headers = dict2pretty(headers)

        result = """\
requests.{method}(
    url='{url}'{headers}{data}{auth}{verify}
)
""".format(
            method=method.lower(),
            url=url,
            headers=",\n{}headers={}".format(
                BASE_INDENT, headers) if headers else '',
            data=",\n{}{}={}".format(
                BASE_INDENT, data_type, data) if data else '',
            auth=",\n{}auth={}".format(
                BASE_INDENT, auth) if auth else '',
            verify=",\n{}verify={}".format(
                BASE_INDENT, verify) if verify else ''
        )
        return result

class CurlJavaCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                text = self.convert2java(command_text)
                self.view.replace(edit, region, text)

    def convert2java(self, command_text):
        parsed_args_tuple = parse_curl_command(command_text)
        if parsed_args_tuple is None:
            return command_text

        method, url, data, data_type, headers, verify, auth = parsed_args_tuple

        headers_code = "\n".join(['{base_indent}{base_indent}httpConn.setRequestProperty("{key}", "{value}");'.format(
            base_indent=BASE_INDENT, key=x[0], value=x[1]) for x in headers.items()])

        data_code = ''
        if data:
            data_code = """
        httpConn.setDoOutput(true);
        OutputStreamWriter writer = new OutputStreamWriter(httpConn.getOutputStream());
        writer.write("{data}");
        writer.flush();
        writer.close();
        httpConn.getOutputStream().close();
        """.format(data=double_quotes(data))

        auth_code = ''
        if auth:
            auth_code = """
        byte[] message = ("{auth_user}:{auth_pwd}").getBytes("UTF-8");
        String basicAuth = DatatypeConverter.printBase64Binary(message);
        httpConn.setRequestProperty("Authorization", "Basic " + basicAuth);
        """.format(auth_user=auth[0], auth_pwd=auth[1])

        result = """
    public static void main(String[] args) throws IOException {{
        URL url = new URL("{url}");
        HttpURLConnection httpConn = (HttpURLConnection) url.openConnection();
        httpConn.setRequestMethod("{method}");
{headers_code}{auth_code}{data_code}
        InputStream responseStream = httpConn.getResponseCode() / 100 == 2
                ? httpConn.getInputStream()
                : httpConn.getErrorStream();
        Scanner s = new Scanner(responseStream).useDelimiter("\\\\A");
        String response = s.hasNext() ? s.next() : "";
        System.out.println(response);
    }}

""".format(
            method=method.upper(),
            url=url,
            headers_code=headers_code,
            auth_code=auth_code,
            data_code=data_code
        )

        return result

