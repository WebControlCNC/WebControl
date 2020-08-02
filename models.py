#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created: 07/12/2020 Robert Lambert
# Modified:
#
# Model

import hashlib, binascii, os

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    accountlevel = Column(Integer, default=1)
    activated = Column(Integer, default=0)
    activity = Column(Integer, default=0)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            if property == "password":
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class User_activity(db.Model):
    __tablename__ = "User_activity"

    id = Column(Integer, primary_key=True)
    login_count = Column(Integer, default=0)
    un = Column(String, unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            setattr(self, property, value)

class Site_Users(db.Model):
    __tablename__ = "Site_Users"

    id = Column(Integer, primary_key=True)
    multiuser = Column(Integer, default=0)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            setattr(self, property, value)

def hash_pass(password):
    """
    Hash 
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash  # return bytes


def verify_pass(provided_password, stored_password):
    """
    Verify password
    """
    stored_password = stored_password.decode("ascii")
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")
    user = User.query.filter_by(username=username).first()
    return user if user else None
