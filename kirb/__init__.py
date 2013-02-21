from logging import info
from copy import deepcopy
from os import path

try :
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler


    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, callback):
            self.callback = callback
        def on_modified(self, event):
            if not event.is_directory and event.event_type == "modified":
                self.callback(event.src_path)
except:
    info('watchdog not available, cannot perform live build')
    pass

class Watcher(object):
    def _on_file_changed(self, src_path):
        src_path = path.relpath(src_path, self.root)
        # prevent onchange handler from being repeatedly fired by mirrors
        used_onchanges = []
        for out, props in self.file_set.iteritems():
            files = props['files']
            callbacks = props['callbacks']
            if src_path in files:
                if 'onchange' in callbacks and not callbacks['onchange'].__name__ in used_onchanges:
                    if not callbacks['onchange'](path.abspath(src_path)):
                        raise Exception('onchange callback errored for file ' + src_path)
                    used_onchanges.append(callbacks['onchange'].__name__)
                self._compile(files, callbacks, path.abspath(out))
                
    def _compile(self, files, callbacks, out):
        if 'mode' in callbacks and callbacks['mode'] is 'slurp':
            slurpy = []
            for filename in files:
                try:
                    filename = path.abspath(path.join(self.root, filename))
                    with open(filename) as infile:
                        slurpy.append([filename, infile.read()])
                except IOError:
                    info('IOError on ' + filename + ', maybe the file doesnt exist')
                    pass
            if 'each' in callbacks:
                callbacks['each'](out, slurpy)
            else:
                raise Exception('slurp mode requires an each handler')
        else:
            # default mode is concat, also contains break for files_only mode
            if 'each' in callbacks:
                rv = callbacks['each']([out, files])
                if isinstance(rv, list):
                    files = rv
            if 'mode' in callbacks and callbacks['mode'] is 'files_only':
                info("files_only mode, no concat or post")
                return
            with open(out, 'w') as outfile:
                for filename in files:
                    filename = path.abspath(path.join(self.root, filename))
                    try:
                        with open(filename) as infile:
                            for line in infile:
                                outfile.write(line if not 'line' in callbacks else callbacks['line'](line))
                    except IOError:
                        info('IOError on ' + filename + ', maybe the file doesnt exist')
                        pass
            info("Wrote file: " + out)
            if 'post' in callbacks:
                callbacks['post'](out)
    
    def compile(self):
        for out, props in self.file_set.iteritems():
            files = props['files']
            callbacks = props['callbacks']
            if not 'no_out' in callbacks or not callbacks['no_out']:
                self._compile(files, callbacks, path.abspath(out))
    
    def add_file_set(self, out, files, callbacks = {}):
        if out in self.file_set:
            raise Exception('out file is already in use by another FileSet')
        if out in files:
            raise Exception('cannot watch out file')
        self.file_set[out] = {'files' : files, 'callbacks' : callbacks}
        return out
    
    def add_mirror_set(self, orig, new, addl = None):
        if type(orig) is not str:
            raise TypeError('orig list is a required  argument')
        if type(new) is not str:
            raise TypeError('new is a required argument')
        # is deepcopy necessary for inline substitution later?
        files = deepcopy(self.file_set[orig]['files'])
        skin_path = path.join(self.root, new)
        out = path.join(skin_path, orig)
        for i, filename in enumerate(files):
            filePath = path.join(skin_path, filename)
            if (path.exists(filePath)):
                # is lineline substution while looping acceptable?
                files[i] = path.relpath(filePath, self.root)
        if addl is not None:
            files.extend(addl)
        callbacks = deepcopy(self.file_set[orig]['callbacks'])
        callbacks['no_out'] = False
        self.file_set[out] = {'files' : files, 'callbacks' : callbacks}
    
    try:
        def stop(self):
            self.observer.stop()
    
        def start(self):
            event_handler = ChangeHandler(self._on_file_changed)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.root, recursive=True)
            self.observer.start()
    except:
        pass
    
    def __init__(self, root):
        self.root = path.abspath(root)
        self.file_set = {}

