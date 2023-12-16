#March 1st 2022 - Victoria Hill (vhill@odu.edu)
#This code trains and classifies from the orginal image file
##############################################################
#USING INDIVIDIUAL TRAINING PATCH FILES FOR EACH IMAGE
##############################################################
#You will need 
#1. Your training patches
#2. DEM file (if it is not in meters then be aware you will need to make changes to the code when you mask out deep water)
#   also be aware that in most DEM water is negative and land is positive

###########UPDATES V1_1
#11/18/2023 VJH
#Using new master schema where SAV has subclasses
#Aquatic veg = 10, emergent = 11, submerged = 12, deeper = 13
#All other classes are 20 and greater


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
arcpy.env.overwriteOutput = True

#######get working directory##################
topdir = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)
##############################################
#######set input directory##################
fld_images = '2b_Composite_images'
path_images= os.path.abspath(os.path.join(topdir, fld_images))


#######select files needed####################
#1. DEM
path_DEM=filedialog.askopenfilename(title='Select DEM',filetypes =[('tif', '*.tif')])
#2. shape files with training patches
#path_shape=filedialog.askopenfilename(title='Select training files',filetypes =[('feature file', '*.shp')])
##############################################

#######Query the presence folder for output###
# Joins the folder that we wanted to create
fld_classified = '3a_Classified'
path_outputs = os.path.abspath(os.path.join(topdir, fld_classified )) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_outputs, exist_ok=True)
##############################################
# Joins the folder that we wanted to create
fld_ROI = '6_ROIs'
path_ROI = os.path.abspath(os.path.join(topdir, fld_ROI )) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_outputs, exist_ok=True)
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
##############################################
fld_freq = '5c_SAV_frequency'
path_freq = os.path.abspath(os.path.join(topdir, fld_freq)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_freq, exist_ok=True)




# Text to identify image filenames:
#filename_ending = str(input("How do your image filenames end? SR.tif or SR_clip.tif? Please type reponse: "))
filename_ending = '.tif' 
print('Searching for filenames ending in : ',filename_ending) 
#######Query 1_Images folder for files to process###



arcpy.env.workspace = topdir

searchdirectory = path_images
RGBN_files=[]  
#full directory and file name for all files
for root, dirs, files in os.walk(searchdirectory):
    for name in files:
        if name.endswith((filename_ending)):
            RGBN_files.append(os.path.abspath(os.path.join(root,name)))

file_count=len(RGBN_files)
if file_count == 0:
    print('I cant find any files, did you give me the right text string to search for?')
    print('Please check you chose the right working directory')
else:
    print('I found '+str(len(RGBN_files))+' files to process')
    print('Starting - go get coffee:')
    print('***************************')



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
    shape_file=name+'.shp'
    shape_file=os.sep.join([path_ROI,shape_file])
    ###classified file name########
    class_name=name+('_classified.tif')
    class_nameout= os.sep.join([path_outputs, class_name])
    ####make output definition name
    def_file =name+('_definitionfile.ecd')
    def_file= os.sep.join([path_outputs, def_file ])
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
        
#############REMAP THE UNIQUE PIXEL VALUE GIVEN TO THE RASTER CELLS BACK INTO THE ORIGINAL CLASSVALUE######################### 
        
        # Get the unique class values assigned by the SVM classifier
        # Convert the classified raster to a NumPy array
        classified_array = arcpy.RasterToNumPyArray(classifiedraster)

        # Get unique values from the NumPy array
        unique_numbers = np.unique(classified_array)
        # Retrieve the original class labels from the training samples
        org_labels = set(row[0] for row in arcpy.da.SearchCursor(shape_file, "Classvalue"))
        # Sort the original class labels in ascending order
        srt_org_labels = sorted(set(org_labels))
        # Ensure both lists have the same length, in a few images there seems to be an extra unique numbers, pixels that don't fit into a class maybe
        min_length = min(len(unique_numbers), len(srt_org_labels))
        unique_numbers = unique_numbers[:min_length]
        srt_org_labels = srt_org_labels[:min_length]
        # Create a dynamic mapping between unique numbers and original class values
        mapping = {num: srt_org_labels[i] for i, num in enumerate(unique_numbers)}
        # Create a remap range based on the dynamic mapping
        #remap_ranges = RemapValue([[num, mapping[num]] for num in unique_nums])
        # Remap the classified raster to original class values
        #remapped_raster = Reclassify(classifiedraster, "VALUE", remap_ranges)

        # Create a conditional remap range to handle values not explicitly mapped
        conditional_remap = RemapValue([[num, mapping.get(num, "NODATA")] for num in unique_numbers])

        # Remap the classified raster to original class values
        remapped_raster = Reclassify(classifiedraster, "VALUE", conditional_remap)
        print('Remapped file saved')


             
#############EXECUTE SETNULL FOR DEPTH, if DEM is equal to or less than -2 m (6.5 ft id 2 m). CHANGE THE DEPTH TO SUIT YOUR SITE
        classified_DEMmasked = SetNull(path_DEM, remapped_raster , "VALUE <= -2 Or VALUE > 0"); #use this line for just deep water
#############SAVE SETNULL CLASSIFIED FILE #########################          
        ##print(classDEMmask)
        #classDEMmaskname=filename+('_setnullDEM.tif')
        #classDEMmasknameout= os.sep.join([savepath_output, classDEMmaskname])
        classified_DEMmasked .save(class_nameout)
        print('Classified and DEM mask completed')

########RECLASSIFY SO THAT aquatic vegetation equals 1 AND ALL OTHERS = 0
 
        #CHECK TO SEE WHAT VALUE YOUR SAV CLASS IS, THIS CLASS WILL BE RECLASSIFIED TO 1, ALL OTHERS EQUAL TO 0.
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/reclassify.htm
        reclass_ranges1 = RemapRange([[10, 19, 1], [20, 100, 0],["NODATA","NODATA", 0]])
        #SAVpresence=Reclassify(classified_DEMmasked, "Value", "0 1;1 0;2 0;3 0;4 0;5 0;6 0;7 0;NODATA 0")
        SAVpresence=Reclassify(classified_DEMmasked, "Value", reclass_ranges1)
        SAVpresence.save(SAVpresencenameout)
        print('SAV presence file saved')


########RECLASSIFY so all imaged pixels are = 1 allows you to calculate total number of times pixels are imaged.

        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/reclassify.htm
        reclass_ranges2 = RemapRange([[10, 19, 1], [20, 100, 1],["NODATA","NODATA", 0]])
        Imaged=Reclassify(classified_DEMmasked, "Value", reclass_ranges2)
        #Imaged=Reclassify(classified_DEMmasked, "Value", "0 1;1 1;2 1;3 1;4 1;5 1;6 1;7 1;NODATA 0")
        Imaged.save(Imagednameout)
        print('Imaged file saved')
    else:
        print('No shapefile found, make one')

    print('**************************')

print("FINISHED Classifications - Starting frequency calculations")



#######################################################################################################
####Frequency processing of presence/absence
#######################################################################################################


#################Setting so that the frequency files can be overwritten################################
arcpy.env.overwriteOutput = True
#####################################################################################################

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
SAV_out=os.sep.join([path_freq , site_name])

with arcpy.EnvManager(extent="MAXOF"):
    outSAVpresence = CellStatistics(needed_rasters_virtual, "SUM", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
    outSAVpresence.save(SAV_out)
        
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
percentfilename_location= os.sep.join([path_freq, percentfilename])

precentSAV=(Raster(outSAVpresence)/Raster(outpixelsimaged))*100
precentSAV.save(percentfilename_location)

    
