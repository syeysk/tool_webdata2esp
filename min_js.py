class MinJS:
    
    def __init__(self):
        pass

    def min(self, file_in, file_out):
        compiler = 'closure-compiler-v20180402.jar';
        os.system('java -jar '+compiler+' --js '+file_in+' --js_output_file '+file_out+'_')
        # переименовываем, затирая неминимизированную копию. (джава не хочет затирать существующий файл :( )
        os.system('mv '+file_out+'_ '+file_out)
