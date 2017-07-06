#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys, os, re
import logging
import getopt

scriptName = os.path.basename(os.path.abspath(sys.argv[0])).replace('.pyc', '.py')

# If this script is called via a symbolic link:
# this returns the symbolic link's directory:
# scriptDir = os.path.dirname(os.path.abspath(sys.argv[0]))
# this returns the symbolic link's target's directory:
scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))

sys.path.append(scriptDir)

if sys.version_info[0] == 3:  # for python3
    xrange = range

#=============================================

# For error messages

import inspect

def srcLineNum(caller=1):
    callerframerecord = inspect.stack()[caller] # caller=0 represents this line
                                                # caller=1 represents line at caller
                                                # caller=2 represents line at the caller's caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # print info.filename                       # __FILE__     -> Test.py
    # print info.function                       # __FUNCTION__ -> Main
    # print info.lineno                         # __LINE__     -> 13
    return str(info.lineno)

#============================================= 

# dprint = debug print
#
# Compare the output from:
# print(91, 'one\ntwo\nthree')  # prints out unwanted tuple (91, 'one\ntwo\nthree') .  tuple prevents newlines from getting printed out.
# dprint(91, 'one\ntwo\nthree') # prints out strings instead of tuple, and so newlines get printed.

def dprint(*params):
    separator = ''
    if 'int' not in str(type(params[0])):
        sys.stdout.write(separator + str(srcLineNum(caller=2)))
        separator = ','

    for param in params:
        sys.stdout.write(separator + str(param))
        separator = ','
    sys.stdout.write('\n')

#============================================= 
def debug_option(location=''):

    if os.environ.get('MI_DEBUG') != None:
        if location != '':
            print("debug_option() called from " + location)

        print(__file__ + ": " + srcLineNum() + ": debug enabled")
        return True
    else:
        return False

#=============================================

try:
    debug_flag
except NameError:
    debug_flag = False
#   print "well, it WASN'T defined after all!"
# else:
#   print "sure, it was defined."

#=============================================

global progress_flag
progress_flag = False # Display non-optional non-debug INFO output so user will see some progress messages.
global progress_fd

# Example:
# report_progress(run_command_on_machines.machineName + ">" + prev_func + ">" + curr_func + ">" + cmd)

def report_progress(msg):
    if progress_flag == True:
        display_msg = "Progress: " + msg
        print(display_msg)
        # progress_fd.write(display_msg + '\n')
        # logging.debug(display_msg)

# progress_message_file = scriptName+"_progress.log"
# progress_fd = open(progress_message_file, "w")

#===================================================

def dump_callers_variables(caller_frame, var_dump_file):
    from pprint import pformat

    # print(84, caller_frame)

    output = []

    fd = open(var_dump_file, 'w')

    """Print the local variables in the caller's frame."""
    screen_columns = int(os.getenv("COLUMNS", '80'))
    frame = inspect.currentframe()
    fd.write("======================================\n")
    output.append("======================================")
    fd.write("locals_from_caller():\n")
    output.append("locals_from_caller():")
    try:
        # for entry in pformat(frame.f_back.f_locals).split('\n'):
        for entry in pformat(caller_frame.f_locals).split('\n'):
            fd.write(entry +'\n')
            entry_truncated = entry[:screen_columns] + (entry[screen_columns:] and '..')
            output.append(entry_truncated)
    except:
        # del frame  # keep frame for next check below
        pass

    output.append("======================================")
    output.append("globals_from_caller():")
    try:
        # for entry in pformat(frame.f_back.f_globals).split('\n'):
        for entry in pformat(caller_frame.f_globals).split('\n'):
            fd.write(entry +'\n')
            entry_truncated = entry[:screen_columns] + (entry[screen_columns:] and '..')
            output.append(entry_truncated)
    finally:
        del frame

    fd.close()

    return output


#=============================================

def debug_run_status(msg=''):
    from columnize_output import columnize_output
    import inspect
    # frame = inspect.currentframe().f_back
    # full_msg = os.path.basename('{0.f_code.co_filename}'.format(frame)) + ',' + '{0.f_lineno}'.format(frame) + ',' + '{0.f_code.co_name}'.format(frame) + ',' + msg

    list_of_list_of_string = []
    output = []

    output.append("")
    list_of_list_of_string.append(["Debug dump--  " + msg.strip() ])
    list_of_list_of_string.append(["stack dump: "])
    list_of_list_of_string.append(["filename","lineno","function", "line" ])
    for entry in reversed(inspect.stack()):
    #   frame = callerframerecord[0]
    #   info = inspect.getframeinfo(frame)
    # for entry in inspect.getouterframes(inspect.currentframe()):
        (dont_care, filename, line_number, function_name, line, dont_care2) = entry
        list_of_list_of_string.append([filename.strip(), line_number, function_name, line[0].strip()])

    # for row in list_of_list_of_string:
    #     output.append(94, row)

    rc, full_msg_columnized = columnize_output(input_data=list_of_list_of_string, justify_cols='L')

    if 'log' in vars() or 'log' in globals():
        log.debug(full_msg_columnized)

    for row in full_msg_columnized:
        if 'list' in str(type(row)):
            if len(row) == 1:
                output.append(row[0].rstrip())
                continue
        elif 'str' in str(type(row)):
            output.append(row.rstrip())
            continue
        output.append(row.rstrip())

    var_dump_file = scriptDir + "/" + scriptName + "_var_dump_debug_run_status.log"
    caller_frame = inspect.currentframe().f_back
    output += dump_callers_variables(caller_frame, var_dump_file)

    return output


def report_status(status_type, location='', rc=-1, results='', msg=''):
    if location == '':
        location = location.replace('<module>', 'main')  # if in main using  inspect.stack()[0][3] to get the current func name

    msg = status_type + ": " + str(location) + ": rc = " + str(rc) + ".  results = " + str(results)
    if progress_flag == True:
        report_progress(msg)
    else:
        print(msg)
    if status_type == 'ERROR':
        logging.error(msg)
    if status_type == 'INFO':
        logging.info(msg)


#===================================================

global log
log = ''
global logfile
logfile = ''
global logging_screen
logging_screen = True

logfile = scriptName + '.log'

def logging_setup(logfilename=logfile, loglevel=logging.ERROR, logMsgPrefix='', mode='a', common_format=''):
    global log
    # global console

    # logMsgPrefix can be used tp filter out log messages from real script user output.
    # common_format = logMsgPrefix + ': %(asctime)s %(levelname)s: %(filename)s,%(lineno)s,%(funcName)s: %(message)s'
    common_format = logMsgPrefix + ',%(asctime)s,%(levelname)s,%(message)s'
    datetime_format = '%d %b %H:%M:%S'
    logging.basicConfig(format=(common_format), datefmt=datetime_format)

    log = logging.getLogger(scriptName)
    logfile = logfilename
    try:
        handler = logging.FileHandler(logfile, mode)
    except:
        logfile = logfilename
        handler = logging.FileHandler(logfile, mode)
    formatter = logging.Formatter((common_format), datefmt=datetime_format)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(loglevel)
    return log

    # if logfile != '':
        # set up logging to file

    # else:
    #    logging.basicConfig(level=logging.INFO, format=('%(asctime)s,%(levelname)s,%(funcName)s,%(message)s'))

    if logging_screen:
        # logging.basicConfig(level=logging.DEBUG,
        #                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        #                     datefmt='%m-%d %H:%M',
        #                     filename='/temp/myapp.log',
        #                     filemode='w')

        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(loglevel)
        # set a format which is simpler for console use
        formatter = logging.Formatter(common_format, datefmt='%d %b %H:%M:%S')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        # log = logging.getLogger(scriptName)
        # log.addHandler(console)
        log = logging.getLogger('').addHandler(console)

def setLoggingLevel(loglevel):
    global console
    log.setLevel(loglevel)

def test_func():
    log.error("Error in command")
    log.debug("debug output")
    # debug_run_status(inspect.stack()[0][3] + ", " + srcLineNum(), "test debug messages") # Our custom debug output format.
    debug_run_status("test debug messages") # Our custom debug output format.


#===================================================

def reportError(msg='', mode='screen_and_return'):
    # print(186)
    # for line in msg.split('\n'):
    #     print(187, line)

    sys.stdout.flush()

    stack_trace = ''
    if 'Stack Trace:' not in msg:
        for callerframerecord in inspect.stack()[1:]:
            frame = callerframerecord[0]
            info = inspect.getframeinfo(frame)
            # print info.filename                       # __FILE__     -> Test.py
            # print info.function                       # __FUNCTION__ -> Main
            # print info.lineno                         # __LINE__     -> 13
            stack_entry = '\nfilename: ' + info.filename + ', lineno: ' + str(info.lineno) + ', function: ' + str(info.function)
            if 'reportError' not in stack_entry and stack_entry in msg:
                stack_trace = ''
                break
            stack_trace = stack_entry + stack_trace

    if stack_trace != '':
        msg_formatted = msg + '\nreportError Stack Trace: ' + stack_trace
    else:
        # msg_formatted = '\nreportError msg:\n' + 'ERROR: ' + str(msg)
        msg_formatted = msg

    var_dump_file = scriptDir + "/" + scriptName + "_var_dump_reportError.log"
    caller_frame = inspect.currentframe().f_back
    dump_callers_variables(caller_frame, var_dump_file)

    if 'Variables Dump File:' not in msg_formatted:
        msg_formatted += "\nVariables Dump File: " + var_dump_file + '\n'

    if mode == 'screen_and_return':
       if log == '':
           print("ERROR: " + msg_formatted)
       else:
           log.error(msg_formatted)

    # print(234)
    # for line in msg_formatted.split('\n'):
    #     print(237, line)

    return msg_formatted

#===================================================

def reportWarning(msg):
    log.warn(msg)

#===================================================

def reportInfo(msg):
    log.info(msg)

#===================================================

def reportDebug(msg):
    debug_run_status(msg)

#===================================================

def user_input(prompt='',  defaultText=''):
    # # sys.stdout.write(prompt)
    # # sys.stdout.flush()
    # # return sys.stdin.readline().strip('\n')  # does not have command line history
    # if (sys.version_info > (3, 0)):
    #     return input(prompt)
    # else:
    #     return raw_input(prompt)

    import readline
    readline.set_startup_hook(lambda: readline.insert_text(defaultText))
    if (sys.version_info > (3, 0)):
        return input(prompt)
    else:
        return raw_input(prompt)

#===================================================

def print_multi_array(top_of_list, indent=''):
    if isinstance(top_of_list, list) == False:
        print(indent + top_of_list)
        return
    print(indent + "new_array")
    for row in top_of_list:
        print_multi_array(row, indent + '   ')

#===================================================

def dump_obj_type(obj, indent):
    obj_type = type(obj)
    print(indent + str(obj_type))
    if obj_type is list or obj_type is tuple:
        for loop in obj:
            dump_obj_type(loop, indent+'   ')

#===================================================

# Example main code

if __name__ == '__main__':
    # global debug_flag

    # Set a global debug flag based on an environment variable, or use logging.DEBUG below, or both.
    debug_flag = debug_option(__file__ + "," + srcLineNum())

    logging_setup(logMsgPrefix=scriptName, logfilename=scriptName + '.log', loglevel=logging.ERROR)

    if len(sys.argv) < 2:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["list=", "of=", "debug", "unit_test=" ])
    except:
        print("ERROR: Unrecognized runstring option.")
        usage()

    list_option = ''
    of_option = 'full'

    for opt, arg in opts:
        if opt == "--list":
            list_option = arg
        elif opt == "--of":
            of_option = arg
        elif opt == "--debug":
            setLoggingLevel(logging.DEBUG)
            debug_flag = True
        # elif opt == "--unit_test":
        else:
            print("ERROR: Runstring options.")
            usage()

    # If you have non-hyphenated options in the runstring such as filenames, you can get them from the runstring like this:
    # file1 = args[0]
    # file2 = args[1]

    # As examples and for testing, you can call above logging_wrapper functions here.

    sys.exit(0)




