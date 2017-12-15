import os
import os.path

def ffile(fname):
	print("the file i am looking for is ", fname)

	if fname in  os.listdir("DBM_File/"):
		print("file is  existing on db")
		fpath= "DBM_file/" + fname
		return fpath
	else:
		print("file is not existing on db. creating file")
		fpath= "DBM_file/" + fname
		f=open(fpath,"w+")
		f.close()
		return fpath
