#!/usr/bin/env python

from sys import argv
from os import path
from time import sleep
import kirb

def js_lint(file):
    from subprocess import call
    jshint = path.abspath("./buildtools/node_modules/jshint/bin/hint")
    call([jshint, "--config", "buildtools/jshint.json", file])
    return True

args = argv[1:]
css_paths = ['css/ui-core.css','css/ui.css']
js_paths = ['js/raphael.js','js/jquery/validate.js','js/myApp.js']
js_mobile_paths = ['skins/mobile/js/test.js']

watcher = kirb.Watcher('.')

watcher.add_file_set('styles.css', css_paths)
watcher.add_mirror_set('styles.css', 'skins/mobile')

watcher.add_file_set('app.js', js_paths, {'onchange': js_lint})
watcher.add_mirror_set('app.js', 'skins/mobile', js_mobile_paths)

watcher.compile()
print "Static compile finished"


if not '-c' in args:
    watcher.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
    
