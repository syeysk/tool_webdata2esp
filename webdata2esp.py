import mimetypes
import os
import gzip
import sys
import importlib
import argparse

from jinja2 import Environment, FileSystemLoader#, select_autoescape

import min_html
import min_css
import min_js

def get_context(context, lang, path, x=0):
    sys.path.clear()
    sys.path.append(path)
    if lang in sys.modules: del sys.modules[lang]
    module_lang = importlib.import_module(lang)
    context.update(module_lang.context)
    #print(x, module_lang, sys.path)
    x += 1
    if x == 5: exit()
    if 'path' in dir(module_lang):
        for m_path in module_lang.path: get_context(context, lang, m_path, x)


mHTML = min_html.MinHTML()
mCSS = min_css.MinCSS()
mJS = min_js.MinJS()

# ---------------------------------------------------------------------
# ---------------- User config

device_type = "wfnli"
lang = "RU"
fnames = ['index.html']


devices = {
    "wfr": {
        "input_path": os.path.expanduser(os.path.join('~', 'Репозитории', 'syeysk', 'wfr_fgmt_webif_main')),
        "output_path": os.path.expanduser(os.path.join('~', 'Arduino', 'WFR'))
    },
    "wfnli": {
        "input_path": os.path.expanduser(os.path.join('~', 'Репозитории', 'syeysk', 'wfnli_fgmt_webif_main')),
        "output_path": os.path.expanduser(os.path.join('~', 'Arduino', 'WFNLI'))
    }
}

input_path = devices[device_type]["input_path"]
output_path = devices[device_type]["output_path"]

temp_path = os.path.join(os.getcwd(), 'temp')

fname_out = os.path.join(output_path, 'webpage.ino')
fname_out2 = os.path.join(output_path, 'set_handlers.ino')
fname_out3 = os.path.join(output_path, 'constants.ino')

if not os.path.exists(temp_path): os.mkdir(temp_path)

context = {}
get_context(context, lang, os.path.join(input_path, 'languages'))

env = Environment(
    loader=FileSystemLoader(input_path)
    #autoescape=select_autoescape(['html', 'xml'])
)

# ---------------------------------------------------------------------

with open(fname_out, 'w') as f_out, open(fname_out2, 'w') as f_out2, open(fname_out3, 'w') as f_out3:

    f_out2.write('void set_handlers(void) {\r\n')

    print()

    for fname_in in fnames:
    
        print('file:', fname_in)


        fpath_in = os.path.join(input_path, fname_in)
        fpath_in_min = os.path.join(temp_path, fname_in)
 
        os.system('mkdir -p "'+os.path.dirname(fpath_in_min)+'" && cp "'+fpath_in+'" "'+fpath_in_min+'"')
        fpath_in = fpath_in_min

        # compilation of template
        print('  compilation of template...')

        template = env.get_template(fname_in)
        with open(fpath_in, 'w') as f: f.write(template.render(context))

        # minificate the file
        print('  minificating...')
    
        if fname_in.split('.')[-1] == 'html':
            mHTML.min(fpath_in, fpath_in_min, fnames)
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
    
        with open(fpath_in, 'rb') as f_in:
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

    f_out.write("\r\n")
    f_out2.write("}\r\n")
    f_out3.write("\r\n")
