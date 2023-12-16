# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 12:03:27 2021

@author: broyl
"""
######
#Searches for zipped foldes, unzips them
####

from tkinter import filedialog #for Python 3
import zipfile, os

#######Select working directory#############################################
topdir = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)

########Location for zipped files#######################################
fld_zip = '0_Zipped'
path_zip= os.path.abspath(os.path.join(topdir, fld_zip))


########Folder for unzipped files#######################################
fld_image = '1_Images'
path_images= os.path.abspath(os.path.join(topdir, fld_image))
# Creates the folder, and checks if it is created or not.
os.makedirs(path_images, exist_ok=True)

os.chdir(path_zip)

for file in os.listdir(path_zip):   # get the list of files
    
    if zipfile.is_zipfile(file): # if it is a zipfile, extract it
        #uses text before _psscene to make unzipped folder name
        zip_out=(os.path.basename(file).split("_psscene")[0])
        zip_location=os.sep.join([path_images, zip_out])
        #print(file)
        print(zip_out)
        if os.path.isfile(zip_location):
            print("File has already been unzipped")
        else:

            with zipfile.ZipFile(file) as item: # treat the file as a zip
                item.extractall(zip_location)  # extract it in the working directory
           
