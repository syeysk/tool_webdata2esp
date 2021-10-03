import os


class MinJS:
    def __init__(self):
        pass

    def min(self, file_in, file_out):
        compiler = 'closure-compiler.jar'
        os.system('java -jar {compiler} --charset UTF-8 --js {file_in} --js_output_file {file_out}_'.format(
            compiler=compiler,
            file_in=file_in,
            file_out=file_out,
        ))
        # переименовываем, затирая неминимизированную копию. (джава не хочет затирать существующий файл :( )
        os.system('mv {}_ {}'.format(file_out, file_out))
