import argparse
import gzip
import json
import mimetypes
import os
import io

from jinja2 import Template

import min_html
import min_css
import min_js

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


def transform(io_webpage, io_set_handlers, io_constants, fnames, context, func_logger):
    io_set_handlers.write(SET_HANDLERS_INO_HEAD)
    for fname_in, file_data in fnames:
        func_logger('file: {}'.format(fname_in))
        func_logger('    SIZE: {}'.format(len(file_data)))
        is_str_data = fname_in.endswith('.html') or fname_in.endswith('.css') or fname_in.endswith('.js')
        if is_str_data:
            func_logger('  rendering of template...')
            template = Template(file_data.decode('utf-8'))
            templated_data: str = template.render(context)
            func_logger('    SIZE: {}\n  minification...'.format(len(templated_data.encode('utf-8'))))
            minified_data: io.BytesIO = io.BytesIO()
            if fname_in.endswith('.html'):
                mHTML.min(io.StringIO(templated_data), minified_data)
            elif fname_in.endswith('.css'):
                mCSS.min(templated_data, minified_data)
            elif fname_in.endswith('.js'):
                mJS.min(templated_data, minified_data)

            file_data: bytes = minified_data.getvalue()
            func_logger('    SIZE: {}'.format(len(file_data)))

        func_logger('  archiving...')
        zipped_data = gzip.compress(file_data)
        fsize = len(zipped_data)
        func_logger('    SIZE: {}\n  converting into C-code for Arduino...'.format(fsize))
        fmtype = mimetypes.guess_type(fname_in)
        func_name = 'handler_{}'.format(fname_in.replace('.', '_').replace('/', '_'))
        io_webpage.write(WEBPAGE_INO_BODY.format(
            func_name=func_name,
            fmtype=fmtype[0] if fmtype[0] else 'text/plain',
            fsize_in=fsize,
        ))
        io_set_handlers.write(SET_HANDLERS_INO_BODY.format(fname_in=fname_in, func_name=func_name))
        io_constants.write(CONSTANTS_INO_BODY_BEFORE_BYTES.format(func_name=func_name, fsize_in=fsize))
        for byte, i in enumerate(zipped_data, 1):
            io_constants.write('{}{}'.format(byte, ',' if i < fsize-1 else ''))

        io_constants.write(CONSTANTS_INO_BODY_AFTER_BYTES)

    io_webpage.write(WEBPAGE_INO_TAIL)
    io_set_handlers.write(SET_HANDLERS_INO_TAIL)


if __name__ == '__main__':
    def get_files_from_fs(fnames, input_path):
        for fname_in in fnames:
            fpath_in = os.path.join(input_path, fname_in)
            with open(fpath_in, 'rb') as file:
                yield fname_in, file.read()

    cli_parser = argparse.ArgumentParser(description='Script for integration web-files into Arduino-program')
    cli_parser.add_argument('--input', dest='input_path')
    cli_parser.add_argument('--output', dest='output_path')
    cli_parser.add_argument('-l', '--lang', default='EN', help='language for text in web-files', dest='lang')
    cli_parser.add_argument(
        '-f',
        '--file',
        dest='files',
        action='append',
        default=['index.html', 'index.css', 'functions_wfnli.js', 'after_load.js', 'webif_libs/functions_embedded.js'],
        help='list of "*.html" files for transformation. '
             'All local links in this files will include in this list automatically.'
    )
    cli_args = cli_parser.parse_args()
    input_path = os.path.expanduser(os.path.normpath(cli_args.input_path))
    output_path = os.path.expanduser(os.path.normpath(cli_args.output_path))

    context_path = '{}{}languages{}{}.json'.format(input_path, os.path.sep, os.path.sep, cli_args.lang.upper())
    with open(context_path, 'r') as context_file:
        context = json.load(context_file)

    path_webpage = os.path.join(output_path, 'webpage.ino')
    path_set_handlers = os.path.join(output_path, 'set_handlers.ino')
    path_constants = os.path.join(output_path, 'constants.ino')
    with open(path_webpage, 'w') as io_webpage, open(path_set_handlers, 'w') as io_set_handlers:
        with open(path_constants, 'w') as io_constants:
            print()
            transform(
                io_webpage,
                io_set_handlers,
                io_constants,
                get_files_from_fs(cli_args.files, input_path),
                context,
                print,
            )
