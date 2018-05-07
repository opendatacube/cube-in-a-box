# magic function that checks a cell for pep8 compliance
# %%pep8
# a=1
# should give an error about missing spaces

import sys
import tempfile
import io
import logging
import pep8 as pep8_module


from IPython.core.magic import register_cell_magic


logger = logging.getLogger('pep8')
if not logging.root.hasHandlers():
    handler = logging.StreamHandler(stream=sys.stderr)
    # format = '%(lineno)d: %(msg)s'
    # handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)


def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    pass


def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass


@register_cell_magic
def pep8(line, cell):
    """pep8 cell magic"""

    logger.setLevel(logging.INFO)
    # output is written to stdout
    # remember and replace
    old_stdout = sys.stdout
    # temporary replace
    sys.stdout = io.StringIO()
    # store code in a file, todo unicode
    with tempfile.NamedTemporaryFile(mode='w') as f:
        # save to file
        f.write(cell + '\n')
        # make sure it's written
        f.flush()
        # now we can check the file by name.
        # we might be able to use 'stdin', have to check implementation
        format = '%(row)d:%(col)d: %(code)s %(text)s'
        pep8style = pep8_module.StyleGuide(format=format)
        # check the filename
        # reusing the file is not allowed under windows
        pep8style.check_files(paths=[f.name])
        # split lines
        stdout = sys.stdout.getvalue().splitlines()
    for line in stdout:
        logger.info(line)
    # restore
    sys.stdout = old_stdout
    return
