import gzip
import mimetypes
import os
import io
import zipfile

from jinja2 import Template

from tool_webdata2esp import min_css, min_html, min_js

SOURCE_NAME = (
    '/* This code was generated with\n'
    '** https://github.com/syeysk/tool_webdata2esp\n'
    '** try online: https://py2c.ru/web2esp/\n'
    '*/\n\n'
)
CONSTANTS_INO_BODY_BEFORE_BYTES = 'const char const_{func_name}[{fsize_in}] PROGMEM = {{'
CONSTANTS_INO_BODY_AFTER_BYTES = '};\r\n'
SET_HANDLERS_INO_HEAD = 'void set_handlers(void) {\r\n'
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
    io_webpage.write(SOURCE_NAME)
    io_set_handlers.write(SOURCE_NAME)
    io_constants.write(SOURCE_NAME)

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
        for i, byte in enumerate(zipped_data, 1):
            io_constants.write('{}{}'.format(byte, ',' if i < fsize-1 else ''))

        io_constants.write(CONSTANTS_INO_BODY_AFTER_BYTES)

    io_webpage.write(WEBPAGE_INO_TAIL)
    io_set_handlers.write(SET_HANDLERS_INO_TAIL)


def get_files_from_archive(archive):
    with zipfile.ZipFile(archive) as archive_object:
        for member_name in archive_object.namelist():
            member_info = archive_object.getinfo(member_name)
            if not member_info.is_dir():
                with archive_object.open(member_info) as member_file:
                    yield member_name, member_file.read()


def get_files_from_list_of_filenames(fnames, base_path):
    for fname_in in fnames:
        fpath_in = os.path.join(base_path, fname_in)
        with open(fpath_in, 'rb') as file:
            yield fname_in, file.read()


