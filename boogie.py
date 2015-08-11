#!/usr/bin/python2 -tt

# Generates a cache of bugzilla bugs according to some 
# criteria
# Uses functions from the bugzilla library and its 
# bugzilla client


# Instead of reinventing the wheel we use the functions arleady created on
# the bugzilla client

import os
import sys
import locale
#import logging
import bugzilla

from jinja2 import Environment, FileSystemLoader

#log = bugzilla.log

#TODO  add command line options
#log.setLevel(logging.DEBUG)

#if global_opt.debug:
#    log.setLevel(logging.DEBUG)
#elif global_opt.verbose:
#    log.setLevel(logging.INFO)
#else:
#    log.setLevel(logging.WARN)




default_bz = 'https://bugzilla.redhat.com/xmlrpc.cgi'

cookiefile = None
tokenfile = None
bz = bugzilla.Bugzilla(url = default_bz,
    cookiefile = cookiefile,
    tokenfile = tokenfile,
    sslverify = True)

templateLoader = FileSystemLoader( searchpath="./" )
env = Environment(loader=templateLoader)

DOCUMENT_ROOT = "~/public_html"

options = {
'product'                : None,
'component'              : ["openstack-packstack", "openstack-puppet-modules"],
'sub_component'          : None,
'version'                : None,
'reporter'               : None,
'bug_id'                 : None,
'short_desc'             : None,
'long_desc'              : None,
'cc'                     : None,
'assigned_to'            : None,
'qa_contact'             : None,
'bug_status'             : ['NEW', 'ASSIGNED', 'POST'],
'blocked'                : None,
'dependson'              : None,
'keywords'               : None,
'keywords_type'          : None,
'url'                    : None,
'url_type'               : None,
'status_whiteboard'      : None,
'status_whiteboard_type' : None,
'fixed_in'               : None,
'fixed_in_type'          : None,
'flag'                   : None,
'alias'                  : None,
'qa_whiteboard'          : None,
'devel_whiteboard'       : None,
'boolean_query'          : None,
'bug_severity'           : ['urgent', 'high'],
'priority'               : None,
'target_milestone'       : None,
'quicksearch'            : None,
'savedsearch'            : None,
'savedsearch_sharer_id'  : None,
'tags'                   : None,
}
 

def get_bugs(bz, query_opts):

    include_fields =  ["id", "product", "status", "assigned_to", "summary", "whiteboard", "flags", "keywords", "blocks", "description", "priority", "severity", "comments"]
    built_query = bz.build_query(
        product                = query_opts['product'],
        component              = query_opts['component'],
        sub_component          = query_opts['sub_component'],
        version                = query_opts['version'],
        reporter               = query_opts['reporter'],
        bug_id                 = query_opts['bug_id'],
        short_desc             = query_opts['short_desc'],
        long_desc              = query_opts['long_desc'],
        cc                     = query_opts['cc'],
        assigned_to            = query_opts['assigned_to'],
        qa_contact             = query_opts['qa_contact'],
        status                 = query_opts['bug_status'],
        blocked                = query_opts['blocked'],
        dependson              = query_opts['dependson'],
        keywords               = query_opts['keywords'],
        keywords_type          = query_opts['keywords_type'],
        url                    = query_opts['url'],
        url_type               = query_opts['url_type'],
        status_whiteboard      = query_opts['status_whiteboard'],
        status_whiteboard_type = query_opts['status_whiteboard_type'],
        fixed_in               = query_opts['fixed_in'],
        fixed_in_type          = query_opts['fixed_in_type'],
        flag                   = query_opts['flag'],
        alias                  = query_opts['alias'],
        qa_whiteboard          = query_opts['qa_whiteboard'],
        devel_whiteboard       = query_opts['devel_whiteboard'],
        boolean_query          = query_opts['boolean_query'],
        bug_severity           = query_opts['bug_severity'],
        priority               = query_opts['priority'],
        target_milestone       = query_opts['target_milestone'],
        emailtype              = "exact",
        booleantype            = "substring",
        include_fields         = include_fields,
        quicksearch            = query_opts['quicksearch'],
        savedsearch            = query_opts['savedsearch'],
        savedsearch_sharer_id  = query_opts['savedsearch_sharer_id'],
        tags                   = query_opts['tags'])
    
    return bz.query(built_query)

def generate(severity, priority, status):
    template = env.get_template('templates/bug.html')
    output = template.render(severity_bugs = severity, priority_bugs = priority, 
             status_buglist = status)
    print to_encoding(output)
    with open("%s/bugs.html" % (DOCUMENT_ROOT), 'w') as f:
        f.write(to_encoding(output))

def to_encoding(ustring):
    string = ''
    if isinstance(ustring, basestring):
        string = ustring
    elif ustring is not None:
        string = str(ustring)

    if hasattr(sys.version_info, "major") and sys.version_info.major >= 3:
        return string
    else:
        preferred = locale.getpreferredencoding()
        if "PYTHON_BUGZILLA_TEST_SUITE" in os.environ:
            preferred = "UTF-8"
        return string.encode(preferred, 'replace')


def set_options(options, opt, val):
    for key in options:
        if key != 'component' and key != 'bug_status':
            options[key] = None
    options[opt] = val


set_options(options, 'bug_severity', ['urgent', 'high'])
print "Getting severity bugs..."
severity = get_bugs(bz, options)

print "Getting priority bugs..."
set_options(options, 'priority', ['urgent', 'high'])
priority = get_bugs(bz, options)

print "Getting status bugs..."
set_options(options, 'bug_status', ['NEW', 'ASSIGNED', 'POST'])
status = get_bugs(bz, options)
generate(severity, priority, status)
