#coding: utf8

import re
import sys
import string
import random
import base64
import urllib2

import settings
from tornado.web import HTTPError
from pyDes import *

def find(s,regex):
	import re
	match = re.search(regex, s)
	if match:
		result = match.group()
	else:
		result = ""
	return result

def parse_data(data):
	a = data.split()
	c = {'type':'ProfileData'}
	try:
		for i in range(0,10):
			a[i] = a[i].split('=')
	except IndexError:
		pass
	for b in a:
		c[b[0]] = b[1]
	return c

def encrypt(data,iv):
	k = triple_des(settings.JA_KEY,CBC,iv,pad=None,padmode=PAD_PKCS5)
	d = k.encrypt(data)
	data = chr(8)+iv+d
	data = urllib2.quote(base64.b64encode(data))
	return data

def decrypt(data,iv):
	try:
		data = base64.b64decode(urllib2.unquote(data))
		data = data[1:]
		d = triple_des(settings.JA_KEY,CBC,iv,pad=None,padmode=PAD_PKCS5)
		k = d.decrypt(data)
	except TypeError,ValueError:
		raise HTTPError(404)
	return k
