#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

import argparse
import sys
import os
import datetime
import httplib
import urllib
import urllib2
from ntlm import HTTPNtlmAuthHandler

# Constant definition
ERR_MSG_BADDAY = '''Invalid Argument for Weekday:
    Must be Monday, Tuesday, Wednesday,
    Thursday, Friday, Saturday or Sunday.'''

ERR_MSG_BADPRJ = '''Invalid Argument for Project:
    Use --list argument to print valid project names.'''

ERR_MSG_BADPRJPATH = ''' Invalid enviornment variable value for: 
    PRJ_META_PATH
    
    Said variable should provide valid path to project metadata file.'''

ERR_MSG_BADUSER = '''Invalid enviornment variable value for: 
    USER
    
    Said variable should provide valid username.'''

ERR_MSG_BADPASS = '''Invalid enviornment variable value for: 
    ME_KEY
    
    Said variable should provide valid user password.'''

DAY_DICT = {'monday' : 0, 'tuesday' : 1, 'wednesday' : 2, 
           'thursday' : 3, 'friday' : 4, 'saturday' : 5, 'sunday' : 6}

TSS_URL = "http://intra.fry.com/tools/tss/xt_tss.asp"

# parse the settings file ('projects.txt' in the same directory as the script)
# for project values dictionary for values depending upon task
path = os.environ.get('PRJ_META_PATH')
if (path == None):
    print ERR_MSG_BADPRJPATH
    sys.exit(1)

projects = {}
defaultPrj = None
f = open(path, 'r')
for line in f:
    parts = line.split('|')

    if parts[0].startswith('*'):
        parts[0] = parts[0].lstrip('*')
        defaultPrj = parts[0]

    projects[parts[0]] = {'taskID' : parts[1], 'taskName' : parts[2], 
                          'projectID' : parts[3], 'jobID' : parts[4], 
                          'catID' : parts[5], 'jobTypeID' : parts[6]}
f.close()

# Parse the command-line arguments 
parser = argparse.ArgumentParser(description="Submit hours to TSS")
parser.add_argument("-d", "--day", dest="weekday", 
                    help='Weekday to submit time for (Monday ... Sunday). '
                    'If not provided, current date is assumed.')
parser.add_argument("-p", "--project", dest="project",
                    help='Project name to submit time for. If not provided, ' 
                    'default project is assumed.')
parser.add_argument("-l", "--list", 
                    action="store_true", dest="prjList", default=False,
                    help="Print all valid project names.")
parser.add_argument("-dp", "--default", 
                    action="store_true", dest="prjDefault", default=False,
                    help="Print default project name.")
parser.add_argument('hours', type=int, nargs='?', 
                    help='Number of hours to submit. (Required for submission.)')
parser.add_argument('comment', nargs='?', 
                    help='Comment associated with hour submission. (Required '
                    'for submission)')
args = parser.parse_args()

# Check for CLI conditions & validity
weekday = None
if (args.weekday != None):
    if (DAY_DICT.has_key((args.weekday).lower())): 
        weekday = DAY_DICT.get((args.weekday).lower())
    else:
        # Throw an exception and exit
        print ERR_MSG_BADDAY
        sys.exit(1) 

project = None
if (args.project != None):
    if(projects.has_key((args.project).lower())):
        project = projects.get((args.project).lower())
    else:
        # Throw an exception and exit
        print ERR_MSG_BADPRJ
        sys.exit(1)
else:
    project = projects.get(defaultPrj)

# Check for the CLI "info" conditions (list and default), 
# if detected, then do and exit
if (args.prjList):
    print 'Valid list of Project Names:'
    print '\t' + str(projects.keys())
    sys.exit(0)

if (args.prjDefault):
    print 'Default Project:'
    print '\t' + defaultPrj
    sys.exit(0)

# Check to ensure that required arguments (hours & comment)
# for all but the listing options (above) have been properly provided
if (args.hours == None):
    print 'Invalid input for required argument \'hours\'.'
    sys.exit(1)
if (args.comment == None):
    print 'Invalid input for required argument \'comment\'.'
    sys.exit(1)

# Calculate dates for the current week
# First, get the day of the week we're on (note: 0 is Monday, Sunday is 6)
today = datetime.date.today()
todayDay = today.weekday()

# Second, figure out the mon/day/yr for each Mon-Fri for the week we're on.
# Then, create timedeltas for each of the other 6 days.
# Then, use these to create day objects, put into a dictionary indexed by day #.

dayList = []
for i in range(7):
    if i < todayDay:
        # then go backward
        dayList.append(today - datetime.timedelta(todayDay - i))
    elif i > todayDay:
        # then go forward
        dayList.append(today + datetime.timedelta(i - todayDay))
    else:
        # then today
        dayList.append(today)

# Determine what the date is for requested day to submit.
# (If no day provided, assume 'today' is the submission target.)
submissionDate = today    
if (weekday != None):
    # then we're using what the user provided
    submissionDate = dayList[weekday]

formatDate = ''.join([str(submissionDate.month), '/', 
                      str(submissionDate.day), '/', 
                      str(submissionDate.year)])

# Setup NTLM authenticated HTTP connection & submit hours
user = 'fry\\' + os.environ.get('DOMAIN_USER')
if (user == None):
    print ERR_MSG_BADUSER
    sys.exit(1)

password = os.environ.get('ME_KEY')
if (password == None):
    print ERR_MSG_BADPASS
    sys.exit(1)

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, TSS_URL, user, password)

# create the NTLM authentication handler
auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    
# create and install the opener
opener = urllib2.build_opener(auth_NTLM)
urllib2.install_opener(opener)

# post submission to TSS
params = urllib.urlencode({'date' : formatDate, 'task_id' : project.get('taskID'), 
                           'task_name' : project.get('taskName'), 
                           'hrs' : args.hours, 
                           'project_type' : '', 
                           'project_id' : project.get('projectID'),
                           'job_id' : project.get('jobID'), 
                           'category_id' : project.get('catID'), 
                           'job_type_id' : project.get('jobTypeID'),
                           'tasknum' : '', 'comments' : args.comment,
                           'submitIsPending' : 'false', 'GO_add' : 'Submit', 
                           'tss_update' : '', 'tss_update_id' : ''})
response = urllib2.urlopen(TSS_URL, params)
