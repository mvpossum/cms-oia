Contest Management System (Modified for OIA)
=========================

Main project homepage: <http://cms-dev.github.io/>

Documentation: <https://cms.readthedocs.org/en/latest/>

[![Build Status](https://travis-ci.org/cms-dev/cms.svg?branch=master)](https://travis-ci.org/cms-dev/cms)
[![Join the chat at https://gitter.im/cms-dev/cms](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cms-dev/cms?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Introduction
------------

CMS, or Contest Management System, is a distributed system for running
and (to some extent) organizing a programming contest.

Forked from https://github.com/cms-dev/cms, see the link for main
explanation of the system.

This is a slightly modified version to suit the needs of the regional contest of the Argentinian Informatics Olympiads.
These contests have three different levels (according to age) each one with a different set of problems.

Installation and Usage
------------

Please use the Documentation provided in https://cms.readthedocs.org/en/latest/

Changes done
------------

- Added spanish translations.
- Registration capabilities (explained below).
- Users & problems separated by levels (explained below).
- Users in scoreboard are also separated by levels.
- cmsImportContest (italian format) modified to load users from csv file (see folder ejemplo for an example contest, load it with cmsImportContest ejemplo/ ).
- Option to separate the problems in categories (explained below)
- Other minor changes like disabling Testing, hiding some texts, etc.

Online registration
------------
You can set it up under contest properties from the admin interface (cmsAdminWebServer).
Once you get there you can activate and configure it:

- You need to provide your google recaptcha codes (https://www.google.com/recaptcha/)
- You need to provide the credentials for the gmail account used to send confirmation links. Don't use an account with critical information since the method is not secure. To be able to use the account you need to enable the access for less secure apps (https://www.google.com/settings/security/lesssecureapps)

Categories
------------
Every task can have a category. From the cmsAdminWebServer contest settings is possible to enable or disable categories.
When categories is enabled, the list of the problem shown to the contestants form a tree structure.
You can set the category of a tree under task properties on the cmsAdminWebServer. It's also loaded from the yaml file, setting the property 'category'.

Separate subcategories with dots. For example, if a task should be in the category Day 1, which is inside the category IOI 2013, then the category should be:
IOI 2013.Day 1

Levels
------------
Every user and task can have a level. From the cmsAdminWebServer contest settings is possible to restrict the visibility of tasks so that users can only see problems of their levels.
Level can be 1, 2, 3 or x. Users with level x can see all levels, tasks with level x can be seen by all levels.

User levels
------------
You can set the level under user properties on the cmsAdminWebServer. It's also loaded from the csv file during import.


Task levels
------------
You can set the level under task properties on the AdminWebServer. It's also loaded from the yaml file, setting the property 'level'.


Scoreboard
------------
It is separated by levels, and shows the school instead of the team. You can modify the school with admin interface (cmsAdminWebServer), under user properties or automatically load it from a csv when importing the contest. 


Log
------------

To help with the troubleshooting, you can collect the complete log
files that are placed in /var/local/log/cms/ (if CMS was running
installed) or in ./log (if it was running from the local copy).

