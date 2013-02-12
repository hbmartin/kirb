import sys, os, time, copy, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        if callable(callback):
            self.callback = callback
        else:
            raise TypeError('callback is required')
    def on_modified(self, event):
        if event.is_directory or event.event_type is not "modified":
            return
        self.callback(event.src_path)

class Watcher(object):
    file_set = {}
    def _trim_root(self, path, root = None):
        if root is None:
            root = self.root
        if path.startswith(root):
            path = path[len(root):]
        if path.startswith('/'):
            path = path[1:]
        return path
    def _on_file_changed(self, src_path):
        src_path = self._trim_root(src_path)
        for out, props in self.file_set.iteritems():
            files = props['files']
            callbacks = props['callbacks']
            if src_path in files:
                if callable(callbacks['onchange']):
                    if not callbacks['onchange'](os.path.abspath(src_path)):
                        raise Exception('onchange callback errored for file ' + src_path)
                print os.path.abspath(out)
                self._compile(files, callbacks, os.path.abspath(out))
                
    def _compile(self, files, callbacks, out):
        if hasattr(callbacks, 'mode') and callbacks['mode'] is 'slurp':
            slurpy = [out, []]
            for fname in files:
                with open(fname) as infile:
                    slurpy[1].append([fname, infile.read()])
            if hasattr(callbacks, 'each') and callable(callbacks['each']):
                callbacks['each'](slurpy)
            else:
                raise Exception('slurp mode requires an each handler')
        else:
            # default mode is concat, also contains break for files_only mode
            if hasattr(callbacks, 'each') and callable(callbacks['each']):
                rv = callbacks['each']([out, files])
                if type(rv) is list:
                    files = rv
                elif rv is False:
                    logging.info('each callback asked us to exit quietly')
                    return
                elif rv is True:
                    logging.info('finished each callback, proceeding with original file list')
                else:
                    raise TypeError('the each callback must return an array of file names or True')
            if hasattr(callbacks, 'mode') and callbacks['mode'] is 'files_only':
                logging.info("files_only mode, no concat or post")
                return
            with open(out, 'w') as outfile:
                for fname in files:
                    with open(fname) as infile:
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
    
    def FileSet(self, out = None, files = None, callbacks = {}):
        if type(files) is not list:
            raise TypeError('files list is a required  argument')
        if type(out) is not str:
            raise TypeError('out is a required argument')
        if hasattr(self.file_set, out):
            raise Exception('out file is already in use by another FileSet')
        if out in files:
            raise Exception('cannot watch out file')
        self.file_set[out] = {'files' : files, 'callbacks' : callbacks}
        return out
    
    def MirrorSet(self, orig = None, new = None, addl = None):
        if type(orig) is not str:
            raise TypeError('orig list is a required  argument')
        if type(new) is not str:
            raise TypeError('new is a required argument')
        try:
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
        except:
            raise
    
    def stop(self):
        self.observer.stop()
        
    def start(self):
        event_handler = ChangeHandler(self._on_file_changed)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.root, recursive=True)
        self.observer.start()
    
    def __init__(self, root = None):
        if type(root) is not str:
            raise TypeError('root is required as argument in object instantation')
        self.root = os.path.abspath(root)

