Contest Management System (Modified for OIA)
=========================

Homepage: <http://cms-dev.github.io/>

Introduction
------------


Forked from https://github.com/cms-dev/cms, see the link for main
explanation of the system.

This is a slightly modified version to suit the needs of the regional
(and possibly national too) contest of the Argentinian Informatics Olympiads.
These contests have three different levels(according to age) each one with a different set of problems.


The changes are very dirty, so it's far away from something official.

Changes done
------------

- Added spanish translations.
- Users & problems name special codification
- Scoreboard separated by levels.
- Added a few util_scripts (probably you'll have to modify them, so read and understand before run)
- Other dirty changes like disabling Testing, hiding some texts, etc.


Usernames
------------
They have to be in the form:

[level][twoletterschoolcode]whatever

For example:

2pocharles

It's a username level 2 from "po" school.
The school will be automatically parsed as the user's team at the scoreboard.


Problem names
------------
They have to be in the form:

N[level]whatever

For example:

N3rmq

Scoreboard
------------
It has three tabs for each level.
In order to get school icons(team's flag) working you should try to follow the 'install_all' script.




