import sys
import os
import logging
from configobj import ConfigObj
from optparse import OptionParser, OptionValueError
from api_clients import api_client as apc
import json
import shutil
import commands

sys.path.append('/usr/local/lib/airtime/media-monitor/mm2/')
from media.monitor.pure import is_file_supported

# create logger
logger = logging.getLogger()

# no logging
ch = logging.StreamHandler()
logging.disable(50)

# add ch to logger
logger.addHandler(ch)

if (os.geteuid() != 0):
    print 'Must be a root user.'
    sys.exit()

# loading config file
try:
    config = ConfigObj('/usr/local/etc/airtime/media-monitor.cfg')
except Exception, e:
    print('Error loading config file: %s', e)
    sys.exit()

api_client = apc.AirtimeApiClient(config)

#helper functions
# copy or move files
# flag should be 'copy' or 'move'
def copy_or_move_files_to(paths, dest, flag):
    try:
        for path in paths:
            if (path[0] == "/" or path[0] == "~"):
                path = os.path.realpath(path)
            else:
                path = currentDir+path
            path = apc.encode_to(path, 'utf-8')
            dest = apc.encode_to(dest, 'utf-8')
            if(os.path.exists(path)):
                if(os.path.isdir(path)):
                    path = format_dir_string(path)
                    #construct full path
                    sub_path = []
                    for temp in os.listdir(path):
                        sub_path.append(path+temp)
                    copy_or_move_files_to(sub_path, dest, flag)
                elif(os.path.isfile(path)):
                    #copy file to dest
                    if(is_file_supported(path)):
                        destfile = dest+os.path.basename(path)
                        if(flag == 'copy'):
                            print "Copying %(src)s to %(dest)s..." % {'src':path, 'dest':destfile}
                            shutil.copyfile(path, destfile)
                        elif(flag == 'move'):
                            print "Moving %(src)s to %(dest)s..." % {'src':path, 'dest':destfile}
                            shutil.move(path, destfile)
            else:
                print "Cannot find file or path: %s" % path
    except Exception as e:
            print "Error: ", e

def format_dir_string(path):
    if(path[-1] != '/'):
        path = path+'/'
    return path

def helper_get_stor_dir():
    try:
        res = api_client.list_all_watched_dirs()
    except Exception, e:
        return res

    if(res['dirs']['1'][-1] != '/'):
        out = res['dirs']['1']+'/'
        return out
    else:
        return res['dirs']['1']

def checkOtherOption(args):
    for i in args:
        if(i[0] == '-'):
            return True

def errorIfMultipleOption(args, msg=''):
    if(checkOtherOption(args)):
        if(msg != ''):
            raise OptionValueError(msg)
        else:
            raise OptionValueError("This option cannot be combined with other options")

def printHelp():
    storage_dir = helper_get_stor_dir()
    if(storage_dir is None):
        storage_dir = "Unknown"
    else:
        storage_dir += "imported/"
    print """
========================
 Airtime Import Script
========================
There are two ways to import audio files into Airtime:

1) Use airtime-import to copy or move files into the storage folder.

   Copied or moved files will be placed into the folder:
   %s

   Files will be automatically organized into the structure
   "Artist/Album/TrackNumber-TrackName-Bitrate.file_extension".

2) Use airtime-import to add a folder to the Airtime library ("watch" a folder).

   All the files in the watched folder will be imported to Airtime and the
   folder will be monitored to automatically detect any changes. Hence any
   changes done in the folder(add, delete, edit a file) will trigger
   updates in Airtime library.
""" % storage_dir
    parser.print_help()
    print ""

def CopyAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) == 0 ):
        raise OptionValueError("No argument found. This option requires at least one argument.")
    stor = helper_get_stor_dir()
    if(stor is None):
        print "Unable to connect to the Airtime server."
        return
    dest = stor+"organize/"
    copy_or_move_files_to(parser.rargs, dest, 'copy')

def MoveAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) == 0 ):
        raise OptionValueError("No argument found. This option requires at least one argument.")
    stor = helper_get_stor_dir()
    if(stor is None):
        exit("Unable to connect to the Airtime server.")
    dest = stor+"organize/"
    copy_or_move_files_to(parser.rargs, dest, 'move')

def WatchAddAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) > 1):
        raise OptionValueError("Too many arguments. This option requires exactly one argument.")
    elif(len(parser.rargs) == 0 ):
        raise OptionValueError("No argument found. This option requires exactly one argument.")
    path = parser.rargs[0]
    if (path[0] == "/" or path[0] == "~"):
        path = os.path.realpath(path)
    else:
        path = currentDir+path
    path = apc.encode_to(path, 'utf-8')
    if(os.path.isdir(path)):
        #os.chmod(path, 0765)
        try:
            res = api_client.add_watched_dir(path)
        except Exception, e:
            exit("Unable to connect to the server.")
        # sucess
        if(res['msg']['code'] == 0):
            print "%s added to watched folder list successfully" % path
        else:
            print "Adding a watched folder failed: %s" % res['msg']['error']
            print "This error most likely caused by wrong permissions"
            print "Try fixing this error by chmodding the parent directory(ies)"
    else:
        print "Given path is not a directory: %s" % path

def WatchListAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) > 0):
        raise OptionValueError("This option doesn't take any arguments.")
    try:
        res = api_client.list_all_watched_dirs()
    except Exception, e:
        exit("Unable to connect to the Airtime server.")
    dirs = res["dirs"].items()
    # there will be always 1 which is storage folder
    if(len(dirs) == 1):
            print "No watch folders found"
    else:
        for key, v in dirs:
            if(key != '1'):
                print v

def WatchRemoveAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) > 1):
        raise OptionValueError("Too many arguments. This option requires exactly one argument.")
    elif(len(parser.rargs) == 0 ):
        raise OptionValueError("No argument found. This option requires exactly one argument.")
    path = parser.rargs[0]
    if (path[0] == "/" or path[0] == "~"):
        path = os.path.realpath(path)
    else:
        path = currentDir+path
    path = apc.encode_to(path, 'utf-8')
    if(os.path.isdir(path)):
        try:
            res = api_client.remove_watched_dir(path)
        except Exception, e:
            exit("Unable to connect to the Airtime server.")
        # sucess
        if(res['msg']['code'] == 0):
            print "%s removed from watch folder list successfully." % path
        else:
            print "Removing the watch folder failed: %s" % res['msg']['error']
    else:
        print "The given path is not a directory: %s" % path

def StorageSetAction(option, opt, value, parser):
    bypass = False
    isF = '-f' in parser.rargs
    isForce = '--force' in parser.rargs
    if(isF or isForce ):
        bypass = True
        if(isF):
            parser.rargs.remove('-f')
        if(isForce):
            parser.rargs.remove('--force')
    if(not bypass):
        errorIfMultipleOption(parser.rargs, "Only [-f] and [--force] option is allowed with this option.")
        possibleInput = ['y','Y','n','N']
        confirm = raw_input("Are you sure you want to change the storage direcory? (y/N)")
        confirm = confirm or 'N'
        while(confirm  not in possibleInput):
            print "Not an acceptable input: %s\n" % confirm
            confirm = raw_input("Are you sure you want to change the storage direcory? (y/N) ")
            confirm = confirm or 'N'
        if(confirm == 'n' or confirm =='N'):
            sys.exit(1)

    if(len(parser.rargs) > 1):
        raise OptionValueError("Too many arguments. This option requires exactly one argument.")
    elif(len(parser.rargs) == 0 ):
        raise OptionValueError("No argument found. This option requires exactly one argument.")

    path = parser.rargs[0]
    if (path[0] == "/" or path[0] == "~"):
        path = os.path.realpath(path)
    else:
        path = currentDir+path
    path = apc.encode_to(path, 'utf-8')
    if(os.path.isdir(path)):
        try:
            res = api_client.set_storage_dir(path)
        except Exception, e:
            exit("Unable to connect to the Airtime server.")
        # success
        if(res['msg']['code'] == 0):
            print "Successfully set storage folder to %s" % path
        else:
            print "Setting storage folder failed: %s" % res['msg']['error']
    else:
        print "The given path is not a directory: %s" % path

def StorageGetAction(option, opt, value, parser):
    errorIfMultipleOption(parser.rargs)
    if(len(parser.rargs) > 0):
        raise OptionValueError("This option does not take any arguments.")
    print helper_get_stor_dir()

class OptionValueError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg

usage = """[-c|--copy FILE/DIR [FILE/DIR...]] [-m|--move FILE/DIR [FILE/DIR...]]
       [--watch-add DIR] [--watch-list] [--watch-remove DIR]
       [--storage-dir-set DIR] [--storage-dir-get]"""

parser = OptionParser(usage=usage, add_help_option=False)
parser.add_option('-c','--copy', action='callback', callback=CopyAction, metavar='FILE', help='Copy FILE(s) into the storage directory.\nYou can specify multiple files or directories.')
parser.add_option('-m','--move', action='callback', callback=MoveAction, metavar='FILE', help='Move FILE(s) into the storage directory.\nYou can specify multiple files or directories.')
parser.add_option('--watch-add', action='callback', callback=WatchAddAction, help='Add DIR to the watched folders list.')
parser.add_option('--watch-list', action='callback', callback=WatchListAction, help='Show the list of folders that are watched.')
parser.add_option('--watch-remove', action='callback', callback=WatchRemoveAction, help='Remove DIR from the watched folders list.')
parser.add_option('--storage-dir-set', action='callback', callback=StorageSetAction, help='Set storage dir to DIR.')
parser.add_option('--storage-dir-get', action='callback', callback=StorageGetAction, help='Show the current storage dir.')
parser.add_option('-h', '--help', dest='help', action='store_true', help='show this help message and exit')

# pop "--dir"
sys.argv.pop(1)
# pop "invoked pwd"
currentDir = sys.argv.pop(1)+'/'

if('-l' in sys.argv or '--link' in sys.argv):
    print "\nThe [-l][--link] option is deprecated. Please use the --watch-add option.\nTry 'airtime-import -h' for more detail.\n"
    sys.exit()
if('-h' in sys.argv):
    printHelp()
    sys.exit()
if(len(sys.argv) == 1 or '-' not in sys.argv[1]):
    printHelp()
    sys.exit()

try:
    (option, args) = parser.parse_args()
except Exception, e:
    printHelp()
    if hasattr(e, 'msg'):
        print "Error: "+e.msg
    else:
        print "Error: ",e
    sys.exit()
except SystemExit:
    printHelp()
    sys.exit()

if option.help:
    printHelp()
    sys.exit()




