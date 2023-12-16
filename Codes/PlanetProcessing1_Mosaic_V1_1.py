#March 1st 2022 - Victoria Hill (vhill@odu.edu)
#This code looks for images taken on the same day and puts filenames in a txt file for each individual date
#If you did not order harmonzied and clipped data, then you will need to change the file ending name so it searches for the right files

#11/19/2022 vhill@odu.edu
#Alter code so that if there is only one tile per day per sensor that image just gets copied
#to the next folder. also is renamed as YYYMMDD_xxxx_mosaic.tif even if it's not an actual mosaic
#If content_list is greater than 1, then the images get mosacied.


#02/09/2023 - Mosaic_V1
#Combined get files names and moasaic into one step.
#Yippee finally

#7/26/2023 Mosaic_V1_1
#changed numberofbands variable to a user input
#changed code so that it looks for .tif filenames and then disregards files with udm2 in the name.
#this means that you don't need to change the code to whatever filename ending your images have. Reduces the chances of errors.

#############import packages#############
import os
import pandas as pd
import numpy as np
from tkinter import filedialog #for Python 3
import shutil
import arcpy
from arcpy import env
from arcpy.sa import *
#########################################

print('You are using PlanetProcessing1_Mosaic_V1_1 updated on 7/26/2023')
print('If you have questions email Victoria Hill at vhill@odu.edu')


         

#######get working directory##################
topdir = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)
##############################################
#######set image and classified images directory##################
fld_images = '1_Images'
path_images= os.path.abspath(os.path.join(topdir, fld_images))
print('Your image directory is: '+path_images)
############Folder for mosaic txt lists####################################
fld_mosaictext = '1b_MosaicTxtFiles'
path_txtfiles= os.path.abspath(os.path.join(path_images, fld_mosaictext))
# Creates the folder, and checks if it is created or not.
os.makedirs(path_txtfiles, exist_ok=True)
############Folder for mosaic images####################################
fld_mosaic = '2a_Mosaic'
path_mosaic = os.path.abspath(os.path.join(topdir, fld_mosaic))
# Creates the folder, and checks if it is created or not.
os.makedirs(path_mosaic, exist_ok=True)

###enter number of bands in your data
numberofbands = int(input("How many bands does your data have 4 or 8 (just type in the number and hit enter: "))



files = []
arr=[]

#get the filenames that end in .tif
processed=[]
for root, dirs, files in os.walk(path_images):
    for name in files:
        if name.endswith((".tif")):
            fullpath=os.path.abspath(os.path.join(root,name))
            processed.append(fullpath)

#filenames that end in .tif includes the masking file, which you do not want to process, so we need to get rid of filenames with udm2 in the filename
processed[:] = [x for x in processed if "udm2" not in x]
#print(processed)

#get just the date from the filenames
firstCharList = []
for name in processed:
    name_only=(os.path.basename(name).split(".")[0])
    firstCharList.append(name_only[0:8])
#print(firstCharList)

sensorIDList=[]
for name in processed:
    sensor=name.partition("_3B")[0][-4:]
    sensorIDList.append(sensor)
#print(sensorIDList)

#remove duplicates
firstCharList = list( dict.fromkeys(firstCharList) )
sensorIDList = list( dict.fromkeys(sensorIDList) )
#print(firstCharList)
#print(sensorIDList)

#now step through date list, if filename has that date then add to a text file and name that text file
#this gives you a text file with the names of the files that are from the same day
for date in firstCharList:
    for sensor in sensorIDList:
        mylist=[]
        for file in processed:
            #print(file)
            if date in file and sensor in file:
                #print(file)
                #fullfile=os.path.abspath(os.path.join(dirs,file))
                mylist.append(file)
                #print(mylist)
                outputfile=os.sep.join([path_txtfiles,date+('_')+sensor+('_tobemosaic.txt')])
                np.savetxt(outputfile,mylist,delimiter="\n", fmt="%s")


arr2=[]  
#full directory and file name for all _tobemosaic.text files
for root, dirs, files in os.walk(path_txtfiles):
    for name in files:
        if name.endswith(("_tobemosaic.txt")):
            arr2.append(os.path.join(root,name))
            mastername='master_mosaic_list.txt'
            masternameoutput=os.sep.join([path_txtfiles, mastername])
            np.savetxt(masternameoutput,arr2,delimiter="\n", fmt="%s")


with open(masternameoutput) as e:
#open a listof filenames
    master_list=e.readlines()
    #print(master_list)
# remove new line characters
master_list = [x.strip() for x in master_list]
#print(master_list)

#now start a for loop
for names in master_list:
    #print('running file',names)
    file_to_open=names
    filename=(os.path.basename(names).split(".")[0])
    date=filename[0:8]
    sensor=filename.partition("_tobe")[0][-4:]
    outsensor='_'+sensor
    newfilename=date+'_'+sensor+'_mosaic.tif'
    newfilelocation=os.sep.join([path_mosaic, newfilename])
    
    with open(file_to_open) as f:
        content_list = f.readlines()
        numberfiles=len(content_list)
        if numberfiles == 1:
            print('There is only one tile for  '+date+' and '+sensor+' this pass, no mosaic needed, file copied and renamed')
            ########Check to see if a file has already been processed#######################################
            if os.path.isfile(newfilelocation):
                print("This file already exisits - skipping to next file")
            else:
                for source in content_list:
                    source_name = source.strip()
                    shutil.copy(source_name, newfilelocation)
        else:    
            print('There is more than one tile for '+date+' and '+sensor+'  this pass, mosaic needed')
            if os.path.isfile(newfilelocation):
                print("This file already exisits - skipping to next file")
            else:
                needed_rasters_virtual = [arcpy.Raster(i) for i in content_list]
                #print(needed_rasters_virtual)
                #MosaicToNewRaster
                arcpy.MosaicToNewRaster_management (needed_rasters_virtual, path_mosaic, newfilename, None,"16_BIT_UNSIGNED", None,numberofbands, "BLEND", "FIRST")
                print('File'+newfilename+'  mosaiced')
            
                
