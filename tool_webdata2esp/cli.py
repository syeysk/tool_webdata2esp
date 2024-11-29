import argparse
import json
import os

from tool_webdata2esp.core import get_files_from_list_of_filenames, transform


def run():
    cli_parser = argparse.ArgumentParser(description='Script for integration web-files into Arduino-program')
    cli_parser.add_argument('--input', dest='input_path')
    cli_parser.add_argument('--output', dest='output_path')
    cli_parser.add_argument('--templates', dest='templates_path')
    cli_parser.add_argument('-l', '--lang', default='EN', help='language for text in web-files', dest='lang')
    cli_parser.add_argument(
        '-f',
        '--file',
        dest='files',
        action='append',
        default=['index.html'],
        help='list of "*.html" files for transformation. '
             'All local links in these files will include in this list automatically.'
    )
    cli_args = cli_parser.parse_args()
    input_path = os.path.expanduser(os.path.normpath(cli_args.input_path))
    output_path = os.path.expanduser(os.path.normpath(cli_args.output_path))
    context_path = '{}{}languages{}{}.json'.format(input_path, os.path.sep, os.path.sep, cli_args.lang.upper())
    with open(context_path, 'r') as context_file:
        context = json.load(context_file)

    templates = {}
    for root, dirs, filenames in os.walk(cli_args.templates_path):
        for filename in filenames:
            with open(os.path.join(root, filename), 'r') as file:
                templates[filename] = file.read()

    print()
    output_files_data = transform(
        templates,
        get_files_from_list_of_filenames(cli_args.files, input_path),
        context,
        print,
    )
    for output_file_name, output_file_content in output_files_data:
        with open(os.path.join(output_path, output_file_name), 'w', encoding='utf-8') as output_file:
            output_file.write(output_file_content)




if __name__ == '__main__':
    run()
