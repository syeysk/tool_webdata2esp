import gzip
import mimetypes
import os
import io
import zipfile

from jinja2 import Template

from tool_webdata2esp import min_css, min_html, min_js


mHTML = min_html.MinHTML()
mCSS = min_css.MinCSS()
mJS = min_js.MinJS()


def transform(templates, fnames, context, func_logger):
    output_files_data = []
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
        output_files_data.append({
            'name': fname_in,
            'funcname': fname_in.replace('.', '_').replace('/', '_'),
            'size': fsize,
            'mimetype': fmtype[0] or 'text/plain',
            'array': ','.join(str(b) for b in zipped_data),
        })
    

    output_context = {'files': output_files_data}
    for template_name, template_content in templates:
        template = Template(template_content.decode('utf-8'))
        yield template_name, template.render(output_context)


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


