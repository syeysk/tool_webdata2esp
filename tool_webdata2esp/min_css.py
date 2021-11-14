import re

import tinycss2


class MinCSS:
    def min(self, file_in, file_out):
        # with open(file_in, 'r', encoding='utf-8') as f:
        css = tinycss2.parse_stylesheet(file_in, True, True)

        # with open(file_out, 'w', encoding='utf-8') as f:
        for rule in css:
            rule = rule.serialize()
            if not rule or rule.startswith('/*'):
                continue

            rule = re.sub(r'\s+', ' ', rule)
            rule = re.sub(r'\s*}\s*', '}', rule)
            rule = re.sub(r'\s*{\s*', '{', rule)
            rule = re.sub(r'\s*;\s*', ';', rule)
            rule = re.sub(r'\s*,\s*', ',', rule)
            rule = re.sub(r'\s*,\s*', ',', rule)
            rule = re.sub(r'\s*:\s*', ':', rule)
            file_out.write(rule.encode('utf-8'))
