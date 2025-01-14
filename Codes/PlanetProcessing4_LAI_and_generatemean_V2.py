#7 June 2022 - Victoria Hill (vhill@odu.edu)
#This code calculates leaf area index
#You will need
#1. Orginial file image
#2. Classified file
#3. DEM file (should be in meters, also needs to be the same pixel resolution as your images. Use resampling tool in arcgis to do this.



#############import packages#############
import arcpy
from arcpy import env
from arcpy.sa import *
import os
import pandas as pd
import numpy as np
from tkinter import filedialog #for Python 3
#########################################


#######get working directory##################################
topdir  = filedialog.askdirectory(title='Select working directory')
print('Your working directory is: '+topdir)################
##############################################################

#######set image and classified images directory##################
########Folder for orginial images#######################################
fld_org = '1_Images'
dir_images= os.path.abspath(os.path.join(topdir, fld_org))
print('Your image directory is: '+dir_images)
print('*********************************')
#############Folder for composite images###########################
fld_composite = '2b_Composite_images'
path_comp = os.path.abspath(os.path.join(topdir, fld_composite)) 
# Creates the folder, and checks if it is created or not.
os.makedirs(path_comp, exist_ok=True)
#################Folder for classified images########################
fld_classified = '5a_SAV_presence'#'3a_Classified'
path_SAVpresence = os.path.abspath(os.path.join(topdir, fld_classified)) 
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


######################################################################################
##Get csv with tide state info
######################################################################################
path_tide=filedialog.askopenfilename(title='Select csv file with tide information',filetypes =[('csv', '*.csv')])

# Read CSV file into a Pandas DataFrame
tide = pd.read_csv(path_tide)
tide_state=tide[['ImageID','relative MLLW']]

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

    ##SAV only raster in green band filename###
    SAVonly=rastername+('_SAVonly.tif')
    SAVonlyout= os.sep.join([path_temp , SAVonly])    
    ##DEM with only SAV pixels###
    DEMSAVonly=rastername+('_DEMSAVonly.tif')
    DEMSAVonlyout= os.sep.join([path_temp , DEMSAVonly])
    
    print('Processing file: '+rastername)
    


    if os.path.isfile(LAInameout):
        print("LAI file already exisits - skipping to next file")
    elif os.path.isfile(SAVpresence_file):
        #print("Classifed file found")
        print('Calcualting LAI:  '+rastername)
        
#######SELECT ONLY THE GREEN AND DEM BANDS###########################
##########SET BAND NUMBER FOR GREEN BAND AND DEM BAND######################################
        #green_band=2 #4 for 8 band #2 for 4 band
        #DEM_band=5 # 9 for the 8 band  #5 for 4 band
        dsc = arcpy.Describe(image)
        num_bands = dsc.bandCount
        print(f"The raster has {num_bands} bands.")
        if num_bands == 9:
            green_band=4
            DEM_band=9
        elif num_bands ==5:
            green_band=2
            DEM_band=5

        green= arcpy.MakeRasterLayer_management(image, "green", "", "", green_band)
        arcpy.CopyRaster_management(green, green_file)
        
        DEM= arcpy.MakeRasterLayer_management(image, "DEM", "", "", DEM_band)
        arcpy.CopyRaster_management(DEM, DEM_file)
       
        

#         #IF USING NEW MASTER SCHEMA SAV SHOULD BE 11, 12 AND 13.       
# ######## Make a raster where only pixels identified as seagrass are retained, all others are set to null.
# #######Set all values equal to 0 to null
        SAVonly = SetNull(SAVpresence_file, green, "VALUE <=0")# "VALUE >= 20")
        SAVonly.save(SAVonlyout)
        
        Rrs=SAVonly*0.0001
        Rrs=Rrs/3.14


# ########Execute ExtractByMask - use DEM and only retain pixels that were identified as seagrass
        DEMSAVonly = ExtractByMask(DEM_file, SAVonlyout)
        DEMSAVonly.save(DEMSAVonlyout)
        
        DEM_MLLW=DEMSAVonly+0.8
        DEM=DEM_MLLW*-1  #DEM is negative for depth *-1 converts to postivie number

# #####################################################################################
# #SET PARAMETERS FOR LAI CALCULATION################################################
    #FIND CORRESPONDING TIDAL STATE
    # Use loc
        tide_depth = tide_state.loc[tide_state['ImageID'] == rastername, 'relative MLLW']
        tide_depth = tide_depth.item()
# ######################################################################################
        canopy_height=0.3  #average length of seagrass leeaves.
        tidal_state=tide_depth #06 August2021 1500 GMT. 1.2ft = 0.4m ;  Tide at Wreck island is approx 20 mins earlier than Wachapreague
        #https://tidesandcurrents.noaa.gov/waterlevels.html?id=8631044&units=standard&bdate=20200221&edate=20200223&timezone=GMT&datum=MLLW&interval=6&action=
        #calculate depth of water from sea surface to top of canopy.
        Zcanopy=((DEM+tidal_state)-canopy_height)
        Zcanopy_corr=Con(Zcanopy, 0.1, Zcanopy, "VALUE <= 0")  #if canopy height becomes negative then set to 0.1 m    
# ################set constants for calculation of Klu and Kd - used Hydrolight to get these values
# ########VALUES ARE FROM ST JOE BAY
        klu_a=0.0186  # 
        klu_b=0.0452#

        kd_slope=0.003
        kd_intercept=0.1946
        ################calculate klu = a*depth^b+c#############################################
        Klu=(klu_a*Zcanopy_corr)-klu_b
        ################calculate kd
        Kd=(kd_slope*(Zcanopy_corr))+kd_intercept    
################calculate reflectance at top of canopy#############################################
        Rb=((Rrs*3.1415)/0.54)*(Exp(-Klu*(Zcanopy_corr))/Exp(-Kd*(Zcanopy_corr)))

      
# ################calculate LAI from Rb - relationship calculated for Planet bandwdiths
        Rblog = Log10(Rb)  #; **convert whole spectrum to log
        LAI_prelim=-2.92*Rblog-2.11  #m2 m-2

##########################set any emergent SAV = 13 to LAI of 3
        LAI = Con(in_conditional_raster=LAI_prelim,in_true_raster_or_constant=3,in_false_raster_or_constant=LAI_prelim,where_clause="Value > 3")
        LAI.save(LAInameout)
        print('LAI file saved:  '+LAInameout)



        ###############convert LAI raster to numpy for some analysis###################################
        LAInump = arcpy.RasterToNumPyArray(LAI)
        mask = LAInump < 0  #SET lai LESS THAN 0 TO NAN
        LAInump[mask] = np.nan

        pixel_size=3*3 #m2
        #print(pixel_size)

 #####################################################################################
 #CALCULATE BIOMASS###############################################
 ###################################################################################### 

        print('Seagrass pixel count: '+str(((np.count_nonzero(LAInump > 0))*pixel_size)/1000000)+' (km^2)')
        seagrass_area=((np.count_nonzero(LAInump > 0))*pixel_size)/1000000

        LAInump_pixel=LAInump*pixel_size  #m2

        fresh_wt=LAInump*500  #500 g m-2 leaf * LAInump m2 leaf m-2 seabed  = g FW m-2
        fresh_wt_pixel=LAInump_pixel*500  #g FW per pixel

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

        LAI_mean=np.nanmean(LAInump)
        LAI_stdev=np.nanstd(LAInump)


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



print("FINISHED LAI - Calculating mean annual LAI")

#######################################################################################################
####CALCULATE MEAN LAI
##OVERWRITES OLD MEAN LAI FILES - SO WILL UPDATE AS NEW IMAGES PROCESSED
#######################################################################################################


###################Setting so that the frequency files can be overwritten################################
arcpy.env.overwriteOutput = True
#######################################################################################################

searchdirectory = path_LAI
#get just the filenames that end in shrink.tif, depending on what level of processing you did in step 2 this maybe different for you
LAI_files=[]
for root, dirs, files in os.walk(searchdirectory):
 for image_name in files:
     if image_name.endswith(('_LAI.tif')):
         fullfile=os.path.abspath(os.path.join(path_LAI,image_name))
         LAI_files.append(fullfile)
    
needed_rasters_virtual = [arcpy.Raster(i) for i in LAI_files]
#print('Using the following images: ')
#print(needed_rasters_virtual)


################MAKE THE NAME OF OUTPUT MEAN LAI FILE
path_site=os.path.basename(topdir)
site_name=path_site+'_meanLAI.tif'
mean_LAI_out=os.sep.join([path_LAI , site_name])

with arcpy.EnvManager(extent="MAXOF"):
 #iletype='EasternShore_LAI_mean_2019.tif'
 #LAIname= os.sep.join([directory, filetype])
 meanLAI = CellStatistics(needed_rasters_virtual, "MEAN", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
 meanLAI.save(mean_LAI_out)#change this to save your frequency file
    
print('LAI mean file is saved'+mean_LAI_out)

################MAKE THE NAME OF OUTPUT MEDIAN LAI FILE
path_site=os.path.basename(topdir)
site_name=path_site+'_medianLAI.tif'
median_LAI_out=os.sep.join([path_LAI , site_name])

with arcpy.EnvManager(extent="MAXOF"):
 #iletype='EasternShore_LAI_mean_2019.tif'
 #LAIname= os.sep.join([directory, filetype])
 medianLAI = CellStatistics(needed_rasters_virtual, "MEDIAN", "", "") #you are summing all overlapping pixels, so SAV has to equal 1 in all your mosaiced files
 medianLAI.save(median_LAI_out)#change this to save your frequency file
    
print('LAI median file is saved'+median_LAI_out)   
