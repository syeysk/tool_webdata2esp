import argparse
import gzip
import importlib.util
import mimetypes
import os
import shutil

from jinja2 import Environment, FileSystemLoader  # , select_autoescape

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


def get_context(lang, path, level=0, context=None):
    if level == 5:
        return context

    context = context if context is not None else {}
    _path = '{}{}{}.py'.format(path, os.path.sep, lang)
    spec = importlib.util.spec_from_file_location(lang, _path)
    module_lang = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_lang)
    context.update(module_lang.context)
    for new_path in getattr(module_lang, 'path', []):
        get_context(lang, new_path, level + 1, context)

    return context


def transform(webpage, set_handlers, constants, fnames, input_path, language):
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
    io_set_handlers.write(SET_HANDLERS_INO_HEAD)
    print()
    for fname_in in fnames:
        print('file:', fname_in)
        fpath_in = os.path.join(input_path, fname_in)
        fpath_in_min = os.path.join(TEMP_DIRECTORY, fname_in)
        if not os.path.exists(os.path.dirname(fpath_in_min)):
            os.makedirs(os.path.dirname(fpath_in_min))

        shutil.copy(fpath_in, fpath_in_min)
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
        io_webpage.write(WEBPAGE_INO_BODY.format(
            func_name=func_name,
            fmtype=fmtype[0] if fmtype[0] else 'text/plain',
            fsize_in=fsize,
        ))
        io_set_handlers.write(SET_HANDLERS_INO_BODY.format(fname_in=fname_in, func_name=func_name))
        io_constants.write(CONSTANTS_INO_BODY_BEFORE_BYTES.format(func_name=func_name, fsize_in=fsize))
        with open(gz_fpath_in, 'rb') as f_in:
            for i in range(1, fsize):
                io_constants.write('{}{}'.format(f_in.read(1)[0], ',' if i < fsize-1 else ''))
                f_in.seek(i)

        io_constants.write(CONSTANTS_INO_BODY_AFTER_BYTES)

    io_webpage.write(WEBPAGE_INO_TAIL)
    io_set_handlers.write(SET_HANDLERS_INO_TAIL)


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

    path_webpage = os.path.join(output_path, 'webpage.ino')
    path_set_handlers = os.path.join(output_path, 'set_handlers.ino')
    path_constants = os.path.join(output_path, 'constants.ino')
    with open(path_webpage, 'w') as io_webpage, open(path_set_handlers, 'w') as io_set_handlers:
        with open(path_constants, 'w') as io_constants:
            transform(
                io_webpage,
                io_set_handlers,
                io_constants,
                cli_args.files,
                input_path,
                cli_args.lang.upper()
            )
