#!/usr/bin/env python3
from requests import Session

verbose = False

auth_head = {}

se = Session()
log_file = None

clogin_info = {
    'd2l_referrer': '',
    'target': '/d2l/home',
    'loginPath': '/d2l/login',
    'userName': '',
    'password': '',
    }
