import re
from .utils import APPLICATION_JSON, ParsedArgsTuple

def parse_raw_http(raw):
    lines = raw.split("\n")
    method = 'get'
    url = ''
    headers_dict = {}
    body_lines = None

    for cur_line in lines:
        cur_line = cur_line.strip()
        if not url:
            match = re.search(
                r'^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\s+',
                cur_line,
                re.I)
            if match:
                method = match.group(0)
                url = cur_line[len(method):]
                match = re.search(r'\s+HTTP/.*$', url, re.I)
                url = url[:match.span()[0]] if match else url
                continue

        if body_lines is None:
            if not cur_line:
                body_lines = []
                continue
            separator_index = cur_line.index(":")
            if separator_index == -1:
                key = cur_line
                value = ''
            else:
                key = cur_line[:separator_index].strip().lower()
                value = cur_line[separator_index + 1:].strip()
            headers_dict[key] = value
        else:
            body_lines.append(cur_line)

    host = headers_dict.get('host')
    if host and url[0] == '/':
        host_port = host.split(":")
        scheme = 'http'
        if len(host_port) > 1:
            scheme = 'https' if host_port[1] == '443' else 'http'
        url = '{0}://{1}{2}'.format(scheme, host, url)

    data_type = 'data'
    post_data = ''
    if body_lines:
        post_data = ''.join(body_lines)
        post_data = "'{}'".format(post_data)
        content_type = headers_dict.get('content-type')
        if content_type == APPLICATION_JSON:
            data_type = 'json'

    auth = ''
    verify = ''

    return ParsedArgsTuple(
        method=method,
        url=url,
        data=post_data,
        data_type=data_type,
        headers=headers_dict,
        verify=verify,
        auth=auth
    )
