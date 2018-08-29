import re
import mimetypes
import os
import gzip

import min_html
import min_css
import min_js

mHTML = min_html.MinHTML()
mCSS = min_css.MinCSS()
mJS = min_js.MinJS()

# User config ------------------------------------

the_project_path = os.path.expanduser(os.path.join('~', 'Arduino', 'WFNLI'))
the_if_path = os.path.expanduser(os.path.join('~', 'Репозитории', 'syeysk', 'wfnli_fgmt_webif_'))
fnames = {
    "0": ['index.html'],
    "1": ['index.html'],
    "main": ['index.html']
}
interface_type = "main"

# ------------------------------------

path_min = os.path.join(os.getcwd(), 'temp')
if not os.path.exists(path_min): os.mkdir(path_min)
fname_out = os.path.join(the_project_path, 'webpage'+interface_type+'.ino')
fname_out2 = os.path.join(the_project_path, 'set_handlers'+interface_type+'.ino')
fname_out3 = os.path.join(the_project_path, 'constants'+interface_type+'.ino')

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

print()

for fname_in in fnames[interface_type]:
    
    print('file:', fname_in)

    fpath_in = os.path.join(the_if_path+interface_type, fname_in)
    fpath_in_min = os.path.join(path_min, fname_in)
 
    os.system('mkdir -p "'+os.path.dirname(fpath_in_min)+'" && cp "'+fpath_in+'" "'+fpath_in_min+'"')
    fpath_in = fpath_in_min

    # minificate the file
    print('  minificating...')
    
    if fname_in.split('.')[-1] == 'html':
        mHTML.min(fpath_in, fpath_in_min, fnames[interface_type])
    elif fname_in.split('.')[-1] == 'css': 
        mCSS.min(fpath_in, fpath_in_min)
    elif fname_in.split('.')[-1] == 'js': 
        mJS.min(fpath_in, fpath_in_min)

    # archivate (compress) the file
    print('  archivating...')

    with open(fpath_in+'.gz', 'wb') as myzip:
        with open(fpath_in, 'rb') as s:
            myzip.write(gzip.compress(s.read()))
    fpath_in = fpath_in+'.gz'

    # convert into C-code for Arduino
    print('  converting...')
    
    with open(fpath_in, 'rb') as f_in, open(fname_out, 'a') as f_out, open(fname_out2, 'a') as f_out2, open(fname_out3, 'a') as f_out3:
        fmtype = mimetypes.guess_type(fname_in)
        fmtype = fmtype[0] if fmtype[0] is not None else 'text/plain'
        fsize_in = os.path.getsize(fpath_in)
        func_name = "handler_"+fname_in.replace('.', '_').replace('/', '_')

        f_out.write("void "+func_name+"() {\r\n");
        f_out.write("    webServer.sendHeader(\"Content-Encoding\", \"gzip\");\r\n");
        #f_out.write("    File f = SPIFFS.open(\"/index.html\", \"r\");\r\n")
        f_out2.write("    webServer.on(\"/"+fname_in+"\", HTTP_GET, "+func_name+");\r\n");
        f_out3.write("const char const_"+func_name+"["+str(fsize_in)+"] PROGMEM = {")

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