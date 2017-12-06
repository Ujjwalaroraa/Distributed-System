import os
import os.path

def find_file(filename):
	print("the file we are looking for is ", filename)

	if filename in  os.listdir("DBM_File/"):
		print("file exists on db")
		file_path= "DBM_file/" + filename
		return file_path
	else:
		print("file does not exist on db. creating file")
		file_path= "DBM_file/" + filename
		f=open(file_path,"w+")
		f.close()
		return file_path
