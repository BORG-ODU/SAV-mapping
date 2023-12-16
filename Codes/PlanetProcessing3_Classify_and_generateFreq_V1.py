#March 1st 2022 - Victoria Hill (vhill@odu.edu)
#This code trains and classifies from the orginal image file, then does some post-prcoessing
#You will need 1. A text file with the names of all files to be processed
#2. Your training patches
#3. DEM file (if it is not in meters then be aware you will need to make changes to the code when you mask out deep water)
#   also be aware that in most DEM water is negative and land is positive
#YOU NEED TO DECIDE IF YOU WANT TO DO ALL THE POST PROCESSING STEPS OR NOT. IF NOT COMMENT THEM OUT
#IF YOU COMMENT OUT SOME OF THE PROCESSING STEPS, MAKE SURE THAT YOU ARE CALLING THE CORRECT FILENAME FOR THE NEXT STEP

###########UPDATES V2
#3/31/2022
#Combined step 1 get files into this code
#You now choose your working directory, DEM and training patches files through browse, instead of hard coding
#Makes a folder 2_Processed if it dones not already exist

###########UPDATES V2.01
#4/5/2022
#Code asks you to input depth for masking
#Code asks you what the ending of your filenames are


###########UPDATES V2.02
#7/25/2022  VJH
#adjusted so that training patches specific to each image will be used.
#post prcoessed commented out

###########UPDATES V2.03
#7/25/2022  VJH
#No DEM mask, as DEM is now part of the training data
#Running with one overall ROI shape file for all images

###########UPDATES V3_3
#1/19/2023  VJH
#added DEM mask back in after classification

###########UPDATES RENAME Train_Classify_and_Freq_V1
#2/9/2023  VJH
#Add code here to reclassify for SAV presence and pixels imaged. Later used in freq calculations
#Added code to run frequency after all classifications are done.




#############import packages#############
import arcpy
import arcpy
from arcpy import env
from arcpy.sa import *
import os
import pandas as pd
import numpy as np
from tkinter import filedialog #for Python 3
#########################################


#######get working directory##################
topdir = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)
##############################################
#######set input directory##################
fld_images = '2b_Composite_images'
path_images= os.path.abspath(os.path.join(topdir, fld_images))
#######set input directory##################

#######select files needed####################
#1. DEM
path_DEM=filedialog.askopenfilename(title='Select DEM',filetypes =[('tif', '*.tif')])
#2. shape files with training patches
path_shape=filedialog.askopenfilename(title='Select training files',filetypes =[('feature file', '*.shp')])
##############################################


#########CREATE FOLDERS####################################
fld_classified = '3a_Classified_composite'
path_classified = os.path.abspath(os.path.join(topdir, fld_classified)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_classified, exist_ok=True)
##############################################
fld_SAVpresence = '5a_SAV_presence'
path_SAVpresence = os.path.abspath(os.path.join(topdir, fld_SAVpresence)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_SAVpresence, exist_ok=True)
##############################################
fld_imaged = '5b_pixels_imaged'
path_imaged = os.path.abspath(os.path.join(topdir, fld_imaged)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_imaged, exist_ok=True)



########FIND IMAGES ENDING IN .TIF#################################################################

filename_ending = '.tif' 

#######Query 1_Images folder for files to process###
arcpy.env.workspace = path_images

searchdirectory = path_images
RGBN_files=[]  
#full directory and file name for all files
for root, dirs, files in os.walk(searchdirectory):
    for name in files:
        if name.endswith((filename_ending)):
            RGBN_files.append(os.path.abspath(os.path.join(root,name)))

file_count=len(RGBN_files)
if file_count == 0:
    print('I cant find any files')
    print('Please check you chose the right working directory')
else:
    print('I found '+str(len(RGBN_files))+' files to process')
    print('Starting - go get coffee:')
    print('***************************')


########STARTING CLASSIFICATION######################################################
#########
#start to count for loops
count=0
#############Starting processing loop####################################
for image in RGBN_files:
    ###start training###########################
    count=count+1
    print('Running loop ' + str(count) + ' of ' + str(file_count))
    ###construct output names###########################
    filename=(os.path.basename(image).split(".")[0])
    name=filename.partition("_composite")[0]
    ###shape file names for ROIs########
    shape_file=path_shape
    #shape_file=os.sep.join([directory_ROI,shape_file])
    ###classified file name########
    class_name=name+('_classified.tif')
    class_nameout= os.sep.join([path_classified, class_name])
    ####make output definition name
    def_file =name+('_definitionfile.ecd')
    def_file= os.sep.join([path_classified, def_file ])
    ##SAV presence filename###
    SAVpresencename=name+('_SAVpresence.tif')
    SAVpresencenameout= os.sep.join([path_SAVpresence, SAVpresencename])
    ##Pixels imaged filename###
    Imagedname=name+('_reclass_imaged.tif')
    Imagednameout= os.sep.join([path_imaged, Imagedname])
    ########Check to see if a file has already been processed
    print('Trying file:  '+filename+" _standby")


    if os.path.isfile(class_nameout):
        print("Classifed file already exisits - skipping to next file")
    elif os.path.isfile(shape_file):
        print("Shape file found")
        print('Training:  '+name)
#############SET TRAINING VARIABLES####################################      
        additional_raster = ''
        maxNumSamples = "500"
        #attributes = "COLOR;MEAN;STD;COUNT;COMPACTNESS;RECTANGULARITY"
        #Execute training
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/image-analyst/train-support-vector-machine-classifier.htm
        arcpy.ia.TrainSupportVectorMachineClassifier(image, shape_file, def_file,additional_raster, maxNumSamples)
        print('done')
        print('Classifying')
        # Execute classying
        classifiedraster = arcpy.ia.ClassifyRaster(image, def_file, additional_raster)
#############SAVE CLASSIFIED FILE IF YOU WANT OTHERWISE WAIT UNTIL THE NEXT STEP########################## 
        #classifiedraster.save(class_nameout)
        #print('classified file saved')

            
#############EXECUTE SETNULL FOR DEPTH, if DEM is equal to or less than -2 m (6.5 ft id 2 m). CHANGE THE DEPTH TO SUIT YOUR SITE
####if you want to mask out land using the DEM use the second line of code that includes the OR command
        classified_DEMmasked = SetNull(path_DEM, classifiedraster , "VALUE <= -2 Or VALUE > 0"); #use this line for just deep water
#############SAVE SETNULL CLASSIFIED FILE #########################        
        ##print(classDEMmask)
        #classDEMmaskname=name+('_setnullDEM.tif')
        #classDEMmasknameout= os.sep.join([path_classified, classDEMmaskname])
        classified_DEMmasked .save(class_nameout)
        print('Classified and DEM mask completed')

#############GET BAND OF 1ST BAND SO WE CAN SET OUTSIDE PIXELS TO NULL##########################  
##        #get band names and select name of band1
##        dsc = arcpy.Describe(image)
##        bands=[]
##        for band in dsc.children:
##            bands.append(band.name)
##        band1=bands[0]
##
##        #Execute SetNull in classification, if Rrs is equal to non-data.
##        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/set-null.htm
##        #This removes those empty pixels around the edge of the image.
##        inSegRasterband1= os.sep.join([image, band1])
##        #print(inSegRasterband1)
##        #whereclause=IsNull(inSegRasterband1)# looking for pixels in the orginial image that are null data, the output of this is a boolean, 1 or 0
##        #where (conditional raster, raster to change, condition)
##        classified_Rrsmask = SetNull(inSegRasterband1, classified_DEMmasked , "Value = 0") #sets these pixels (boolean =1)from above to null in our classified image.
##        #print(classRrsmask)
##        classRrsmaskname=name+('_classified.tif')
##        classRrsmasknameout= os.sep.join([path_outputs, classRrsmaskname])
##        classified_Rrsmask.save(classRrsmasknameout)
##        print('Classified and null pixel mask file saved')

#############DONT NEED THIS AS COMPOSITE CODE ALREADY DOES THIS########################         

        ##reclassify to not seagrass and seagrass
        #CHECK TO SEE WHAT VALUE YOUR SAV CLASS IS, THIS CLASS WILL BE RECLASSIFIED TO 1, ALL OTHERS EQUAL TO 0.
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/reclassify.htm
        SAVpresence=Reclassify(classified_DEMmasked, "Value", "0 1;1 0;2 0;3 0;4 0;5 0;6 0; 7 0;NODATA 0")
        SAVpresence.save(SAVpresencenameout)
        print('SAV presence file saved')


        #reclassify so all imaged pixels are = 1 allows you to calculate total number of times pixels are imaged.
        Imaged=Reclassify(classified_DEMmasked, "Value", "0 1;1 1;2 1;3 1;4 1;5 1;6 1;NODATA 0")
        Imaged.save(Imagednameout)
        print('Imaged file saved')
    else:
        print('No shapefile found, make one')

    print('**************************')

print("FINISHED Classifications - Starting frequency calculations")


#######################################################################################################
searchdirectory=path_SAVpresence
#Get all files in 5a_SAVpresence
listfiles_SAVpresence=[]
for root, dirs, files in os.walk(searchdirectory):
    for filename in files:
        if filename.endswith(('_SAVpresence.tif')):
            fullfile=os.path.abspath(os.path.join(path_SAVpresence,filename))
            listfiles_SAVpresence.append(fullfile)
        
needed_rasters_virtual = [arcpy.Raster(i) for i in listfiles_SAVpresence]
#print('Using the following images: ')
print(needed_rasters_virtual)

################MAKE THE NAME OF OUTPUT SAV presence total FILE
path_site=os.path.basename(topdir)
site_name=path_site+'_SAVpresence.tif'
SAV_out=os.sep.join([path_SAVpresence , site_name])

with arcpy.EnvManager(extent="MAXOF"):
    #filetype='EasternShore_SAVpresence_2022.tif'
    #SAVpresencename= os.sep.join([path_SAVpresence, filetype])
    outSAVpresence = CellStatistics(needed_rasters_virtual, "SUM", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
    outSAVpresence.save(SAV_out)#change this to save your frequency file
        
print('SAVpresence file saved')   


searchdirectory = path_imaged
#get just the filenames that end in shrink.tif, depending on what level of processing you did in step 2 this maybe different for you
listfiles_pixelsimaged=[]
for root, dirs, files in os.walk(searchdirectory):
    for filename in files:
        if filename.endswith(('reclass_imaged.tif')):
            fullfile=os.path.abspath(os.path.join(path_imaged,filename))
            listfiles_pixelsimaged.append(fullfile)
        
needed_rasters_virtual = [arcpy.Raster(i) for i in listfiles_pixelsimaged]
#print('Using the following images: ')
print(needed_rasters_virtual)

################MAKE THE NAME OF OUTPUT SAV presence total FILE
site_name=path_site+'_pixelsimaged.tif'
imaged_out=os.sep.join([path_imaged , site_name])

with arcpy.EnvManager(extent="MAXOF"):
    #filetype='EasternShore_pixelsimaged_2022.tif'
    #pixelsimagedname= os.sep.join([path_imaged, filetype])
    outpixelsimaged = CellStatistics(needed_rasters_virtual, "SUM", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
    outpixelsimaged.save(imaged_out)#change this to save your frequency file
        
print('pixelsimaged file saved')
print('calculating % SAV presence')


percentfilename=path_site+ '_percentSAV.tif'
percentfilename_location= os.sep.join([path_SAVpresence, percentfilename])

precentSAV=(Raster(outSAVpresence)/Raster(outpixelsimaged))*100
precentSAV.save(percentfilename_location)

    
