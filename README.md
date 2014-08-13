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
- Added a few util_scripts (probably you'll have to modify them, so read first)
- The score shown in the scoreboard is the max between all the submissions.
- Other dirty changes like disabling Testing, hiding some texts, etc.


Usernames
------------
They have to be in the form:

[level][twoletterschoolcode]whatever

For example:

2pocharles

It's a username level 2 from "po" school.
The school code will be automatically parsed as the user's team at the scoreboard.
Note: level can be 1, 2, 3, or x. x's users will see the problems for all levels.
Not following this format will lead to undefined behavior.


Problem names
------------
They have to be in the form:

N[level]whatever

For example:

N3travellingsalesman

Scoreboard
------------
It has three tabs for each level.
In order to get school icons(team's flag) working you should try to follow the 'install_all' script.




