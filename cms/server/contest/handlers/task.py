#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2014 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2017 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2012-2014 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2013 Bernard Blackham <bernard@largestprime.net>
# Copyright © 2014 Artem Iglikov <artem.iglikov@gmail.com>
# Copyright © 2014 Fabian Gundlach <320pointsguy@gmail.com>
# Copyright © 2015 William Di Luigi <williamdiluigi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Task-related handlers for CWS.

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging

import tornado.web

from cms.server import actual_phase_required
from cmscommon.isocodes import is_language_code, translate_language_code, \
    is_country_code, translate_country_code, \
    is_language_country_code, translate_language_country_code
from cmscommon.mimetypes import get_type_for_file_name

from .base import BaseHandler, FileHandler


logger = logging.getLogger(__name__)


class TaskDescriptionHandler(BaseHandler):
    """Shows the data of a task in the contest.

    """
    @tornado.web.authenticated
    @actual_phase_required(0)
    def get(self, task_name):
        try:
            task = self.contest.get_task(task_name)
        except KeyError:
            raise tornado.web.HTTPError(404)
        if self.contest.restrict_level and self.current_user.user.level != task.level and self.current_user.user.level != "x" and task.level != "x":
            raise tornado.web.HTTPError(404)

        for statement in task.statements.itervalues():
            lang_code = statement.language
            if is_language_country_code(lang_code):
                statement.language_name = \
                    translate_language_country_code(lang_code, self.locale)
            elif is_language_code(lang_code):
                statement.language_name = \
                    translate_language_code(lang_code, self.locale)
            elif is_country_code(lang_code):
                statement.language_name = \
                    translate_country_code(lang_code, self.locale)
            else:
                statement.language_name = lang_code

        try:
            self.r_params["primary_statements"] = \
                json.loads(task.primary_statements)
        except ValueError as e:
            self.r_params["primary_statements"] = []
            logger.error("Primary statements for task %s is invalid [%r].",
                         task_name, e)

        try:
            self.r_params["user_primary"] = \
                json.loads(self.current_user.user.preferred_languages)
        except ValueError as e:
            self.r_params["user_primary"] = []
            logger.error("Preferred languages for user %s is invalid [%r].",
                         self.current_user.user.username, e)

        self.render("task_description.html", task=task, **self.r_params)


class TaskStatementViewHandler(FileHandler):
    """Shows the statement file of a task in the contest.

    """
    @tornado.web.authenticated
    @actual_phase_required(0)
    def get(self, task_name, lang_code):
        try:
            task = self.contest.get_task(task_name)
        except KeyError:
            raise tornado.web.HTTPError(404)
        if self.contest.restrict_level and self.current_user.user.level !=  task.level and self.current_user.user.level != "x" and task.level != "x":
            raise tornado.web.HTTPError(404)

        if lang_code not in task.statements:
            raise tornado.web.HTTPError(404)

        statement = task.statements[lang_code].digest
        self.sql_session.close()

        if lang_code != '':
            filename = "%s (%s).pdf" % (task.name, lang_code)
        else:
            filename = "%s.pdf" % task.name

        self.fetch(statement, "application/pdf", filename)


class TaskAttachmentViewHandler(FileHandler):
    """Shows an attachment file of a task in the contest.

    """
    @tornado.web.authenticated
    @actual_phase_required(0)
    def get(self, task_name, filename):
        try:
            task = self.contest.get_task(task_name)
        except KeyError:
            raise tornado.web.HTTPError(404)
        if self.contest.restrict_level and self.current_user.user.level !=  task.level and self.current_user.user.level != "x" and task.level != "x":
            raise tornado.web.HTTPError(404)

        if filename not in task.attachments:
            raise tornado.web.HTTPError(404)

        attachment = task.attachments[filename].digest
        self.sql_session.close()

        mimetype = get_type_for_file_name(filename)
        if mimetype is None:
            mimetype = 'application/octet-stream'

        self.fetch(attachment, mimetype, filename)
