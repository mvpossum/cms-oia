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
These contests have three different levels(according to age) each one with a different set of problems.


Changes done
------------

- Added spanish translations.
- Users & problems name special codification
- Scoreboard separated by levels.
- Added a few util_scripts (probably you'll have to modify, so read them first)
- The score shown in the scoreboard is the max between all the submissions.
- cmsImporter modified to load users from csv file.
- Other dirty changes like disabling Testing, hiding some texts, etc.


Usernames
------------
They have to be in the form:

[level][twoletterschoolcode]whatever

For example:

2pocharles

It's a username level 2 from "po" school.
Note: level can be 1, 2, 3, or x. x's users will see the problems for all levels.
Not following this format will lead to undefined behavior.


Problem names
------------
They have to be in the form:

N[level]whatever

To help with the troubleshooting, you can collect the complete log
files that are placed in /var/local/log/cms/ (if CMS was running
installed) or in ./log (if it was running from the local copy).

N3travellingsalesman

Scoreboard
------------
It has three tabs for each level.




