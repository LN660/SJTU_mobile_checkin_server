# coding: utf8

'''
Settings of MobileCheckin Server
'''

import os
import base64

PORT = 8888

HOST = "128.199.202.41"

LOGGING_LEVEL = "debug"

API_KEY = "b3b9061aaf64ea2515a3538dfb624e94"
API_SECRET = "OfvW6DdyM9iqAa8TkBoBhoiWANX6Kn2Z"

SITE_ID = "jasignin20130507"

ROOT_DIR = os.path.dirname(__file__)

# MySQL database config
DB_USERNAME = "mobile_checkin"
DB_PASSWORD = "speechlab"

# Jaccount APP KEY Base64 encoded
JA_KEY = base64.decodestring("+Ln43/uRueAl7F3vTJuheWsV4IYT45TT")
