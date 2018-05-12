import re
import tinycss2

class MinCSS:
    
    def __init__(self):
        pass

    def min(self, file_in, file_out):
        with open(file_in, 'r') as f:
           css = tinycss2.parse_stylesheet(f.read(), True, True)
        with open(file_out, 'w') as f:
            for rule in css:
                rule = rule.serialize()
                rule = re.sub(r'\s+', ' ', rule)
                rule = re.sub(r'\s*}\s*', '}', rule)
                rule = re.sub(r'\s*{\s*', '{', rule)
                rule = re.sub(r'\s*;\s*', ';', rule)
                rule = re.sub(r'\s*,\s*', ',', rule)
                rule = re.sub(r'\s*,\s*', ',', rule)
                rule = re.sub(r'\s*:\s*', ':', rule)
                f.write(rule)