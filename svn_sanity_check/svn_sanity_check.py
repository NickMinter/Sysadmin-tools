#!/usr/bin/env python

"""
Crawl a working copy directory, record status information to a log file.
"""
import ConfigParser
import mail_team
import os
import os.path
import platform
import svn.client
import svn.core
import svn.wc
import sys

# FIXME: Global var
global data
global section

# Change server name with each deployment
# FIXME: add server name
server_name = platform.node()

# Change verbosity of the scripts output
verbose = 0
# FIXME: What is the prefix used for in SVN?
prefix = None

def process_data(data):
    # FIXME: Global var
    global section
    #FIXME: Check path is correct
    
    #log_file = 'E:\\weblogs\\+section\\'+'svn_check.log'
    #file = open(log_file, 'a')
    #try:
    #    file.write(data)
    #    file.write("\n")  
    #except IOError, e:
    #    print e
    try:
        mail_team.email_results(server_name,section,data)
    except Exception, e:
        print e
    print data
    

def generate_status_code(status):
    """Translate a status value into a single-character status code,
    using the same logic as the Subversion command-line client.
    Change the standard status messages to make some form of sense without
    ambiguity
    """
    code_map = { svn.wc.svn_wc_status_none        : ' ',
                 svn.wc.svn_wc_status_normal      : ' ',
                 svn.wc.svn_wc_status_added       : 'Added',
                 svn.wc.svn_wc_status_missing     : 'Missing',
                 svn.wc.svn_wc_status_incomplete  : 'Incomplete',
                 svn.wc.svn_wc_status_deleted     : 'Deleted',
                 svn.wc.svn_wc_status_replaced    : 'Replaced',
                 svn.wc.svn_wc_status_modified    : 'Modified',
                 svn.wc.svn_wc_status_conflicted  : 'Conflicted',
                 svn.wc.svn_wc_status_obstructed  : 'Obstructed',
                 svn.wc.svn_wc_status_ignored     : 'Ignored',
                 svn.wc.svn_wc_status_external    : 'External',
                 svn.wc.svn_wc_status_unversioned : 'Unversioned',
               }
    return code_map.get(status, '?')

def do_status(wc_path, verbose, prefix):
    # Build a client context baton.
    ctx = svn.client.svn_client_create_context()

    def _status_callback(path, status):
        global data
        """A callback function for svn_client_status."""

        # Print the path, minus the bit that overlaps with the root of
        # the status crawl
        text_status = generate_status_code(status.text_status)
        prop_status = generate_status_code(status.prop_status)
        prefix_text = ''
        if prefix is not None:
            prefix_text = prefix + " "
        #FIXME: Here's our output.. format it and direct it to the correct path.
        #print('%s%s%s  %s' % (prefix_text, text_status, prop_status, path))
        data = text_status+" "+path
        
        process_data(data)

    # Do the status crawl, using _status_callback() as our callback function.
    revision = svn.core.svn_opt_revision_t()
    revision.type = svn.core.svn_opt_revision_head
    svn.client.svn_client_status2(wc_path, revision, _status_callback,
                                  svn.core.svn_depth_infinity, verbose,
                                  0, 0, 1, ctx)
   
if __name__ == '__main__':

    try:
        #Added check to set config location on POSIX system
        # FIXME: Remove these checks in production.
        if os.name == 'nt':
            config = ConfigParser.RawConfigParser()
            config_file = config.readfp(open('E:\\webs\\'+server_name+'-svn_status.config'))
        else:
            config = ConfigParser.RawConfigParser()
            config_file = config.read(server_name+"-svn_status.config")
    except IOError:
        #FIXME: Log all exceptions to the MS Event logs
        print Exception
        sys.exit(1)
    try:
        global section
        for section in config.sections():
            for option in config.options(section):
                code_base = config.get(section,option)
                # Canonicalize the repository path.
                # FIXME: Malformated paths/options in
                # the config file cause the script to die.
                wc_path = svn.core.svn_path_canonicalize(code_base)
                path = 'E:\\weblogs\\'+section+'-svn_check.log'
                # FIXME: Remove these checks in production.
                if os.name == 'nt':
                    if os.path.isfile(path):
                        # FIXME: Make sure this removes the correct file
                        os.unlink(path)
                        # Do the real work.
                    try:
                        do_status(wc_path, verbose, prefix)
                    except svn.core.SubversionException, e:
                        sys.stderr.write("Error (%d): %s\n" % (e.apr_err, e.message))
                        sys.exit(1)
                else:
                    # Do the real work.
                    try:
                        do_status(wc_path, verbose, prefix)
                    except svn.core.SubversionException, e:
                        sys.stderr.write("Error (%d): %s\n" % (e.apr_err, e.message))
                        sys.exit(1)
    except Exception, e:
        print e
        sys.exit(1)