# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
from .utils import ParsedArgsTuple
from .code_generate import convert2python, convert2java
from .curl_parser import parse_curl_command
from .raw_http_parser import parse_raw_http

class CurlPythonCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                parsed_args_tuple = parse_curl_command(command_text)
                if parsed_args_tuple is not None:
                    text = convert2python(parsed_args_tuple)
                self.view.replace(edit, region, text)


class CurlJavaCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                parsed_args_tuple = parse_curl_command(command_text)
                if parsed_args_tuple is not None:
                    text = convert2java(parsed_args_tuple)
                self.view.replace(edit, region, text)


class RawHttpPythonCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                parsed_args_tuple = parse_raw_http(command_text)
                if parsed_args_tuple is not None:
                    text = convert2python(parsed_args_tuple)
                self.view.replace(edit, region, text)


class RawHttpJavaCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                command_text = text.replace("\\\n", " ")
                parsed_args_tuple = parse_raw_http(command_text)
                if parsed_args_tuple is not None:
                    text = convert2java(parsed_args_tuple)
                self.view.replace(edit, region, text)