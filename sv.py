# coding: utf8

from ctypes import cdll, c_int , c_char_p , c_double

# Speech Verify Engine initialize
sv_dll = cdll.LoadLibrary("./sv/libsv.so")
sv_dll.SVtrain.argtypes = [c_char_p , c_char_p , c_char_p , c_char_p , c_char_p]
sv_dll.SVdetect.argtypes = [c_char_p , c_char_p , c_char_p , c_double , c_int]
sv_dll.SVdetect.restype = c_double

def train(uid, file1, file2, file3):
	try:
		return sv_dll.SVtrain3("sv/sv.0.0.3.2.bin" , "data/audio_mod/%s.bin" % (uid) , file1 , file2 , file3)
	except:
		return -1

def detect(uid, tmp_path):
	try:
		return sv_dll.SVdetect("sv/sv.0.0.3.2.bin" , "data/audio_mod/%s.bin" % (uid) , tmp_path , 0.7 ,1)
	except:
		return -1
