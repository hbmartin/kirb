++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Kontinuous Integration and ReBuild
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
================================
Quick Start
================================
**Follow along with example.py**

::

 import kirb
 path = '.'
 watcher = kirb.Watcher(path)

Watchers can specify File Sets, which are a group of files to watch for changes.
A File Set must first specify an output file (where the build output is written)
and a list a files to monitor (relative to the Watcher's path)

``watcher.add_file_set('styles.css', ['css/a.css', 'css/b.css'])``

To start monitoring for file changes, call:

``watcher.start()``

Whenever css/a.css or css/b.css are modified, both files will be concatenated
(in list order) to styles.css
When your program is ready to exit, call ``watcher.stop()``

To immediately apply the operations and callbacks to all File Sets without
waiting for a file to change (i.e. may be called without ``start()`` ):

``watcher.compile()``


================================
Mirrored Builds
================================
File Sets can used to create Mirror Sets. Mirror Sets are useful for building 
variations of the main file set, such as static themes or customer tuned builds.
Mirror Sets assume that there is an identical tree structure to a given File Set
with files that may be overriden or added in the mirror directory.

``my_project.add_mirror_set('styles.css', 'customerA')``

Now we are watching 'customerA/css/a.css' and 'customerA/css/b.css' (if they
exist), and if not we are continuing to watch the original File Set files (with
original order preserved). Output for the Mirror Set will be written to
'customerA/styles.css'. Mirror Sets may also be passed an optional third
argument, a list of files for only the Mirror Set to watch.

================================
Modes
================================
add_file_set can be passed a third argument, a dict containing a mode and
callbacks for various mode-specific build stages:

``watcher.add_file_set(out, js_paths, {'mode' : 'concat', 'onchange' : js_lint})``

--------------------------------
concat
--------------------------------
This mode reads the files in the File Set line by line and writes them to the
File Set's out. This is the default mode.

**Callbacks**

* ``each([out, files]) <list>``
  
  Return a list to modify the files used for concatenation.
  This could be used when watching SCSS files to generate CSS if none is
  present (assume onchange callback already compiled the modified SCSS
  file), then return a list of css paths.
* ``line(str) <str>``
  
  Called during concatenation with line of original file
  Return value is written to concatenated final
* ``post(file_path)``
  
  Called with string path of concatenated file after concatenation

--------------------------------
files_only
--------------------------------
This mode calls the each handler then does nothing else. It's useful for
spriting, so the spriter could be run then return False

**Callbacks**

* ``each([out, files])``
  
  Same as above.

--------------------------------
slurp
--------------------------------
This mode reads the contents of all of files into memory, which it then passes
to a **required** each handler. Note this each handler receives different
arguments that the other callbacks. It is useful for pickling files
together, i.e. to serialize template files into a single JSON object.

**Callbacks**

* ``each(out, [[file_name_1, file_contents_1], [file_name_2, file_contents_2], ...])``
  
  Be careful with this, try to avoid using unless absolutely necessary.

--------------------------------
after Watcher.start()
--------------------------------
After a Watcher has been started, it will fire the onchange callback (all modes)

**Callbacks**

* ``onchange(name of changed file)``
  
  onchange will be passed a string containing the changed file's path. This is
  useful for linting, which may be needlessly expensive to run on all files in
  the File Set. Raise an exception if an error is detected.

================================
Other Options
================================
In addition to mode, add_file_set can also be passed the options:
* no_out
  Set to False to prevent the File Set from writing its output file. Default to
  True. Useful for when the File Set is only used to setup Mirror Set builds.
* prefix_chomp
  This prefix will be removed from any files in the File Set when identifying
  files to be overwritten in a Mirror Set.

.. image:: https://d2weczhvl823v0.cloudfront.net/hbmartin/kirb/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

