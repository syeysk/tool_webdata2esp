import os


class MinJS:
    def __init__(self):
        pass

    def min(self, file_in, file_out):
        _file_in = os.path.join(os.path.expandvars('%TEMP%'), 'webdata2esp_temp.js')
        with open(_file_in, 'w', encoding='utf-8') as f:
            f.write(file_in)

        compiler = 'closure-compiler.jar'
        _file_out = '{}_'.format(_file_in)
        os.system('java -jar {compiler} --charset UTF-8 --js {file_in} --js_output_file {file_out}'.format(
            compiler=compiler,
            file_in=_file_in,
            file_out=_file_out,
        ))

        with open(_file_out, 'rb') as f:
            file_out.write(f.read())

        # переименовываем, затирая неминимизированную копию. (джава не хочет затирать существующий файл :( )
        #os.system('mv "{}_" "{}"'.format(file_out, file_out))
