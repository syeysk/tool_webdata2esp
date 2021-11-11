import argparse
import json
import os

from core import get_files_from_list_of_filenames, transform

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
                get_files_from_list_of_filenames(cli_args.files, input_path),
                context,
                print,
            )
