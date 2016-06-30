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


Changes done
------------

- Added spanish translations.
- Users & problems name special codification (explained below)
- Scoreboard separated by levels.
- The score shown in the scoreboard is the max between all the submissions.
- cmsImportContest (italian format) modified to load users from csv file.
- Other minor changes like disabling Testing, hiding some texts, etc.
- Option to separate the problems in categories (visible for users only)
- Registration capabilities (using confirmation mail, to enable it you have to provide a gmail sender account and a google recaptcha secret code in cms/server/contest/handlers/secret_code.py, used by cms/server/contest/handlers/registration.py).


Usernames
------------
They have to be in the form:

[level]whatever

For example:

2pocharles

It's a username level 2.
Note: level can be 1, 2, 3, or x. x's users will see the problems for all levels.
If you don't use any of these letter, this user won't have a level. It won't appear on ranking.


Problem names
------------
They have to be in the form:

N[level]whatever

For example:

N3travellingsalesman


Scoreboard
------------
It is separated by ranking, and shows the school.


Log
------------

To help with the troubleshooting, you can collect the complete log
files that are placed in /var/local/log/cms/ (if CMS was running
installed) or in ./log (if it was running from the local copy).


