tss.py is a Python script for submitting timesheet entries on the Fry TimeSheet System (TSS) via the command line.  Usage can be determined by invoking the `-h` option at the command line.

## Dependencies ##

The script has been developed atop OS X (Snow Leopard and Lion) and requires the following:

* Python 2.7
* [python-ntlm][ntlm] library

The script should function in other properly configured computing environments, but no testing has been conducted for any environments other than those noted as used in development.

The script has the following configuration dependencies:

* Environment Variable "DOMAIN_USER" - Corpnet Username
* Environment Variable "ME_KEY" - Corpnet Password
* Environment Variable "PRJ_META_PATH" - Path to Project Metadata

### Project Metadata File ###

The project metadata file allows for the user-specific creation of project lists to submit timesheet data for.  In this file, each project or time area (ex: vacation, corporate holiday, etc.) that the user may submit to TSS should be represented with its associated TSS metadata.

The metadata file is a simple text file where each line represents a project.  Each value on a given line is separated by a pipe (`|`) character.  The line has the following values in the following order: 

* Friendly Name (arbitrary, used at command line)
* Task ID
* Task Name
* Project ID
* Job ID
* Cat ID
* Job Type ID

Additionally, one of the listed Friendly Name entries may begin with an asterisk character (`*`).  This denotes that the line where present represents the "default" project (used when no project is provided as a command line argument).

An example metadata file with two projects (one "holiday" the other - the default - "foci"):

    *foci|51259|FOCI|1723|13486|2|242
    holiday|53515|Holiday|166|13457|92|156



[ntlm]: http://code.google.com/p/python-ntlm/



