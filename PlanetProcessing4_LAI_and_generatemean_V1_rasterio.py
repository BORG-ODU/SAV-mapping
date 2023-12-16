# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 18:25:42 2023

@author: vhill
"""

#import libraries
# import numpy as np
# import pandas as pd
# import matplotlib as pt
# import gdal as gdal
# import rasterio as rs
# import matplotlib.pyplot as plt 
# import math

# #open classified ID file
# classes = rs.open('grass_saint_joseph_bay_cnn_georef.tif')
# classes_id = classes.read(1) #read in the one band from this file

# #Composited imaged
# composited = rs.open('StJoe_water.tif')
# green = composited.read(3) #read in band 3 the green band
# DEM = composited.read(3) #read in band 3 the green band

# #you need to know what numbers have been assigned to the classification.
# #set mask so that any pixels not seagrass are set to nan
# #the input file from this cnn is set to only have seagrass pixels identified
# #if you have all classes on one iamge then you need to continue masking all but seagrass out.
# green = classes_id == 0 # is cnn_id is equal to 0 make a mask
# green[mask] = np.nan #apply the mask above to make all cnn id zero vlaues tobe nan on th WV2 image

# DEM = classes_id == 0 # is cnn_id is equal to 0 make a mask
# DEM[mask] = np.nan #apply the mask above to make all cnn id zero vlaues tobe nan on th WV2 image


#This code calculates leaf area index
#You will need
#1. Orginial file image
#2. Classified file
#3. DEM file (should be in meters, also needs to be the same pixel resolution as your images. Use resampling tool in arcgis to do this.



#############import packages#############
#import gdal as gdal
import rasterio as rs
import os
import pandas as pd
import numpy as np
from tkinter import filedialog #for Python 3
import matplotlib.pyplot as plt 
#########################################


#######get working directory##################################
topdir  = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)################
##############################################################

#######set image and classified images directory##################

#############Folder for composite images###########################
fld_composite = '2b_Composite_images'
path_comp = os.path.abspath(os.path.join(topdir, fld_composite)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_comp, exist_ok=True)
#################Folder for classified images########################
fld_SAVpresence = '5a_SAV_presence'
path_SAVpresence = os.path.abspath(os.path.join(topdir, fld_SAVpresence)) 
####################################################################
############Folder for composite images##################################
fld_temp = 'TEMP'
path_temp = os.path.abspath(os.path.join(topdir, fld_temp)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_temp , exist_ok=True)

#######MAKE OUTPUT FOLDERS############################################
fld_LAI = '4_LAI'
path_LAI = os.path.abspath(os.path.join(topdir , fld_LAI)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_LAI, exist_ok=True)
##############################################

#######select files needed################################################
#1. DEM
#path_DEM=filedialog.askopenfilename(title='Select DEM',filetypes =[('tif', '*.tif')])
###############################################################################


######################################################################################
#######LAI LAI  LAI  LAI  LAI  #################################
######################################################################################
print('*********************************')
print('Starting LAI calculations')
print('*********************************')
#######Set empty arrays################################################################
images=[]
#########Search in orginial files folder################################################
searchdirectory = path_comp
#full directory and file name for all files
for root, dirs, files in os.walk(searchdirectory):
    for name in files:
        if name.endswith(('composite.tif')):
            images.append(os.path.abspath(os.path.join(root,name)))

file_count=len(images)
if file_count == 0:
    print('I cant find any files')
    print('Please check you chose the right working directory')
else:
    print('I found '+str(len(images))+' files to process')
    print('Starting - processing:')
    print('***************************')


##############SET UP EMPTY DATAFRAME##############################################
result=pd.DataFrame(columns=['rastername','area','carbon'])
#####################################################################################
#start to count for loops
count=0
#############Starting processing loop#################################################
for image in images:
    count=count+1
    print('Running loop ' + str(count) + ' of ' + str(file_count))
    #take the image filename and get the corresponding classified file which will be in the directory_classified path
    rastername=(os.path.basename(image).split(".")[0])
    rastername=rastername.partition("_composite")[0]
    ##classified filename###
    SAVpresence=rastername+'_SAVpresence.tif'
    SAVpresence_file=os.path.join(path_SAVpresence,SAVpresence)
    ##TEMP DEM filename###
    DEM=rastername+'_DEM.tif'
    DEM_file=os.path.join(path_temp,DEM)
    ##TEMP GREEN###
    green=rastername+'_green.tif'
    green_file=os.path.join(path_temp,green)
    ##LAI filename###
    LAIname=rastername+('_LAI.tif')
    LAInameout= os.sep.join([path_LAI , LAIname])
    print('Processing file: '+rastername)
    #print('Processing file: '+classified_file)

    if os.path.isfile(LAInameout):
        print("LAI file already exisits - skipping to next file")
    elif os.path.isfile(SAVpresence_file):
        #print("Classifed file found")
        print('Calculating LAI:  '+rastername)
        
########LOAD RASTERS USING RASTERIO################################################       
        #open classified ID file
        classes = rs.open(SAVpresence_file)
        classes_id = classes.read(1) #read in the one band from this file
    
        #Composited imaged
        composited = rs.open(image)
        green = composited.read(2) #read in band 2 the green band
        DEM = composited.read(5) #read in band 5 the DEM band
    
    ###USE THE CLASSIFIED SAV PRESCENCE TO MASK OUT ANY NON-SAV PIXELS
        mask = classes_id == 0 # if class is equal to 0 make a mask
        green[mask] = np.nan #apply the mask above to make all cnn id zero vlaues tobe nan on th WV2 image
    
        mask = classes_id == 0 # is  class is equal to 0 make a mask
        DEM[mask] = np.nan #apply the mask above to make all cnn id zero vlaues tobe nan on th WV2 image

########SELECT ONLY THE GREEN AND DEM BANDS################################################
###########SET BAND NUMBER FOR GREEN BAND AND DEM BAND######################################
        # green_band=2
        # DEM_band=5

        # green= arcpy.MakeRasterLayer_management(image, "green", "", "", green_band)
        # arcpy.CopyRaster_management(green, green_file)
        
        # DEM= arcpy.MakeRasterLayer_management(image, "DEM", "", "", DEM_band)
        # arcpy.CopyRaster_management(DEM, DEM_file)
       
        
       # arcpy.MakeRasterLayer_management(image, "green", "", "", "2")
########Make a new raster taking the full image and only taking band 5 (DEM)
        #arcpy.MakeRasterLayer_management(image, "DEM", "", "", "5")
##    #reclassify to not seagrass and seagrass#########################################
##    #CHECK TO SEE WHAT VALUE YOUR SAV CLASS IS, THIS CLASS WILL BE RECLASSIFIED TO 1, ALL OTHERS EQUAL TO 0.
##    #https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/reclassify.htm
    #SAVpresence=Reclassify(classified_file, "Value", "0 1;1 0;2 0;3 0;4 0;5 0;6 0; 7 0;NODATA 0")


######## Make a raster where only pixels identified as seagrass are retained, all others are set to null.
#######Set all values equal to 0 to null
#        SG_only = SetNull(SAVpresence_file, green, "VALUE = 0")
        Rrs=green*0.0001
        Rrs=Rrs/3.14


########Execute ExtractByMask - use DEM and only retain pixels that were identified as seagrass
#        DEM_SGonly = ExtractByMask(DEM_file, SG_only)
        DEM_M=DEM*-1  #DEM is negative for depth *-1 covnerts to postivie number
        

#####################################################################################
#SET PARAMETERS FOR LAI CALCULATION################################################
######################################################################################
        canopy_height=0.3  #average length of seagrass leeaves.
        tidal_state=-0.5 #06 August2021 1500 GMT. 1.2ft = 0.4m ;  Tide at Wreck island is approx 20 mins earlier than Wachapreague
        #https://tidesandcurrents.noaa.gov/waterlevels.html?id=8631044&units=standard&bdate=20200221&edate=20200223&timezone=GMT&datum=MLLW&interval=6&action=
        #calculate depth of water from sea surface to top of canopy.
        Zcanopy_corr=((DEM_M+tidal_state)-canopy_height)
        #Zcanopy_corr=Con(Zcanopy, 0.1, Zcanopy, "VALUE <= 0");  #if canopy height becomes negative then set to 0.1 m    
################set constants for calculation of Klu and Kd - used Hydrolight to get these values
########VALUES ARE FROM ST JOE BAY
        klu_a=0.0186  # 
        klu_b=0.0452#

        kd_slope=0.003
        kd_intercept=0.1946
        ################calculate klu = a*depth^b+c#############################################
        Klu=(klu_a*Zcanopy_corr)-klu_b
        ################calculate kd
        Kd=(kd_slope*(Zcanopy_corr))+kd_intercept    
        
 
################calculate reflectance at top of canopy#############################################
        Rb=((Rrs*3.1415)/0.54)*(np.exp(-Klu*(Zcanopy_corr))/np.exp(-Kd*(Zcanopy_corr)))
        
      
################calculate LAI from Rb - relationship calculated for Planet bandwdiths
        Rblog = np.log10(Rb)  #; **convert whole spectrum to log
        LAI=-2.92*Rblog-2.11  #m2 m-2
        
        mask = LAI < 0  #SET LAI LESS THAN 0 TO NAN
        LAI[mask] = np.nan
        
###############################################
######save LAI as new geotif
################################################
        # get the metadata of original GeoTIFF:
        meta =composited.meta
        print(meta)
        
        # get the dtype of our NDVI array:
        LAI_dtype = LAI.dtype
        print(LAI_dtype)
        
        # set the source metadata as kwargs we'll use to write the new data:
        kwargs = meta
        # update the 'dtype' value to uint16:
        kwargs.update(dtype='float32')
        
        # update the 'dtype' value to match our NDVI array's dtype:
        #kwargs.update(dtype=LAI_dtype)
        # Convert the type to 'uint16'
        #from rasterio import float32
        #LAIt = LAI.astype(float32)
        # update the 'count' value since our output will no longer be a 4-band image:
        kwargs.update(count=1)
        
        # Finally, use rasterio to write new raster file 'data/ndvi.tif':
        
        #ALL PRODUCTS ARE ONE BAND. IF YOU MAKE PRODUCTS WITH MORE BANDS YOU WILL NEED TO UPDATE YOUR KWARGS SETTING
                
        with rs.open(LAInameout, 'w', **kwargs) as dst:
               dst.write_band(1, LAI.astype(rs.float32))             

#####################################################################################
#CALCULATE BIOMASS###############################################
###################################################################################### 
        pixel_size=3*3 #m2
        #print(pixel_size)
        
        print('Seagrass pixel count: '+str(((np.count_nonzero(LAI > 0))*pixel_size)/1000000)+' (km^2)')
        seagrass_area=((np.count_nonzero(LAI > 0))*pixel_size)/1000000

        LAI_pixel=LAI*pixel_size  #m2

        fresh_wt=LAI*500  #500 g m-2 leaf * LAInump m2 leaf m-2 seabed  = g FW m-2
        fresh_wt_pixel=LAI_pixel*500  #g FW per pixel

        dry_wt = fresh_wt*0.2  # g DW m-2
        dry_wt_pixel= fresh_wt_pixel*0.2  #g Dry Wt per pixel

        carbon=dry_wt*0.35  #g C m-2
        carbon_pixel=dry_wt_pixel*0.35  #g C per pixel

        growth= fresh_wt*0.01*365  # g C yr-1
        growth_pixel= fresh_wt_pixel*0.01*365  # g C yr-1

        total_fresh_wt=np.nansum(fresh_wt_pixel)  #g FW
        total_fresh_wt=total_fresh_wt/1000000000 #giga grams

        total_dry_wt=np.nansum(dry_wt_pixel)  #g FW
        total_dry_wt=total_dry_wt/1000000000 #giga grams

        total_carbon_wt=np.nansum(carbon_pixel)  #g FW
        total_carbon_wt=total_carbon_wt/1000000000 #giga grams

        print('total carbon weight:'+ str(total_carbon_wt) +' (giga grams)')
        total_carbon=total_carbon_wt

        carbon_mean=np.nanmean(carbon)
        carbon_stdev=np.nanstd(carbon)

        LAI_mean=np.nanmean(LAI)
        LAI_stdev=np.nanstd(LAI)


        print('LAI mean value:' +str(LAI_mean))
        print('carbon mean value:' +str(carbon_mean))
        print('LAI stdev value:' +str(LAI_stdev))
        print('carbon stdev value:' +str(carbon_stdev))

                   
        
        stats_out=rastername+('_stats.txt')
        stats_outpath= os.sep.join([path_LAI, stats_out])
        #print(outputfilename)
        np.savetxt(stats_outpath, ["seagrass_area km2: %s total carbon weight Gg: %s" % (seagrass_area,total_carbon)], fmt='%s')
        print("saved area and total carbon: "+stats_outpath)
    
        print('**************************')
        print(result)


# print("FINISHED LAI - Calculating mean annual LAI")

# #######################################################################################################
# ####CALCULATE MEAN LAI
# ##OVERWRITES OLD MEAN LAI FILES - SO WILL UPDATE AS NEW IMAGES PROCESSED
# #######################################################################################################


# ###################Setting so that the frequency files can be overwritten################################
# arcpy.env.overwriteOutput = True
# #######################################################################################################

# searchdirectory = path_LAI
# #get just the filenames that end in shrink.tif, depending on what level of processing you did in step 2 this maybe different for you
# LAI_files=[]
# for root, dirs, files in os.walk(searchdirectory):
#     for image_name in files:
#         if image_name.endswith(('_LAI.tif')):
#             fullfile=os.path.abspath(os.path.join(path_LAI,image_name))
#             LAI_files.append(fullfile)
        
# needed_rasters_virtual = [arcpy.Raster(i) for i in LAI_files]
# #print('Using the following images: ')
# print(needed_rasters_virtual)


# ################MAKE THE NAME OF OUTPUT MEAN LAI FILE
# path_site=os.path.basename(topdir)
# site_name=path_site+'_meanLAI.tif'
# mean_LAI_out=os.sep.join([path_LAI , site_name])

# with arcpy.EnvManager(extent="MAXOF"):
#     #iletype='EasternShore_LAI_mean_2019.tif'
#     #LAIname= os.sep.join([directory, filetype])
#     meanLAI = CellStatistics(needed_rasters_virtual, "MEAN", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
#     meanLAI.save(mean_LAI_out)#change this to save your frequency file
        
# print('LAI mean file is saved'+mean_LAI_out)   
