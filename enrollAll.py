import os
import glob

for filename in glob.iglob(os.path.join('faces', '*.jpg')):
	name = filename.split('/')
	names = name[1].split('_')
		
	firstName = names[0]
	lastName = names[1].split('.')[0]

	command = "python Enrollment.py localhost 9000 " + firstName + " " + lastName + " 0 faces/"+name[1]
	print command
	os.system(command)