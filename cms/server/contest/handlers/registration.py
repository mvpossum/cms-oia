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

"""Registration handler for CWS.

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging

import tornado.web

from cms.db import Participation, User, Contest

from datetime import date
from datetime import datetime

from .base import BaseHandler

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

from email.mime.nonmultipart import MIMENonMultipart
from email import charset

class MIMEUTF8QPText(MIMEText):
  def __init__(self, payload, content):
    MIMENonMultipart.__init__(self, 'text', content, charset='utf-8')
    utf8qp=charset.Charset('utf-8')
    utf8qp.body_encoding=charset.QP
    self.set_payload(payload, charset=utf8qp) 
#https://www.google.com/settings/security/lesssecureapps
def send_email(gmailuser, password, recipient, subject, body, htmlbody=None):
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
    server.login(gmailuser, password)
    server.sendmail(gmailuser, to, msg.as_string())
    server.close()
    
def send_credentials(gmailuser, password, user, host):
    plain = """\
Hola, te creamos un usuario para que puedas enviar tus soluciones. Solo
debes entrar a:
HOST

Tu credenciales son:
Usuario: USERNAME
Contrase=C3=B1a: PASSWORD

Cualquier error/problema que te surja no dudes en mandarnos un mail.

No olvidar los recursos online (apuntes, links, etc):
bit.ly/oiapoli

Saludos!
""".replace('USERNAME', user.username).replace('PASSWORD', user.password).replace('HOST', host)
    html = """\
<div dir=3D"ltr">Hola, te creamos un usuario para que puedas enviar tus sol=
uciones. Solo debes entrar a:<div style=3D"text-align:center"><font size=3D=
"6"><a href=3D"http://HOST" target=3D"_blank">HOST=
</a></font></div><div style=3D"text-align:center"><br></div><div>Tu cr=
edenciales son:</div><div>Usuario: USERNAME</div><div>Contrase=C3=B1a:=C2=A0=
PASSWORD</div><div><br></div><div>Cualquier error/problema que te =
surja no dudes en mandarnos un mail.<br></div><div><br></div><div>No olvida=
r los recursos online (apuntes, links, etc):</div><div style=3D"text-align:=
center"><a href=3D"http://bit.ly/oiapoli" target=3D"_blank"><font size=3D"6=
">bit.ly/oiapoli</font></a></div><div><br></div><div>Saludos!</div><div><br=
></div></div>""".replace('USERNAME', user.username).replace('PASSWORD', user.password).replace('HOST', host)
    send_email(gmailuser, password, user.email, "Juez Online OIA - Credenciales de acceso", plain, html)
    
def send_confirmation_code(gmailuser, password, user, host):
    link = "http://"+host+"/register?user=3D" + user['username'] + '&code=3D' + user['activation_code']
    plain = """\
Para poder obtener tu usuario, por favor haz click en la siguiente
direcci=C3=B3n:

LINK
""".replace('LINK', link)
    html = """\
<div dir=3D"ltr">Para poder obtener tu usuario, por favor haz click en la s=
iguiente direcci=C3=B3n:<div><br><div><a href=3D"LINK=
">LINK</a></div></div></div>""".replace('LINK', link)
    send_email(gmailuser, password, user['email'], "Juez Online OIA - Activar usuario", plain, html)
    
class RegisterHandler(BaseHandler):
    """Register handler.

    """
    def get(self):
        if not self.contest.online_registration:
            raise tornado.web.HTTPError(404)
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
                    participation = Participation(contest=self.contest,
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
                    send_credentials(self.contest.gmail_sender, self.contest.gmail_password, user, self.request.host)
                    self.redirect("/?msg="+escape.url_escape("La cuenta ha sido activada exitosamente. Se envió un mail conteniendo tus credenciales."))
        else:
            self.render("register.html", **self.r_params)

    def post(self):
        if not self.contest.online_registration:
            raise tornado.web.HTTPError(404)
        fail_redirect = lambda msg : self.redirect("/register?register_error="+escape.url_escape(msg))

        attrs = dict()
        attrs['password'] = self.get_argument("password", "")
        attrs['first_name'] = self.get_argument("first_name", "").strip()
        attrs['last_name'] = self.get_argument("last_name", "").strip()
        attrs['email'] = self.get_argument("email", "").strip()
        attrs['city'] = self.get_argument("city", "").strip()
        attrs['school'] = self.get_argument("school", "").strip()
        attrs['username'] = self.get_argument("email", "").strip()
        
        if len(attrs['username'])<3:
            fail_redirect('El usuario tiene que tener al menos 3 caracteres.')
            return
        if len(attrs['password'])<3:
            fail_redirect('La clave tiene que tener al menos 3 caracteres.')
            return
        if not re.match(r"[A-Za-z0-9]*$", attrs['password']):
            fail_redirect('La clave sólo puede tener letras y números.')
            return
        if len(attrs['first_name'])<3:
            fail_redirect('El nombre tiene que tener al menos 3 caracteres.')
            return
        if len(attrs['last_name'])<3:
            fail_redirect('El apellido tiene que tener al menos 3 caracteres.')
            return
        if not re.match(r"([^@|\s]+@[^@]+\.[^@|\s]+)", attrs['email']):
            fail_redirect('Email invalido.')
            return
        if len(attrs['city'])<3:
            fail_redirect('La ciudad tiene que tener al menos 3 caracteres.')
            return
        if len(attrs['school'])<3:
            fail_redirect('La escuela tiene que tener al menos 3 caracteres.')
            return      
                  
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {'secret' : self.contest.captcha_server_code,
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
            send_confirmation_code(self.contest.gmail_sender, self.contest.gmail_password, attrs, self.request.host)
        except Exception as error:
            fail_redirect("Error creando usuario.")
        else:
            # Create the user on RWS.
            self.application.service.proxy_service.reinitialize()
            self.redirect("/?msg="+escape.url_escape("Un correo electrónico fue enviado al email conteniendo el link para activar la cuenta."))
