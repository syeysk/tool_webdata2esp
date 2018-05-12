import re
import mimetypes
import os
import lxml.html as html
#from lxml.html import html5parser as html
import tinycss2
import gzip

fnames = {
    "0": ['index.html'],
    "1": ['index.html']
}
interface_type = "1"

path = 'interface_type'+interface_type
path_min = os.path.join(path, 'min')
if not os.path.exists(path_min): os.mkdir(path_min)
fname_out = 'webpage'+interface_type+'.ino'
fname_out2 = 'set_handlers'+interface_type+'.ino'
fname_out3 = 'constants'+interface_type+'.ino'

preproc_str = "#if INTERFACE_TYPE == "+interface_type+"\r\n"

f_out = open(fname_out, 'w')
f_out.write(preproc_str)
f_out.close();

f_out2 = open(fname_out2, 'w')
f_out2.write(preproc_str+'void set_handlers(void) {\r\n')
f_out2.close();

f_out3 = open(fname_out3, 'w')
f_out3.write(preproc_str+'\r\n')
f_out3.close();

def get_fname_min(fname):
    return '.'.join(fname.split('.')[:-1])+'_min.'+fname.split('.')[-1]

def minificate(el, level=0):
    if len(el.getchildren()) > 0:
        for _el in el.getchildren():
            minificate(_el, level+1)
    else:
        if not isinstance(el.tag, str): el.getparent().remove(el)
        elif el.tag == 'script' and 'src' in el.attrib and el.attrib['src']:
            fnames[interface_type].append(el.attrib['src'])
        elif el.tag == 'link' and 'href' in el.attrib and el.attrib['href']:
            fnames[interface_type].append(el.attrib['href'])

for fname_in in fnames[interface_type]:

    fname_in_min = get_fname_min(fname_in)
    
    fpath_in = os.path.join(path, fname_in)
    fpath_in_min = os.path.join(path_min, fname_in)
 
    os.system('cp '+fpath_in+' '+fpath_in_min)

    fpath_in = fpath_in_min
    
    if fname_in.split('.')[-1] == 'html':
        document = html.parse(fpath_in)
        minificate(document.getroot())
        document.write(fpath_in);
    elif fname_in.split('.')[-1] == 'css': 
        with open(fpath_in, 'r') as f:
           css = tinycss2.parse_stylesheet(f.read(), True, True)
        with open(fpath_in, 'w') as f:
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
    elif fname_in.split('.')[-1] == 'js': 
        compiler = 'closure-compiler-v20180402.jar';
        os.system('java -jar '+compiler+' --js '+fpath_in+' --js_output_file '+fpath_in+'_')
        # перемименовываем, затирая неминимизированную копию. (джава не хочет затирать существующий файл :( )
        os.system('mv '+fpath_in+'_ '+fpath_in)

    with open(fpath_in+'.gz', 'wb') as myzip:
        with open(fpath_in, 'rb') as s:
            myzip.write(gzip.compress(s.read()))
    fpath_in = fpath_in+'.gz'
    
    with open(fpath_in, 'rb') as f_in, open(fname_out, 'a') as f_out, open(fname_out2, 'a') as f_out2, open(fname_out3, 'a') as f_out3:
        fmtype = mimetypes.guess_type(fname_in)
        fmtype = fmtype[0] if fmtype[0] is not None else 'text/plain'
        fsize_in = os.path.getsize(fpath_in)
        func_name = "handler_"+fname_in.replace('.', '_')

        f_out.write("void "+func_name+"() {\r\n");
        f_out.write("    webServer.sendHeader(\"Content-Encoding\", \"gzip\");\r\n");
        #f_out.write("    File f = SPIFFS.open(\"/index.html\", \"r\");\r\n")
        f_out2.write("    webServer.on(\"/"+fname_in+"\", HTTP_GET, "+func_name+");\r\n");
        f_out3.write("const char const_"+func_name+"["+str(fsize_in)+"] PROGMEM = {")

        #for line in f_in:
        #    line = str([i for i in line])[1:-1]
        #    f_out3.write(line.replace(' ', ''))
        for i in range(1, fsize_in):
            f_out3.write(str(f_in.read(1)[0])+',')
            f_in.seek(i)
        f_out.write("    webServer.send_P(200, \""+fmtype+"\", const_"+func_name+", "+str(fsize_in)+");\r\n}\r\n");
        f_out3.write("0};\r\n")


f_out = open(fname_out, 'a')
f_out.write("#endif\r\n")
f_out.close();

f_out2 = open(fname_out2, 'a')
f_out2.write("}\r\n#endif\r\n")
f_out2.close();

f_out3 = open(fname_out3, 'a')
f_out3.write("\r\n#endif\r\n")
f_out3.close();