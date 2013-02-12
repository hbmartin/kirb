#!/usr/bin/env python

import sys, time, os
import kirb

def js_lint(file):
    from subprocess import call
    jshint = os.path.abspath("./buildtools/node_modules/jshint/bin/hint")
    call([jshint, "--config", "buildtools/jshint.json", file])
    return True

args = sys.argv[1:]
css_paths = ['css/ui-core.css','css/ui.css']
js_paths = ['js/raphael.js','js/jquery/validate.js','js/myApp.js']
js_mobile_paths = ['skins/mobile/js/test.js']

watcher = kirb.Watcher('.')

watcher.FileSet('styles.css', css_paths)
watcher.MirrorSet('styles.css', 'skins/mobile')

watcher.FileSet('app.js', js_paths, {'onchange': js_lint})
watcher.MirrorSet('app.js', 'skins/mobile', js_mobile_paths)

watcher.compile()
print "Static compile finished"


if not '-c' in args:
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
    
