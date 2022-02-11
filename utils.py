# -*- coding: utf-8 -*-
import json
from collections import namedtuple

ParsedArgsTuple = namedtuple(
    'ParsedArgs', [
        'method', 'url', 'data', 'data_type', 'headers', 'verify', 'auth'])

INDENT = 4
BASE_INDENT = ' ' * INDENT
APPLICATION_JSON = 'application/json'

def dict2pretty(the_dict):
    if not the_dict:
        return ''
    return ("\n" + BASE_INDENT).join(
        json.dumps(the_dict, sort_keys=True, indent=INDENT, separators=(',', ': ')).splitlines())


def double_quotes(text):
    return text.replace('"', '\\"')