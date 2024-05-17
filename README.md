# Webdata2esp

The Webdata2esp ministers to load your web data into ESP8266 module. It's useful if you do web-interface for your device based on ESP.

# Install

```shell
pip install --user git+https://github.com/syeysk/tool_webdata2esp.git
```

or 
```bash
web2esp --input "path to your webdata" --output "path to your arduino project" --lang en
```

This command will minify and archivate your *.css, *.js and *.html files. Also thecommand will generate three *.ino files and move them into your arduino-project:
- `webpage.ino` - contains the functions for responsing to client by browser's request;
- `set_handlers.ino` - contains the functions for setting handlers on urls (url are equal for file name);
- `constants.ino` - contains the arrays with your archived web files.

You can use the template *.sh for fast running:
```bash
./fast_run/example.sh
```

For minifying the js-code you should install Google Closure Compiler:
- About GCC in russian: https://learn.javascript.ru/minification
- About in english: https://developers.google.com/closure/compiler/
- Download: https://dl.google.com/closure-compiler/compiler-latest.zip . After downloading unpack the "closure-compiler-v*.jar" from "compiler-latest.zip" into root directory of this repository and rename the "closure-compiler-v*.jar" into "closure-compiler.jar".