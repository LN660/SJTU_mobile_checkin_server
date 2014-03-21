import requests
import json

cookies=dict(uid="NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158")

def create_checkin():
	r = requests.post("http://128.199.202.41:8888/detectcreate", cookies=cookies )
	sessionid = ""
	try:
		sessionid = r.cookies['sessionid']
		print r.json(), sessionid
	except:
		print r.text

	cookies['sessionid']=sessionid

def upload_voice():
	files={
		"voice1": open("audio/1.wav", "rb"),
		"voice2": open("audio/2.wav", "rb"),
		"voice3": open("audio/3.wav", "rb"),
	}
	r = requests.post("http://128.199.202.41:8888/svtrain", cookies=cookies, files=files)
	try:
		print r.json()
	except:
		print r.text

def upload_picture():
	files={
		"pic": open("picture/img1.jpg", "rb"),
	}
	r = requests.post("http://128.199.202.41:8888/faceregister", cookies=cookies, files=files)
	print r.text

def verify_voice():
	files={
		"voice": open("audio/1.wav", "rb"),
	}
	r = requests.post("http://128.199.202.41:8888/svdetect", cookies=cookies, files=files)
	print r.text

def verify_picture():
	files={
		"pic": open("picture/img2.jpg", "rb"),
	}
	r = requests.post("http://128.199.202.41:8888/faceverify", cookies=cookies, files=files)
	print r.text

def upload_location():
	data = {
		"latitude":"31",
		"longitude": "121.4357",
	}
	r = requests.post("http://128.199.202.41:8888/uploadlocation", cookies=cookies, data=json.dumps(data))
	print r.text

def get_result():
	r = requests.get("http://128.199.202.41:8888/getdetectresult", cookies=cookies)
	print r.text


if __name__ == '__main__':
	create_checkin()
	upload_voice()
	upload_picture()
	verify_voice()
	verify_picture()
	upload_location()
	get_result()


'''
http  POST 128.199.202.41:8888/detectcreate "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158"

http -f POST 128.199.202.41:8888/svtrain "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158" voice1@1.wav voice2@2.wav voice3@3.wav

http -f POST 128.199.202.41:8888/svdetect "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158;sessionid=MQ==|1395289684|0aff8bdbac1ea9f6b538f2944421f08d95fd797e" voice@audio/1.wav

http -f POST 128.199.202.41:8888/faceregister "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158;sessionid=MQ==|1395289684|0aff8bdbac1ea9f6b538f2944421f08d95fd797e" pic@img.jpg

http -f POST 128.199.202.41:8888/faceverify "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158;sessionid=MQ==|1395289684|0aff8bdbac1ea9f6b538f2944421f08d95fd797e" pic@picture/img2.jpg

http POST 128.199.202.41:8888/uploadlocation "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158;sessionid=MQ==|1395289684|0aff8bdbac1ea9f6b538f2944421f08d95fd797e" latitude='31' longitude='121.4357'

http POST 128.199.202.41:8888/getdetectresult "cookie:uid=NTEwMDMwOTA0NA==|1395149423|f7ca9316a6c781a11e25e5be812d93676771d158;sessionid=MQ==|1395289684|0aff8bdbac1ea9f6b538f2944421f08d95fd797e"
'''