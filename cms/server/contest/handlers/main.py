#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2014 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2015 Stefano Maggiolo <s.maggiolo@gmail.com>
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

"""Non-categorized handlers for CWS.

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import pickle

import tornado.web

from cms import config
from cms.db import Participation, PrintJob, User, Contest
from cms.server import actual_phase_required, filter_ascii
from cmscommon.datetime import make_datetime, make_timestamp

from datetime import date
from datetime import datetime

from .base import BaseHandler, check_ip, \
    NOTIFICATION_ERROR, NOTIFICATION_SUCCESS

from .secret_code import *
import urllib
import urllib2
from tornado import escape
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import uuid
from datetime import timedelta

logger = logging.getLogger(__name__)


class MainHandler(BaseHandler):
    """Home page handler.

    """
    def get(self):
        self.render("overview.html", **self.r_params)


from email.mime.nonmultipart import MIMENonMultipart
from email import charset
class MIMEUTF8QPText(MIMEText):
  def __init__(self, payload, content):
    MIMENonMultipart.__init__(self, 'text', content, charset='utf-8')
    utf8qp=charset.Charset('utf-8')
    utf8qp.body_encoding=charset.QP
    self.set_payload(payload, charset=utf8qp) 
#https://www.google.com/settings/security/lesssecureapps
def send_email(recipient, subject, body, htmlbody=None):
    to = recipient if type(recipient) is list else [recipient]
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = ", ".join(to)
    msg['To'] = recipient
    msg.attach(MIMEUTF8QPText(body.decode('quopri').decode('utf-8'), 'plain'))
    if htmlbody:
        msg.attach(MIMEUTF8QPText(htmlbody.decode('quopri').decode('utf-8'), 'html'))
    server = smtplib.SMTP("smtp.gmail.com", 587)    
    server.ehlo()
    server.starttls()
    server.login(secret_mail, secret_pwd)
    server.sendmail(secret_mail, to, msg.as_string())
    server.close()
    
def send_credentials(user):
    plain = """\
Hola, te creamos un usuario para que puedas enviar tus soluciones. Solo
debes entrar a:
omaforos.com.ar/oia

Tu credenciales son:
Usuario: USERNAME
Contrase=C3=B1a: PASSWORD

Cualquier error/problema que te surja no dudes en mandarnos un mail.

No olvidar los recursos online (apuntes, links, etc):
bit.ly/oiapoli

Saludos!
""".replace('USERNAME', user.username).replace('PASSWORD', user.password)
    html = """\
<div dir=3D"ltr">Hola, te creamos un usuario para que puedas enviar tus sol=
uciones. Solo debes entrar a:<div style=3D"text-align:center"><font size=3D=
"6"><a href=3D"http://omaforos.com.ar/oia" target=3D"_blank">omaforos.com.a=
r/oia</a></font></div><div style=3D"text-align:center"><br></div><div>Tu cr=
edenciales son:</div><div>Usuario: USERNAME</div><div>Contrase=C3=B1a:=C2=A0=
PASSWORD</div><div><br></div><div>Cualquier error/problema que te =
surja no dudes en mandarnos un mail.<br></div><div><br></div><div>No olvida=
r los recursos online (apuntes, links, etc):</div><div style=3D"text-align:=
center"><a href=3D"http://bit.ly/oiapoli" target=3D"_blank"><font size=3D"6=
">bit.ly/oiapoli</font></a></div><div><br></div><div>Saludos!</div><div><br=
></div></div>""".replace('USERNAME', user.username).replace('PASSWORD', user.password)
    send_email(user.email, "Juez Online OIA - Credenciales de acceso", plain, html)
    
def send_confirmation_code(user):
    link = "http://localhost:8888/register?user=3D" + user['username'] + '&code=3D' + user['activation_code']
    plain = """\
Para poder obtener tu usuario, por favor haz click en la siguiente
direcci=C3=B3n:

LINK
""".replace('LINK', link)
    html = """\
<div dir=3D"ltr">Para poder obtener tu usuario, por favor haz click en la s=
iguiente direcci=C3=B3n:<div><br><div><a href=3D"LINK=
">LINK</a></div></div></div>""".replace('LINK', link)
    send_email(user['email'], "Juez Online OIA - Activar usuario", plain, html)
    
class RegisterHandler(BaseHandler):
    """Register handler.

    """
    def get(self):
        fail_redirect = lambda msg : self.redirect("/register?register_error="+escape.url_escape(msg))
        if self.get_argument("user", "") != "" and self.get_argument("code", "") != "":
                user = self.sql_session.query(User)\
                    .filter(User.username == self.get_argument("user", ""))\
                    .first()
                if user is None:
                    fail_redirect("El link ya no es válido.")
                    return
                if user.activation_expire is None:
                    self.redirect("/?msg="+escape.url_escape("La cuenta ya está activada."))
                    return
                if user.activation_expire<datetime.now():
                    fail_redirect("El link ya expiró, por favor vuelva a llenar el formulario.")
                    return
                if self.get_argument("code", "") != user.activation_code:
                    fail_redirect("El link ingresado es inválido.")
                    return
                
                try:
                    # Create the participation.
                    contest = self.sql_session.query(Contest).get(1)
                    participation = Participation(contest=contest,
                                                  user=user,
                                                  hidden=False,
                                                  unrestricted=False)
                    self.sql_session.add(participation)
                    user.set_attrs({'activation_code':None, 'activation_expire':None})
                    self.sql_session.commit()
                    self.application.service.proxy_service.reinitialize()
                except:
                    fail_redirect("Error al activar usuario.")
                    return
                else:
                    send_credentials(user)
                    self.redirect("/?msg="+escape.url_escape("La cuenta ha sido activada exitosamente. Se envió un mail conteniendo tus credenciales."))
        else:
            self.render("register.html", **self.r_params)

    def post(self):
        fail_redirect = lambda msg : self.redirect("/register?register_error="+escape.url_escape(msg))

        attrs = dict()
        attrs['username'] = self.get_argument("username", "").strip()
        attrs['password'] = self.get_argument("password", "")
        attrs['first_name'] = self.get_argument("first_name", "").strip()
        attrs['last_name'] = self.get_argument("last_name", "").strip()
        attrs['email'] = self.get_argument("email", "").strip()
        attrs['province'] = self.get_argument("province", "").strip()
        attrs['city'] = self.get_argument("city", "").strip()
        attrs['school'] = self.get_argument("school", "").strip()
        attrs['birthdate'] = self.get_argument("birthdate", "")
        try:
            attrs['birthdate'] = datetime.strptime(attrs['birthdate'], '%Y-%m-%d')
            attrs['birthdate'] = datetime.combine(attrs['birthdate'], datetime.min.time())
        except Exception as err:
            fail_redirect('La fecha de nacimiento es invalida.')
            return
            
        if len(attrs['username'])<6:
            fail_redirect('El usuario tiene que tener al menos 6 caracteres.')
            return
        if len(attrs['password'])<6:
            fail_redirect('La clave tiene que tener al menos 6 caracteres.')
            return
        if not re.match(r"[A-Za-z0-9]*$", attrs['password']):
            fail_redirect('La clave sólo puede tener letras y números.')
            return
        if len(attrs['first_name'])<2:
            fail_redirect('El nombre tiene que tener al menos 2 caracteres.')
            return
        if len(attrs['last_name'])<2:
            fail_redirect('El apellido tiene que tener al menos 2 caracteres.')
            return
        if not re.match(r"([^@|\s]+@[^@]+\.[^@|\s]+)", attrs['email']):
            fail_redirect('Email invalido.')
            return
        if len(attrs['province'])<5:
            fail_redirect('La provincia tiene que tener al menos 5 caracteres.')
            return
        if len(attrs['city'])<5:
            fail_redirect('La ciudad tiene que tener al menos 5 caracteres.')
            return
        if len(attrs['school'])<6:
            fail_redirect('La escuela tiene que tener al menos 6 caracteres.')
            return      
                  
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {'secret' : secret_code,
                  'response' : self.get_argument("g-recaptcha-response", ""),
                  'remoteip' :  self.request.remote_ip }
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        captcha = json.load(response)['success']
        if not captcha:
            fail_redirect('Por favor, vuelva a verificar el captcha.')
            return
        
        try:    
            user = self.sql_session.query(User)\
                .filter(User.username == attrs['username'])\
                .first()
            if user is not None:
                fail_redirect('El nombre de usuario ya existe.')
                return
            user = self.sql_session.query(User)\
                .filter(User.email == attrs['email'])\
                .first()
            if user is not None:
                fail_redirect('El email ya esta asociado a una cuenta existente.')
                return
        except Exception as error:
            fail_redirect("Error verificando usuario.")
            return
                  
        code = uuid.uuid4().hex
        attrs['activation_code'] = code
        attrs['activation_expire'] = datetime.now() + timedelta(days=3)
        
        self.sql_session.query(User)\
                .filter(User.activation_expire < datetime.now())\
                .delete()
        try:
            # Create the user.
            user = User(**attrs)
            self.sql_session.add(user)
            self.sql_session.commit()
            send_confirmation_code(attrs)
        except Exception as error:
            fail_redirect("Error creando usuario.")
        else:
            # Create the user on RWS.
            self.application.service.proxy_service.reinitialize()
            self.redirect("/?msg="+escape.url_escape("Un correo electrónico fue enviado al email conteniendo el link para activar la cuenta."))
        
class LoginHandler(BaseHandler):
    """Login handler.

    """
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        next_page = self.get_argument("next", "/")
        user = self.sql_session.query(User)\
            .filter(User.username == username)\
            .first()
        participation = self.sql_session.query(Participation)\
            .filter(Participation.contest == self.contest)\
            .filter(Participation.user == user)\
            .first()

        if user is None:
            # TODO: notify the user that they don't exist
            self.redirect("/?login_error=true")
            return

        if participation is None:
            # TODO: notify the user that they're uninvited
            self.redirect("/?login_error=true")
            return

        # If a contest-specific password is defined, use that. If it's
        # not, use the user's main password.
        if participation.password is None:
            correct_password = user.password
        else:
            correct_password = participation.password

        filtered_user = filter_ascii(username)
        filtered_pass = filter_ascii(password)

        if password != correct_password:
            logger.info("Login error: user=%s pass=%s remote_ip=%s." %
                        (filtered_user, filtered_pass, self.request.remote_ip))
            self.redirect("/?login_error=true")
            return

        if self.contest.ip_restriction and participation.ip is not None \
                and not check_ip(self.request.remote_ip, participation.ip):
            logger.info("Unexpected IP: user=%s pass=%s remote_ip=%s.",
                        filtered_user, filtered_pass, self.request.remote_ip)
            self.redirect("/?login_error=true")
            return

        if participation.hidden and self.contest.block_hidden_participations:
            logger.info("Hidden user login attempt: "
                        "user=%s pass=%s remote_ip=%s.",
                        filtered_user, filtered_pass, self.request.remote_ip)
            self.redirect("/?login_error=true")
            return

        logger.info("User logged in: user=%s remote_ip=%s.",
                    filtered_user, self.request.remote_ip)
        self.set_secure_cookie("login",
                               pickle.dumps((user.username,
                                             correct_password,
                                             make_timestamp())),
                               expires_days=None)
        self.redirect(next_page)


class StartHandler(BaseHandler):
    """Start handler.

    Used by a user who wants to start his per_user_time.

    """
    @tornado.web.authenticated
    @actual_phase_required(-1)
    def post(self):
        participation = self.current_user

        logger.info("Starting now for user %s", participation.user.username)
        participation.starting_time = self.timestamp
        self.sql_session.commit()

        self.redirect("/")


class LogoutHandler(BaseHandler):
    """Logout handler.

    """
    def get(self):
        self.clear_cookie("login")
        self.redirect("/")


class NotificationsHandler(BaseHandler):
    """Displays notifications.

    """

    refresh_cookie = False

    @tornado.web.authenticated
    def get(self):
        if not self.current_user:
            raise tornado.web.HTTPError(403)

        participation = self.current_user

        res = []
        last_notification = make_datetime(
            float(self.get_argument("last_notification", "0")))

        # Announcements
        for announcement in self.contest.announcements:
            if announcement.timestamp > last_notification \
                    and announcement.timestamp < self.timestamp:
                res.append({"type": "announcement",
                            "timestamp":
                            make_timestamp(announcement.timestamp),
                            "subject": announcement.subject,
                            "text": announcement.text})

        # Private messages
        for message in participation.messages:
            if message.timestamp > last_notification \
                    and message.timestamp < self.timestamp:
                res.append({"type": "message",
                            "timestamp": make_timestamp(message.timestamp),
                            "subject": message.subject,
                            "text": message.text})

        # Answers to questions
        for question in participation.questions:
            if question.reply_timestamp is not None \
                    and question.reply_timestamp > last_notification \
                    and question.reply_timestamp < self.timestamp:
                subject = question.reply_subject
                text = question.reply_text
                if question.reply_subject is None:
                    subject = question.reply_text
                    text = ""
                elif question.reply_text is None:
                    text = ""
                res.append({"type": "question",
                            "timestamp":
                            make_timestamp(question.reply_timestamp),
                            "subject": subject,
                            "text": text})

        # Update the unread_count cookie before taking notifications
        # into account because we don't want to count them.
        prev_unread_count = self.get_secure_cookie("unread_count")
        next_unread_count = len(res) + (
            int(prev_unread_count) if prev_unread_count is not None else 0)
        self.set_secure_cookie("unread_count", "%d" % next_unread_count)

        # Simple notifications
        notifications = self.application.service.notifications
        username = participation.user.username
        if username in notifications:
            for notification in notifications[username]:
                res.append({"type": "notification",
                            "timestamp": make_timestamp(notification[0]),
                            "subject": notification[1],
                            "text": notification[2],
                            "level": notification[3]})
            del notifications[username]

        self.write(json.dumps(res))


class PrintingHandler(BaseHandler):
    """Serve the interface to print and handle submitted print jobs.

    """
    @tornado.web.authenticated
    @actual_phase_required(0)
    def get(self):
        participation = self.current_user

        if not self.r_params["printing_enabled"]:
            self.redirect("/")
            return

        printjobs = self.sql_session.query(PrintJob)\
            .filter(PrintJob.participation == participation)\
            .all()

        remaining_jobs = max(0, config.max_jobs_per_user - len(printjobs))

        self.render("printing.html",
                    printjobs=printjobs,
                    remaining_jobs=remaining_jobs,
                    max_pages=config.max_pages_per_job,
                    pdf_printing_allowed=config.pdf_printing_allowed,
                    **self.r_params)

    @tornado.web.authenticated
    @actual_phase_required(0)
    def post(self):
        participation = self.current_user

        if not self.r_params["printing_enabled"]:
            self.redirect("/")
            return

        printjobs = self.sql_session.query(PrintJob)\
            .filter(PrintJob.participation == participation)\
            .all()
        old_count = len(printjobs)
        if config.max_jobs_per_user <= old_count:
            self.application.service.add_notification(
                participation.user.username,
                self.timestamp,
                self._("Too many print jobs!"),
                self._("You have reached the maximum limit of "
                       "at most %d print jobs.") % config.max_jobs_per_user,
                NOTIFICATION_ERROR)
            self.redirect("/printing")
            return

        # Ensure that the user did not submit multiple files with the
        # same name and that the user sent exactly one file.
        if any(len(filename) != 1
               for filename in self.request.files.values()) \
                or set(self.request.files.keys()) != set(["file"]):
            self.application.service.add_notification(
                participation.user.username,
                self.timestamp,
                self._("Invalid format!"),
                self._("Please select the correct files."),
                NOTIFICATION_ERROR)
            self.redirect("/printing")
            return

        filename = self.request.files["file"][0]["filename"]
        data = self.request.files["file"][0]["body"]

        # Check if submitted file is small enough.
        if len(data) > config.max_print_length:
            self.application.service.add_notification(
                participation.user.username,
                self.timestamp,
                self._("File too big!"),
                self._("Each file must be at most %d bytes long.") %
                config.max_print_length,
                NOTIFICATION_ERROR)
            self.redirect("/printing")
            return

        # We now have to send the file to the destination...
        try:
            digest = self.application.service.file_cacher.put_file_content(
                data,
                "Print job sent by %s at %d." % (
                    participation.user.username,
                    make_timestamp(self.timestamp)))

        # In case of error, the server aborts
        except Exception as error:
            logger.error("Storage failed! %s", error)
            self.application.service.add_notification(
                participation.user.username,
                self.timestamp,
                self._("Print job storage failed!"),
                self._("Please try again."),
                NOTIFICATION_ERROR)
            self.redirect("/printing")
            return

        # The file is stored, ready to submit!
        logger.info("File stored for print job sent by %s",
                    participation.user.username)

        printjob = PrintJob(timestamp=self.timestamp,
                            participation=participation,
                            filename=filename,
                            digest=digest)

        self.sql_session.add(printjob)
        self.sql_session.commit()
        self.application.service.printing_service.new_printjob(
            printjob_id=printjob.id)
        self.application.service.add_notification(
            participation.user.username,
            self.timestamp,
            self._("Print job received"),
            self._("Your print job has been received."),
            NOTIFICATION_SUCCESS)
        self.redirect("/printing")


class DocumentationHandler(BaseHandler):
    """Displays the instruction (compilation lines, documentation,
    ...) of the contest.

    """
    @tornado.web.authenticated
    def get(self):
        self.render("documentation.html", **self.r_params)
