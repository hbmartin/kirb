import sys, os, time, copy, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    def on_modified(self, event):
        if not event.is_directory and event.event_type == "modified":
            self.callback(event.src_path)

class Watcher(object):
    def _on_file_changed(self, src_path):
        src_path = os.path.relpath(src_path)
        for out, props in self.file_set.iteritems():
            files = props['files']
            callbacks = props['callbacks']
            if src_path in files:
                if callbacks['onchange']:
                    if not callbacks['onchange'](os.path.abspath(src_path)):
                        raise Exception('onchange callback errored for file ' + src_path)
                print os.path.abspath(out)
                self._compile(files, callbacks, os.path.abspath(out))
                
    def _compile(self, files, callbacks, out):
        if hasattr(callbacks, 'mode') and callbacks['mode'] is 'slurp':
            slurpy = [out, []]
            for filename in files:
                with open(filename) as infile:
                    slurpy[1].append([filename, infile.read()])
            if hasattr(callbacks, 'each') and callable(callbacks['each']):
                callbacks['each'](slurpy)
            else:
                raise Exception('slurp mode requires an each handler')
        else:
            # default mode is concat, also contains break for files_only mode
            if hasattr(callbacks, 'each') and callable(callbacks['each']):
                rv = callbacks['each']([out, files])
                if isinstance(rv, list):
                    files = rv
            if hasattr(callbacks, 'mode') and callbacks['mode'] is 'files_only':
                logging.info("files_only mode, no concat or post")
                return
            with open(out, 'w') as outfile:
                for filename in files:
                    with open(filename) as infile:
                        for line in infile:
                            outfile.write(line if not hasattr(callbacks, 'line') else callbacks['line'](line))
            logging.info("Wrote file: " + out)
            if hasattr(callbacks, 'post') and callable(callbacks['post']):
                callbacks['post'](out)
    
    def compile(self):
        for out, props in self.file_set.iteritems():
            files = props['files']
            callbacks = props['callbacks']
            self._compile(files, callbacks, os.path.abspath(out))
    
    def add_file_set(self, out, files, callbacks = {}):
        if type(files) is not list:
            raise TypeError('files list is a required  argument')
        if type(out) is not str:
            raise TypeError('out is a required argument')
        if out in self.file_set:
            raise Exception('out file is already in use by another FileSet')
        if out in files:
            raise Exception('cannot watch out file')
        self.file_set[out] = {'files' : files, 'callbacks' : callbacks}
        return out
    
    def add_mirror_set(self, orig, new, addl = None):
        if not orig in self.file_set:
            raise Exception('first parameter must refer to output used by add_file_set')
        files = copy.deepcopy(self.file_set[orig]['files'])
        skin_path = os.path.join(self.root, new)
        out = os.path.join(skin_path, orig)
        for i, filename in enumerate(files):
            filePath = os.path.join(skin_path, filename)
            if (os.path.exists(filePath)):
                files[i] = os.path.join(new, files[i])
        if addl is not None and type(addl) is list:
            files.extend(addl)
        self.file_set[out] = {'files' : files, 'callbacks' : self.file_set[orig]['callbacks']}
    
    
    def stop(self):
        self.observer.stop()
        
    def start(self):
        event_handler = ChangeHandler(self._on_file_changed)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.root, recursive=True)
        self.observer.start()
    
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.file_set = {}

