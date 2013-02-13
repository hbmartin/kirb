  _  __        _   _                      See example.py
 | |/ /___ _ _| |_(_)_ _ _  _ ___ _  _ ___              
 | ' </ _ \ ' \  _| | ' \ || / _ \ || (_-<              
 |_|\_\___/_||_\__|_|_||_\_,_\___/\_,_/__/              
  ___     _                     _   _            __     
 |_ _|_ _| |_ ___ __ _ _ _ __ _| |_(_)___ _ _   / _|___ 
  | || ' \  _/ -_) _` | '_/ _` |  _| / _ \ ' \  > _|_ _|
 |___|_||_\__\___\__, |_| \__,_|\__|_\___/_||_| \_____| 
  ___     ___    |___/    _                             
 | _ \___| _ )_  _(_) |__| |                            
 |   / -_) _ \ || | | / _` |                            
 |_|_\___|___/\_,_|_|_\__,_|                            


# Quick Start
import kirb and instantiate a Watcher:
path = '.'
watcher = kirb.Watcher(path)

Watchers can specify File Sets, a group of files to watch for changes.
A File Set must specify an output file and list a files to monitor:
watcher.add_file_set('styles.css', ['css/a.css', 'css/b.css'])

To start monitoring for file changes, call:
watcher.start()
After the watcher is started, all modes will also have an the callback:
onchange(changed_files_path) <bool> (see below)

To immediately apply the operations and callbacks to all File Sets without
waiting for a file to change:
watcher.compile()


# Mirrored Builds
File Sets can used to create Mirror Sets. Mirror Sets are useful for building 
variations of the main file set, i.e. for themes or customer specific builds
Mirror Sets assume that there is an identical tree structure to the file set,
with files that may be overriden in the mirror directory.
For example:
my_project.add_mirror_set('styles.css', 'customerA')
Now we are watching 'customerA/css/a.css' and 'customerA/css/b.css' (if they
exist), and if not we are continuing to watch the original File Set files (with
original order preserved). Output for the Mirror Set wil be written to
'customerA/styles.css'. Mirror Set may also be passed an optional third argument,
a list or Mirror Set only files to watch.


# Modes and Callbacks
A File Set can be passed a third argument, a dict containing configuration and
callbacks for various build stages:
watcher.add_file_set(out, js_paths, {'mode' : 'concat', 'onchange': js_lint})

Modes:
* concat (default):
  This mode reads the files in the File Set line by line and writes them to the
  File Set's out.
  Callbacks:
    * each([out, files]) <list>:
      Return a list to modify the files used for concatenation
        This could be used when watching SCSS files to generate CSS if none is
        present (assume onchange callback already compiled the modified SCSS
        file), then return a list of css paths.
    * line(str) <str>:
      Called during concatenation with line of original file
      Return value is written to concatenated final
    * post(file_path):
      Called with string path of concatenated file after concatenation

* files_only:
  This mode calls the each handler then does nothing else. It's useful for
  spriting, so the spriter could be run then return False
    * each([out, files]):

* slurp:
  This mode reads the contents of all of files into memory, which it then passes
  to a required each handler. Note this handler receives a different argument
  than the the previous two. It is useful for pickling objects together, i.e.
  to serialize template files into a single JSON object.
  * each([out,
          [[file_name_1, file_contents_1],
           [file_name_2, file_contents_2], ...]])
  


                                                               
                          11111111111                          
                    11111111111111111111111                    
                111111111111111111111111111111                 
             111111111111111111111111111111111111              
            111111111111111111111111111111111111111            
          11111111111111¶¶¶11111111¶¶¶¶1111111111111           
         11111111111111¶...¶111111¶...¶1111111111111           
        111111111111111¶...¶111111¶...¶111111111111111         
       1111111111111111¶¶.¶¶¶11111¶¶.¶¶¶111111111111111        
      11111111111111111¶¶¶¶¶¶11111¶¶¶¶¶¶11111111111111111      
    1111111111111111111¶¶¶¶¶¶11111¶¶¶¶¶¶1111111111111111111    
  111111111111110000011¶###¶1111111¶###¶111000011111111111111  
 11111111111110000000001¶#¶111111111¶#¶11000000001111111111111 
1111111111111111000001111111$$$$$$$1111111000001111111111111111
1111111111111111111111111111$22222$1111111111111111111111111111
 1111111111111111111111111111122211111111111111111111111111111 
   111111111111111111111111111111111111111111111111111111111   
       1111111111111111111111111111111111111111111111111       
        1111111111111111111111111111111111111111111111         
         11111111111111111111111111111111111111111111          
          111111111111111111111111111111111111111111           
         4441111111111111111111111111111111111111114444        
       44444441111111111111111111111111111111111144444444      
     44444444444411111111111111111111111111111144444444444     
    4444444444444444111111111111111111111144444444444444444    
   444444444444444444444444441111144444444444444444444444444   
   44444444444444444444444444      4444444444444444444444444   
     444444444444444444                44444444444444444444    
            ¯¯¯                                 ¯¯¯¯¯          
