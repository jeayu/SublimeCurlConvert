from .utils import BASE_INDENT, dict2pretty, double_quotes


def convert2python(parsed_args_tuple):
    method, url, data, data_type, headers, verify, auth = parsed_args_tuple
    headers = dict2pretty(headers)

    result = """\
requests.{method}(
    url='{url}'{headers}{data}{auth}{verify}
)""".format(
        method=method.lower(),
        url=url,
        headers=",\n{}headers={}".format(
            BASE_INDENT, headers) if headers else '',
        data=",\n{}data={}".format(
            BASE_INDENT, data) if data else '',
        auth=",\n{}auth={}".format(
            BASE_INDENT, auth) if auth else '',
        verify=",\n{}verify={}".format(
            BASE_INDENT, verify) if verify else ''
    )
    return result


def convert2java(parsed_args_tuple):
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

    result = """\
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
