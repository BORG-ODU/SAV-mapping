#March 1st 2022 - Victoria Hill (vhill@odu.edu)
#This code scans directory for files with the same date of collection and saves full directory and filename to text file
#Make sure to change "directory" to your folder
#Make sure the change "name.endswith" to the filenames you are looking for - whcih files are you trying mosiac? it should be the final product of step 3.
#   either shrink.tiff or clip.tiff
#Make sure to change the output text filename if wanted.
#This code looks for images taken on the same day and puts filenames in a txt file for each individual date

#11/19/2022 vhill@odu.edu
#Alter code so that if there is only one tile per day per sensor that image just gets copied
#to the next folder. also is renamed as YYYMMDD_xxxx_mosaic.tif even if it's not an actual mosaic
#If content_list is greater than 1, then the images get mosacied.


#02/09/2023
#Combined get files names and moasaic into one step.


#02/10/2023
#Combine mosaic, clip and composite into one step
#Asks whether clipping is wanted
#Still need to add a check to see if a mosaic file already exists, if it does skip processing and move to clip and composite.

#20/11/2023
#Correct mistake, have clipping section of code look for the composite file before clipping, so it can skip if it exists


#######import packages#################################################
import os
import numpy as np
import arcpy
from arcpy import env
from arcpy.sa import *
from tkinter import filedialog #for Python 3
import shutil

#######Select working directory#############################################
topdir = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)
#######################################################################
print('*********************************')
#######Set and create other working folders###############################
########Folder for orginial images#######################################
fld_org = '1_Images'
dir_images= os.path.abspath(os.path.join(topdir, fld_org))
print('Your image directory is: '+dir_images)
print('*********************************')
############Folder for mosaic images####################################
fld_mosaic = '2a_Mosaic'
path_mosaic = os.path.abspath(os.path.join(topdir, fld_mosaic))
# Creates the folder, and checks if it is created or not.
os.makedirs(path_mosaic, exist_ok=True)
############Folder for composite images##################################
fld_temp = 'TEMP'
path_temp = os.path.abspath(os.path.join(topdir, fld_temp)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_temp , exist_ok=True)
#############Folder for composite images#################################
fld_composite = '2b_Composite_images'
path_comp = os.path.abspath(os.path.join(topdir, fld_composite)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_comp, exist_ok=True)
############################################################################


#######select files needed##################################################
#1. DEM
path_DEM=filedialog.askopenfilename(title='Select DEM',filetypes =[('tif', '*.tif')])

#######################################################################################

######################################################################################
################################################################################################
#######Clip files###Clip files#####Clip files##################################################
################################################################################################

#############Search in mosaic folder#######################################################
input_files=[] 
for root, dirs, files in os.walk(path_mosaic):
    for name in files:
        if name.endswith(("mosaic.tif")):
            fullpath=os.path.abspath(os.path.join(root,name))
            input_files.append(fullpath)

file_count=len(input_files)
##if file_count == 0:
##    print('I cant find any files')
##    print('Please check you chose the right working directory')
##else:
##    print('I found '+str(len(input_files))+' files to process')
##    print('Starting - processing:')
##    print('***************************')

###################################################################################################
clip_choice = str(input("Do you want to clip the mosaic images; enter yes to clip, no to skip: "))
if clip_choice == 'yes':
    print('Ok, clipping images')
    print('*********************************')
    print('Starting clipping')
    print('*********************************')
#2. Clip shapefile - if you want to clip your files
    path_clip=filedialog.askopenfilename(title='Select clip file',filetypes =[('shp', '*.shp')])
#start to count for loops
    count=0
#############Starting processing loop - output progress#####################################################
    for image in input_files:
        count=count+1
        print('Running loop ' + str(count) + ' of ' + str(file_count))
#############get the image filename and output to command line for progress###################
        rastername=(os.path.basename(image).split(".")[0])
        rastername=rastername.partition("_mosaic")[0]
        
            

################################################################################################
#######Clip and composite files####################################
################################################################################################
########Check to see if a file has already been processed#######################################
        compositename=rastername+('_composite.tif')
        compositenameout= os.sep.join([path_comp, compositename])
        raster_clipname=rastername+('_clip.tif')
        raster_clipnameout= os.sep.join([path_temp, raster_clipname])
########Make a new raster composite with color bands and DEM############################################
########This first file will go the temp folder and will be deleted######################################
        if os.path.isfile(compositenameout):
            print("File:"+rastername+ "already exisits - skipping to next file")
        else:
            print('Processing file: '+rastername+ ' :for clipping and compositing')
#######################Execute ExtractByMask#################################################
            raster_clip = ExtractByMask(image,path_clip,"INSIDE")
            raster_clip.save(raster_clipnameout)
            print('Clipping completed on: '+rastername)
 #######################MAKE A TEMP FILE TO PUT INITAL COMPOSITIE FILE#################################################               
            temp_nameout= os.sep.join([path_temp , compositename])
            arcpy.CompositeBands_management(raster_clipnameout+';'+path_DEM, temp_nameout)
            
            
#########Use IsNull to find pixels in temp file where all bands are equal to 0    
            mask = SetNull(temp_nameout, temp_nameout, "VALUE = 65535 OR VALUE =0") #sets these pixels (boolean =1)from above to null 
            mask.save(compositenameout)
            print('File: '+rastername+ 'composited.tif  :composited and saved')        
            print('**************************')
            
########delete file that we saved to temp folder#############################################################
            os.remove(temp_nameout)

            
################################################################################################
#######Composite files###Composite files#####Composite files####################################
################################################################################################
else:
    print('Ok, going straight to composite')
    #start to count for loops
    count=0
#############Starting processing loop - output progress#####################################################
    for image in input_files:
        count=count+1
        print('Running loop ' + str(count) + ' of ' + str(file_count))

#############get the image filename and output to command line for progress###################
        rastername=(os.path.basename(image).split(".")[0])
        rastername=rastername.partition("_mosaic")[0]
        print('Processing file: '+rastername+ ' :for compositing')
########Check to see if a file has already been processed#######################################
        compositename=rastername+('_composite.tif')
        compositenameout= os.sep.join([path_comp, compositename])
########Make a new raster composite with color bands and DEM############################################
########This first file will go the temp folder and will be deleted######################################
        if os.path.isfile(compositenameout):
            print("This file already exisits - skipping to next file")
        else:
            #print("Processing")
            temp_nameout= os.sep.join([path_temp , compositename])
            arcpy.CompositeBands_management(image+';'+path_DEM, temp_nameout)
            #print('Composite Saved')
            
#########Use IsNull to find pixels in temp file where all bands are equal to 0    
            mask = SetNull(temp_nameout, temp_nameout, "VALUE = 65535 OR VALUE =0") #sets these pixels (boolean =1)from above to null 
            mask.save(compositenameout)
            print('File: '+rastername+ ' composited.tif  :composited and saved')        
            print('**************************')
            
########delete file that we saved to temp folder#############################################################
            os.remove(temp_nameout)

print("FINISHED")
