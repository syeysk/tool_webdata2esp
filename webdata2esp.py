#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mimetypes
import os
import gzip
import sys
import importlib
import argparse

from jinja2 import Environment, FileSystemLoader  #, select_autoescape

import min_html
import min_css
import min_js

TEMP_DIRECTORY = os.path.join(os.path.expandvars('%TEMP%'), 'webdata2esp')
CONSTANTS_INO_BODY_BEFORE_BYTES = 'const char const_{func_name}[{fsize_in}] PROGMEM = {{'
CONSTANTS_INO_BODY_AFTER_BYTES = '};\r\n'
SET_HANDLERS_INO_HEAD = 'void set_handlers(void) {{\r\n'
SET_HANDLERS_INO_BODY = '    webServer.on("/{fname_in}", HTTP_GET, {func_name});\r\n'
SET_HANDLERS_INO_TAIL = '}\r\n'
WEBPAGE_INO_BODY = '''void {func_name}() {{\r
    webServer.sendHeader("Content-Encoding", "gzip");\r
    //File f = SPIFFS.open("/index.html", "r");\r
    webServer.send_P(200, "{fmtype}", const_{func_name}, {fsize_in});\r\n}}\r\n'''
WEBPAGE_INO_TAIL = '\r\n'

mHTML = min_html.MinHTML()
mCSS = min_css.MinCSS()
mJS = min_js.MinJS()


def get_context(lang, path, x=0, context=None):
    context = context if context is not None else {}
    sys.path.clear()
    sys.path.append(path)
    if lang in sys.modules:
        del sys.modules[lang]

    module_lang = importlib.import_module(lang)
    context.update(module_lang.context)
    # print(x, module_lang, sys.path)
    x += 1
    if x == 5:
        exit()

    if 'path' in dir(module_lang):
        for m_path in module_lang.path:
            get_context(lang, m_path, x, context)

    return context


def transform(path_webpage, path_set_handlers, path_constants, fnames, input_path, language):
    if not os.path.exists(TEMP_DIRECTORY):
        os.mkdir(TEMP_DIRECTORY)

    context = get_context(
        language,
        os.path.join(input_path, 'languages'),
    )
    env = Environment(
        loader=FileSystemLoader(input_path)
        #  autoescape=select_autoescape(['html', 'xml'])
    )
    with open(path_webpage, 'w') as f_out, open(path_set_handlers, 'w') as f_out2, open(path_constants, 'w') as f_out3:
        f_out2.write(SET_HANDLERS_INO_HEAD)
        print()
        for fname_in in fnames:
            print('file:', fname_in)
            fpath_in = os.path.join(input_path, fname_in)
            fpath_in_min = os.path.join(TEMP_DIRECTORY, fname_in)
            os.system('mkdir -p "{}" && cp "{fpath_in}" "{fpath_in_min}"'.format(  # TODO: заменить Bash на Python
                os.path.dirname(fpath_in_min),
                fpath_in=fpath_in,
                fpath_in_min=fpath_in_min
            ))
            fsize = os.path.getsize(fpath_in)
            fpath_in = fpath_in_min
            print('    SIZE: {}\n  compilation of template...'.format(fsize))
            template = env.get_template(fname_in)
            with open(fpath_in, 'w', encoding='utf-8') as f:
                f.write(template.render(context))

            fsize = os.path.getsize(fpath_in)
            print('    SIZE: {}\n  minification...'.format(fsize))
            if fname_in.endswith('.html'):
                mHTML.min(fpath_in, fpath_in, fnames)
            elif fname_in.endswith('.css'):
                mCSS.min(fpath_in, fpath_in)
            elif fname_in.endswith('.js'):
                mJS.min(fpath_in, fpath_in_min)

            fsize = os.path.getsize(fpath_in)
            print('    SIZE: {}\n  archiving...'.format(fsize))
            gz_fpath_in = '{}.gz'.format(fpath_in)
            with open(gz_fpath_in, 'wb') as myzip, open(fpath_in, 'rb') as s:
                myzip.write(gzip.compress(s.read()))

            fsize = os.path.getsize(gz_fpath_in)
            print('    SIZE: {}\n  converting into C-code for Arduino...'.format(fsize))
            fmtype = mimetypes.guess_type(fname_in)
            func_name = 'handler_{}'.format(fname_in.replace('.', '_').replace('/', '_'))
            f_out.write(WEBPAGE_INO_BODY.format(
                func_name=func_name,
                fmtype=fmtype[0] if fmtype[0] else 'text/plain',
                fsize_in=fsize,
            ))
            f_out2.write(SET_HANDLERS_INO_BODY.format(fname_in=fname_in, func_name=func_name))
            f_out3.write(CONSTANTS_INO_BODY_BEFORE_BYTES.format(func_name=func_name, fsize_in=fsize))
            with open(gz_fpath_in, 'rb') as f_in:
                for i in range(1, fsize):
                    f_out3.write('{}{}'.format(f_in.read(1)[0], ',' if i < fsize-1 else ''))
                    f_in.seek(i)

            f_out3.write(CONSTANTS_INO_BODY_AFTER_BYTES)

        f_out.write(WEBPAGE_INO_TAIL)
        f_out2.write(SET_HANDLERS_INO_TAIL)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser(description='Script for integration web-files into Arduino-program')
    cli_parser.add_argument('--input', dest='input_path')
    cli_parser.add_argument('--output', dest='output_path')
    cli_parser.add_argument('-l', '--lang', default='EN', help='language for text in web-files', dest='lang')
    cli_parser.add_argument(
        '-f',
        '--file',
        dest='files',
        action='append',
        default=['index.html'],
        help='list of "*.html" files for transformation. '
             'All local links in this files will include in this list automatically.'
    )
    cli_args = cli_parser.parse_args()
    input_path = os.path.expanduser(os.path.normpath(cli_args.input_path))
    output_path = os.path.expanduser(os.path.normpath(cli_args.output_path))

    transform(
        os.path.join(output_path, 'webpage.ino'),
        os.path.join(output_path, 'set_handlers.ino'),
        os.path.join(output_path, 'constants.ino'),
        cli_args.files,
        input_path,
        cli_args.lang.upper()
    )
