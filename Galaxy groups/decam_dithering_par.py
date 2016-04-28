#!/usr/bin/env python

#Calling sequence: >python decam_dithering.py [dithering pattern] [probe (optional)]
#Current dithering options = 'rect', 'rect_centre', 'hexagon', 'spiral', 'spiral2'
#e.g. >python decam_dithering.py spiral
#e.g. >python decam_dithering.py spiral probe (if one desires the probe output, severely increased execution time)

#Outputs:
#dithering_pattern_NAME.pdf - the coverage map of the simulation, including target (green star), probe positions (red circles)
#, targets of interest (red triangles), and pointings (black dots). NAME = whatever dithering pattern was selected.
#pointing_coords_NAME.txt - the list of pointing coordinates including dither positions. Each set of dither points are
#separated by pN, where N is the number of the pointing.
#spiral.pdf - if 'spiral' is selected, this is an example of the Fermat spiral used. The pointings are repeated for each sky field.
#e.g. Pointing #1 in the spiral is repeated for the target field, then sky1, then the target again,
#then sky2 before moving on to Pointing #2 and repeating...
#The 'spiral2' options does the Fermat spiral with the pattern: 
#  Pointing #1 Target, Pointing #1 Sky1, Pointing #2 Target, Pointing #2 Sky2, Pointing #3 Target, Pointing #3 Sky3,
#  Pointing #4 Target, Pointing #4 Sky1, ....
#decam_probes_NAME.pdf - A plot showing the results of the probes. The exposure times are collapsed about RA and Dec
#for each of the requested probe positions.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import sys
import json
from multiprocessing import cpu_count
from joblib import Parallel, delayed

#################################################################################
#Draw the footprint of DECam. MODIFY AT YOUR OWN RISK!!!
#I assure you that it's accurate...trust me?
#################################################################################
def draw_chips(x,y,chip_x0,gap_sht0):
    #create a package of structures to draw the chips
    import matplotlib.patches as patches
    from matplotlib.collections import PatchCollection
    
    row_nums = [2,4,5,6,6,7,7,6,6,5,4,2]
    chips = []
    
    for ii in range(len(row_nums)):
        if ii == 0:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+11.*chip_y+11.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+4.*chip_x+4.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - 2.*chip_x - 2.*gap_sht
        if ii == 1:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+10.*chip_y+10.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+4.*chip_x+5.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 2:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+9.*chip_y+9.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+5.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 3:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+8.*chip_y+8.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+6.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 4:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+7.*chip_y+7.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+6.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 5:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+6.*chip_y+6.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+6.*chip_x+6.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 6:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+5.*chip_y+5.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+6.*chip_x+6.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 7:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+4.*chip_y+4.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+6.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 8:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+3.*chip_y+3.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+6.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 9:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+2.*chip_y+2.*gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+5.*chip_x+5.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 10:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+chip_y+gap_lng
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+4.*chip_x+5.*gap_sht+chip_x/2.
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - chip_x - gap_sht
        if ii == 11:
            y0 = (y-6.*chip_y-5.*gap_lng-gap_lng/2.)+0
            chip_x = chip_x0/np.cos(y0*np.pi/180.)
            gap_sht = gap_sht0/np.cos(y0*np.pi/180.)
            x0 = (x-3.*chip_x-3.*gap_sht-chip_x/2.)+4.*chip_x+4.*gap_sht
            for jj in range(row_nums[ii]):
                rect = patches.Rectangle([x0,y0],chip_x,chip_y)
                chips.append(rect)
                hits_ra.append([x0,(x0+chip_x)])
                hits_dec.append([y0,y0+chip_y])
                x0 = x0 - 2.*chip_x - 2.*gap_sht
    return chips

######################################################
#Draw the footprint of the selected dithering pattern
######################################################
def draw_footprint(point_ra,point_dec,chip_x,gap_sht,iis=0):
    #define a dithering pattern
    global name
    #print name
    if name == 'spiral':
        points_x = [point_ra, \
            point_ra+(sky_coords[0][0]-target_ra)*np.cos((sky_coords[0][1]-target_dec)*np.pi/180.), \
            point_ra-offset/3600., \
            point_ra+(sky_coords[1][0]-target_ra)*np.cos((sky_coords[1][1]-target_dec)*np.pi/180.),\
            point_ra+offset/3600., \
            point_ra+(sky_coords[2][0]-target_ra)*np.cos((sky_coords[2][1]-target_dec)*np.pi/180.)]
            
        points_y = [point_dec, \
            point_dec+(sky_coords[0][1]-target_dec), \
            point_dec+offset/3600., \
            point_dec+(sky_coords[1][1]-target_dec),\
            point_dec-offset/3600., \
            point_dec+(sky_coords[2][1]-target_dec)]
            
        p1 = PatchCollection(draw_chips(point_ra,point_dec,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra+(sky_coords[0][0]-target_ra)*np.cos((sky_coords[0][1]-target_dec)*np.pi/180.),\
        point_dec+(sky_coords[0][1]-target_dec),chip_x,gap_sht),alpha=0.1)
        p3 = PatchCollection(draw_chips(point_ra+1./3600.,point_dec+1./3600.,chip_x,gap_sht),alpha=0.1)
        p4 = PatchCollection(draw_chips(point_ra+(sky_coords[1][0]-target_ra)*np.cos((sky_coords[1][1]-target_dec)*np.pi/180.),\
        point_dec+(sky_coords[1][1]-target_dec),chip_x,gap_sht),alpha=0.1)
        p5 = PatchCollection(draw_chips(point_ra-1./3600.,point_dec-1./3600.,chip_x,gap_sht),alpha=0.1)
        p6 = PatchCollection(draw_chips(point_ra+(sky_coords[2][0]-target_ra)*np.cos((sky_coords[2][1]-target_dec)*np.pi/180.),\
        point_dec+(sky_coords[2][1]-target_dec),chip_x,gap_sht),alpha=0.1)
        
        collection = [p1,p2,p3,p4,p5,p6]

    if name == 'spiral2':
        points_x = [point_ra, \
            point_ra+(sky_coords[iis][0]-target_ra)*np.cos((sky_coords[iis][1]-target_dec)*np.pi/180.)]
             
        points_y = [point_dec, \
            point_dec+(sky_coords[iis][1]-target_dec)]

        p1 = PatchCollection(draw_chips(point_ra,point_dec,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra+(sky_coords[iis][0]-target_ra)*np.cos((sky_coords[iis][1]-target_dec)*np.pi/180.),\
        point_dec+(sky_coords[iis][1]-target_dec),chip_x,gap_sht),alpha=0.1)
        
        collection = [p1,p2]

    if name == 'tetra':
        points_x = [point_ra+3.*dra/2.,point_ra+dra/2.,point_ra-dra/2.,point_ra-3.*dra/2.]
        points_y = [point_dec-ddec/2.,point_dec+3.*ddec/2.,point_dec-3.*ddec/2.,point_dec+ddec/2.]
        p1 = PatchCollection(draw_chips(point_ra+3.*dra/2.,point_dec-ddec/2.,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra+dra/2.,point_dec+3.*ddec/2.,chip_x,gap_sht),alpha=0.1)
        p3 = PatchCollection(draw_chips(point_ra-dra/2.,point_dec-3.*ddec/2.,chip_x,gap_sht),alpha=0.1)
        p4 = PatchCollection(draw_chips(point_ra-3.*dra/2.,point_dec+ddec/2.,chip_x,gap_sht),alpha=0.1)
        collection = [p1,p2,p3,p4]

    if name == 'rect':
        points_x = [point_ra+dra/2.,point_ra+dra/2.,point_ra-dra/2.,point_ra-dra/2.]
        points_y = [point_dec-ddec/2.,point_dec+ddec/2.,point_dec+ddec/2.,point_dec-ddec/2.]
        p1 = PatchCollection(draw_chips(point_ra+dra/2.,point_dec-ddec/2.,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra+dra/2.,point_dec+ddec/2.,chip_x,gap_sht),alpha=0.1)
        p3 = PatchCollection(draw_chips(point_ra-dra/2.,point_dec+ddec/2.,chip_x,gap_sht),alpha=0.1)
        p4 = PatchCollection(draw_chips(point_ra-dra/2.,point_dec-ddec/2.,chip_x,gap_sht),alpha=0.1)
        collection = [p1,p2,p3,p4]

    if name == 'rect_centre':
        points_x = [point_ra,point_ra-1.*dra,point_ra+dra,point_ra+dra,point_ra-1.*dra]
        points_y = [point_dec,point_dec-1.*ddec,point_dec-1.*ddec,point_dec+ddec,point_dec+ddec]
        p1 = PatchCollection(draw_chips(point_ra,point_dec,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra-dra,point_dec-ddec,chip_x,gap_sht),alpha=0.1)
        p3 = PatchCollection(draw_chips(point_ra+dra,point_dec-ddec,chip_x,gap_sht),alpha=0.1)
        p4 = PatchCollection(draw_chips(point_ra+dra,point_dec+ddec,chip_x,gap_sht),alpha=0.1)
        p5 = PatchCollection(draw_chips(point_ra-dra,point_dec+ddec,chip_x,gap_sht),alpha=0.1)
        collection = [p1,p2,p3,p4,p5]

    if name == 'hexagon':
        points_x = [point_ra+dra/2.,point_ra+dra/4.  ,point_ra-dra/4.  ,point_ra-dra/2.,point_ra-dra/4.  ,point_ra+dra/4.]
        points_y = [point_dec      ,point_dec+ddec/2.,point_dec+ddec/2.,point_dec      ,point_dec-ddec/2.,point_dec-ddec/2.]
        p1 = PatchCollection(draw_chips(point_ra+dra/2,point_dec,chip_x,gap_sht),alpha=0.1)
        p2 = PatchCollection(draw_chips(point_ra+dra/4.,point_dec+ddec/2.,chip_x,gap_sht),alpha=0.1)
        p3 = PatchCollection(draw_chips(point_ra-dra/4.,point_dec+ddec/2.,chip_x,gap_sht),alpha=0.1)
        p4 = PatchCollection(draw_chips(point_ra-dra/2.,point_dec,chip_x,gap_sht),alpha=0.1)
        p5 = PatchCollection(draw_chips(point_ra-dra/4.,point_dec-ddec/2.,chip_x,gap_sht),alpha=0.1)
        p6 = PatchCollection(draw_chips(point_ra+dra/4.,point_dec-ddec/2.,chip_x,gap_sht),alpha=0.1)
        collection = [p1,p2,p3,p4,p5,p6]
    
    return points_x, points_y, collection

######################################################
#Probe calculation
######################################################
def probecalc(probes,pcheck_ra,pcheck_dec,hits_ra0,hits_ra1,hits_dec0,hits_dec1,ii):
    print "Probe %i, RA...." % (ii)
    cnt_ra = [] 
    for ra in pcheck_ra:
        mask = np.where(hits_dec0 <= probes[ii][1],1,0)
        chk_ra0 = np.compress(mask,hits_ra0)
        chk_ra1 = np.compress(mask,hits_ra1)
        chk_dec0 = np.compress(mask,hits_dec0)
        chk_dec1 = np.compress(mask,hits_dec1)
        mask = np.where(chk_dec1 >= probes[ii][1],1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)
        mask = np.where(chk_ra0 <= ra,1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)
        mask = np.where(chk_ra1 >= ra,1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)

        cnt_ra.append(len(chk_ra0))

    print "Probe %i, Dec...." % (ii)
    cnt_dec = []    
    for dec in pcheck_dec:
        mask = np.where(hits_ra0 <= probes[ii][0],1,0)
        chk_ra0 = np.compress(mask,hits_ra0)
        chk_ra1 = np.compress(mask,hits_ra1)
        chk_dec0 = np.compress(mask,hits_dec0)
        chk_dec1 = np.compress(mask,hits_dec1)
        mask = np.where(chk_ra1 >= probes[ii][0],1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)
        mask = np.where(chk_dec0 <= dec,1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)
        mask = np.where(chk_dec1 >= dec,1,0)
        chk_ra0 = np.compress(mask,chk_ra0)
        chk_ra1 = np.compress(mask,chk_ra1)
        chk_dec0 = np.compress(mask,chk_dec0)
        chk_dec1 = np.compress(mask,chk_dec1)

        cnt_dec.append(len(chk_ra0))
        
    return [cnt_ra,cnt_dec]

if __name__ == '__main__':

    ###########
    #Set the individual detector integration times
    ###########
    dit = 120 #seconds

    ###########
    #Set the overhead (readout+slew) between exposures
    ###########
    ovr = 20 #seconds

    ###########
    #Set the number of pointings for the spiral patterns
    ###########
    #n_point = 90  # i
    n_point = 120  # g

    ############
    #Set the dither size if not using Fermat spiral
    ############
    dra = 60./3600. #dither size in x-direction in degrees
    ddec = 60.0/3600. #dither size in y-direction in degrees

    ############
    #Set the coordinates of the target, sky field(s), and any extra targets of interest
    ############
    ngc3923_ra = (11.+51./60.+1.783/3600.)*15. #target RA
    ngc3923_dec = (-28.-48./60.-22.36/3600.) #target Dec

    # Galaxy in chip S4 - preferred
    target_ra = (11.+50./60.+36.7/3600.)*15. #target RA
    target_dec = (-28.-53./60.-34.0/3600.) #target Dec

    #target_ra = (11.+50./60.+43.5/3600.)*15. #target RA
    # Galaxy in chip S11
    #target_ra = (11.+50./60.+25.0/3600.)*15. #target RA
    #target_dec = (-29.-3./60.-0.0/3600.) #target Dec

    # Galaxy in chip S10, no good
    #target_ra = (11.+51./60.+21.0/3600.)*15. #target RA
    #target_dec = (-29.-3./60.-0.0/3600.) #target Dec

    # Old test
    #target_ra = (11.+49./60.+56.85/3600.)*15. #target RA
    #target_dec = (-28.-53./60.-15./3600.) #target Dec

    #sky_coords = [[(11.+43./60.+29./3600.)*15.,-27-17./60.-5./3600.],
    #               [(11.+54./60.+45.9/3600.)*15.,-26-45./60.-13./3600]] #sky fields [RA, Dec] coordinates

    #sky_coords = [[(12.+1./60.+17.26/3600.)*15.,-28.-11./60.-38.3/3600.],
    sky_coords = [[(11.+49./60.+37.6/3600.)*15.,-25.-27./60.-53.7/3600.],
                    [(11.+53./60.+55.6/3600.)*15.,-26-20./60.-4.7/3600], #sky fields [RA, Dec] coordinates
                    [(11.+58./60.+12.8/3600.)*15.,-27.-11./60.-37.9/3600.], #sky fields [RA, Dec] coordinates
    #                [(11.+36./60.+40.4/3600.)*15.,-29.-52./60.-12.3/3600.], #sky fields [RA, Dec] coordinates
                    [(11.+36./60.+40.4/3600.)*15.,-30.-3./60.-56.3/3600.], #sky fields [RA, Dec] coordinates
                    [(11.+41./60.+36.8/3600.)*15.,-25.-53./60.-42.7/3600]] #sky fields [RA, Dec] coordinates

    gal_coords = [[(11.+49./60.+13.206/3600.)*15.,-29.-16./60.-36.09/3600.],
                    [15.*(11.+52./60.+03.1/3600.),-26.-37./60-25./3600.],
                    [15.*(11.+54./60.+58.4/3600.),-27.-16./60.-31./3600.]] #ToI [RA, Dec] coordinates

    star_coords = [[(11.+55./60.+40.08/3600.)*15.,-28.-28./60.-34.85/3600.],
                    [15.*(11.+48./60.+44.94/3600.),-26.-44./60-56.94/3600.],
                    [15.*(11.+58./60.+54.12/3600.),-25.-54./60-26.47/3600.],
                    [15.*(11.+54./60.+42.22/3600.),-25.-42./60.-40.6/3600.], #ToI [RA, Dec] coordinates
                    [15.*(11.+32./60.+14.6/3600.),-29.-15./60.-44.6/3600.], #ToI [RA, Dec] coordinates
                    [15.*(11.+41./60.+8.18/3600.),-29.-11./60.-50.2/3600.]] #ToI [RA, Dec] coordinates

    ##############
    #Set the window size for the coverage and probe plots (automatic sizing is still buggy, I suggest to
    #just set them manually.
    ##############
    xlim = [np.max([target_ra,np.max(sky_coords[:][0])])+1.5*np.cos(target_dec*np.pi/180.),np.min([target_ra,np.min(sky_coords[:][0])])-1.5*np.cos(target_dec*np.pi/180.)]
    ylim = [np.min([target_dec,np.min(sky_coords[:][1])])-1.5,np.max([target_dec,np.max(sky_coords[:][1])])+1.5]

    xlim = [172,181]
    ylim = [-31.5,-24]

    ###############
    #Set the coordinates for whatever probes you want to put in the field, note that each one significantly increases
    #the running time.
    ###############
    #if len(sys.argv) > 2:
    #   if sys.argv[2] == 'probe':
    probes = [[target_ra,target_dec],
             [sky_coords[0][0],sky_coords[0][1]],
             [sky_coords[1][0],sky_coords[1][1]], # probe [RA, Dec] coordinates
             [sky_coords[2][0],sky_coords[2][1]], # probe [RA, Dec] coordinates
             [sky_coords[3][0],sky_coords[3][1]], # probe [RA, Dec] coordinates
             [sky_coords[4][0],sky_coords[4][1]]] # probe [RA, Dec] coordinates
    probes = np.array(probes)

    ##############
    #Set the details of the detector
    ##############
    pres = 0.2632 #pixel scale in arcsec/pix

    global chip_x, chip_y

    gap_sht = 153. #chip gap along x-direction in pixels
    gap_lng = 201. #chip gap along y-direction in pixels
    chip_x = 4096. #chip size along x-direction in pixels
    chip_y = 2048. #chip size along y-direction in pixels

    gap_sht = gap_sht*pres/3600. #degrees
    gap_lng = gap_lng*pres/3600. #degrees
    chip_x = chip_x*pres/3600. #degrees
    chip_y = chip_y*pres/3600. #degrees

    offset = 60.

    hits_ra = [] #initialize list to count probe hits
    hits_dec = [] 

    ##############
    global name
    global probe
    name = ''
    fprobe = ''
    probe = False
    fdisp = ''
    display = False

    try:
        name = sys.argv[1]
    except:
        name = [raw_input('Enter pattern option [spiral, spiral2, tetra, rect, rect_centre, hexagon]: ')][0]
        fprobe = [raw_input('Probe output [yes/no]: ')][0]
        if (fprobe == 'yes'):
            probe = True
        display = True
        fdisp = [raw_input('Display plots [yes/no]: ')][0]
        if (fdisp == 'no'):
            display = False

    if len(sys.argv) > 2:
        if 'probe' in sys.argv:
            probe = True
        if 'display' in sys.argv:
            display = True      

    ##############
    # Parameters for json output
    ##############
    cnt = 1
    exptype = "object"
    object = "NGC3923"
    filter = "g"
    seqid = filter+str(dit)+"_"+name
    outroot = object+"_"+seqid
    
    ##############
    #What file do you want to save the final coordinates to?
    ##############
    #fileout = open('pointing_coords_%s.txt' % sys.argv[1],'w') #output for dither pointings
    #name = 'spiral'
    fileout = open('%s_coords.txt' % outroot,'w') #output for dither pointings
    jsonout = open('%s.json' % outroot,'w') #output for dither pointings
    print >> jsonout, '['


    ######################################################
    #Calculate the coordinates that are dithered around.
    # 1)If using a spiral pattern, each point in the spiral will be dithered according to the 
    #pattern specified in draw_footprints(). Two options are given so that by changing between 'orig'
    #and 'test', one can easily keep the best-so-far pointing set, while using the other as a 
    #workbench to play around with different pointings.
    #
    # 2)Remember that each point is dithered around, so for the 'spiral' option, the 'dithering
    #pattern' is, in fact just switching from target field - sky1 - target - sky2. The spiral dither is encoded 
    #in this function itself. If instead one defines the pointings as a set of absolute pointing coordinates, and 
    #selects, e.g. 'rect', then the rectangle dithering pattern defined by dra and ddec will dither around each of
    #the specified pointings.
    ######################################################
    def get_pointings(target_ra,target_dec,chip_x,gap_sht,chip_y,gap_lng,type,n_point=90):
        #calculate the pointings, save your favourite as 'orig', conduct different experimental setups with 'test'
        #global chip_x, chip_y
    
        if type == 'orig':
            pointings = [[target_ra,target_dec]] #example of a single pointing that gets dithered around would be pointings=[[target_ra,target_dec]]

        if type == 'test':
            ####The parameter "a" defines how compact the spiral is, n_point defines how many pointings go into the spiral
            if name == 'spiral2':
                a = 0.02
            elif name == 'spiral':
                a = 2.*chip_x/15.
            else:
                a = 0.025
            b = 1.0
    #       n_point = 120    # For NGC3923 g-band
    #        n_point = 90    # For NGC3923 i-band
            theta = 137.508*np.pi/180.
        
            plt.figure(figsize=(12,10))
            pointings = []
            for ii in range(n_point):
                ra = a*np.sqrt(ii)*np.cos(b*ii*theta)
                dec = a*np.sqrt(ii)*np.sin(b*ii*theta)
                pointings.append([target_ra+ra*np.cos((target_dec+dec)*np.pi/180.),target_dec+dec])
                plt.plot([target_ra+ra*np.cos((target_dec+dec)*np.pi/180.)],[target_dec+dec],'bo')
                plt.annotate('%i' % (ii+1),xy=(target_ra+ra*np.cos((target_dec+dec)*np.pi/180.),target_dec+dec))
            plt.savefig('%s.pdf' % outroot)
        return pointings

    #########################
    #Get the pointing coordinates
    ##########################
    if name == 'spiral' or name == 'spiral2':
        pointings = get_pointings(target_ra,target_dec,chip_x,gap_sht,chip_y,gap_lng,'test',n_point) #switch between 'test' and 'orig' as you please
    else:
        pointings = get_pointings(target_ra,target_dec,chip_x,gap_sht,chip_y,gap_lng,'orig',n_point) #switch between 'test' and 'orig' as you please

    ##########################
    #Mimic the draw_footprints() function, and save the dithering coordinates to a file separated
    #by 'pN' where N is the pointing number. These coordinates can then be put into the
    #telescope observing script as you like.
    ##########################
    iis = 0
    npsrc = 0
    npoints = 0
    points = []
    for ii in range(len(pointings)):
        objlst = []
        if name == 'spiral':
            points = [[pointings[ii][0],pointings[ii][1]],\
                        [pointings[ii][0]+(sky_coords[0][0]-target_ra)*np.cos((sky_coords[0][1]-target_dec)*np.pi/180.),\
                         pointings[ii][1]+(sky_coords[0][1]-target_dec)],\
                      [pointings[ii][0]-offset/3600.,pointings[ii][1]+offset/3600.],\
                        [pointings[ii][0]+(sky_coords[1][0]-target_ra)*np.cos((sky_coords[1][1]-target_dec)*np.pi/180.),\
                         pointings[ii][1]+(sky_coords[1][1]-target_dec)],\
                      [pointings[ii][0]+offset/3600.,pointings[ii][1]-offset/3600.],\
                        [pointings[ii][0]+(sky_coords[2][0]-target_ra)*np.cos((sky_coords[2][1]-target_dec)*np.pi/180.),\
                         pointings[ii][1]+(sky_coords[2][1]-target_dec)]]
            objlst = [object,'Sky Probe2',object,'Sky Probe3',object,'Sky Probe4']
            npsrc = npsrc + 3
        if name == 'spiral2':
            points = [[pointings[ii][0],pointings[ii][1]],[pointings[ii][0]+\
                    (sky_coords[iis][0]-target_ra)*np.cos((sky_coords[iis][1]-target_dec)*np.pi/180.),\
                    pointings[ii][1]+(sky_coords[iis][1]-target_dec)]]
            npsrc = npsrc + 1 
            iis = iis + 1
            objlst = [object,'Sky Probe'+str(iis)]
            if iis == len(sky_coords):
                iis = 0
        if name == 'tetra':
            points = [[pointings[ii][0]+3.*dra/2.,pointings[ii][1]-ddec/2.],
                      [pointings[ii][0]+dra/2.,pointings[ii][1]+3.*ddec/2.],
                      [pointings[ii][0]-dra/2.,pointings[ii][1]-3.*ddec/2.],
                      [pointings[ii][0]-3.*dra/2.,pointings[ii][1]+ddec/2.]]
            [objlst.append(object) for jj in range(len(points))]
            print >> fileout, "p%i" % (ii+1)
            npsrc = npsrc + 4 
        if name == 'rect':
            points = [[pointings[ii][0]+dra/2.,pointings[ii][1]-ddec/2.],
                      [pointings[ii][0]+dra/2.,pointings[ii][1]+ddec/2.],
                      [pointings[ii][0]-dra/2.,pointings[ii][1]+ddec/2.],
                      [pointings[ii][0]-dra/2.,pointings[ii][1]-ddec/2.]]
            [objlst.append(object) for jj in range(len(points))]
            print >> fileout, "p%i" % (ii+1)
            npsrc = npsrc + 4 
        if name == 'rect_centre':
            points = [[pointings[ii][0],pointings[ii][1]],
                      [pointings[ii][0]-1.*dra,pointings[ii][1]-1.*ddec],
                      [pointings[ii][0]+dra,pointings[ii][1]-1.*ddec],
                      [pointings[ii][0]+dra,pointings[ii][1]+ddec],
                      [pointings[ii][0]-1.*dra,pointings[ii][1]+ddec]]
            [objlst.append(object) for jj in range(len(points))]
            npsrc = npsrc + 5 
        if name == 'hexagon':
            points = [[pointings[ii][0]+dra/2.,pointings[ii][1]],
                      [pointings[ii][0]+dra/4.,pointings[ii][1]+ddec/2.],
                      [pointings[ii][0]-dra/4.,pointings[ii][1]+ddec/2.],
                      [pointings[ii][0]-dra/2.,pointings[ii][1]],
                      [pointings[ii][0]-dra/4.,pointings[ii][1]-ddec/2.],
                      [pointings[ii][0]+dra/4.,pointings[ii][1]-ddec/2.]]
            [objlst.append(object) for jj in range(len(points))]
            npsrc = npsrc + 6 
        print >> fileout, "p%i" % (ii+1)
        stot = len(pointings)*len(points)
        for jj in range(len(points)):
            npoints = npoints + 1
            print >> fileout, points[jj][0], points[jj][1]
            csep = ','
            if npoints == stot:
                csep = ''
            print >> jsonout, json.dumps({"count": cnt, "seqtot":stot, "seqnum":npoints,
            "expType":exptype, "object":objlst[jj], "filter":filter, "seqid":seqid,
            "RA":points[jj][0], "dec":points[jj][1], "expTime":dit}, indent=4, separators=(',', ': '))+csep

    print >> jsonout, ']'    
    fileout.close()
    jsonout.close()
    print 'Total exposures : ',npoints
    print 'Total elapsed time [h] = ', npoints*(dit+ovr)/3600.
    print 'Total on-source time [s,h] = ', npsrc*dit,npsrc*dit/3600.

    ###################################
    #Get the footprints that arise from all the dither/tile combinations,
    #as well as the individual pointing coordinates and plot them together using 
    #opacity to show the deeper areas of observation.
    ###################################
    fig, ax = plt.subplots(figsize=(12,10))

    iis = 0
    for ii in range(len(pointings)):
        point_ra = pointings[ii][0]
        point_dec = pointings[ii][1]    
    
        #print point_ra, point_dec
        points_x, points_y, collection = draw_footprint(point_ra,point_dec,chip_x,gap_sht,iis=iis)
        iis = iis + 1
        if iis == len(sky_coords):
            iis = 0
    
        for patches in collection:
            ax.add_collection(patches)

        ax.plot(points_x,points_y,'k,')
    #Uncomment the line below if you want the pointing numbers output to the plot
        #ax.annotate('%i' % (ii+1),(pointings[ii][0],pointings[ii][1]))

    #Total number of telescope hits on the fields
    #print "Total hits = %i" % (len(hits_ra)/60)
    hits_ra1 = []
    hits_ra0 = []
    hits_dec0 = []
    hits_dec1 = []
    for ii in range(len(hits_ra)):
        hits_ra0.append(hits_ra[ii][0])
        hits_ra1.append(hits_ra[ii][1])
        hits_dec0.append(hits_dec[ii][0])
        hits_dec1.append(hits_dec[ii][1])

    pcheck_ra = np.linspace(np.min(hits_ra0),np.max(hits_ra1),1e4)
    pcheck_dec = np.linspace(np.min(hits_dec0),np.max(hits_dec1),1e4)

    counts = []

    #############################
    #Probe the data, if requested. This indicates how much exposure time on gets along the collapsed
    #RA and Dec directions, for each probe. This option increases the execution time significantly,
    #so should probably only be used once the coverage plot looks good. Trial and error without probes, then
    #probe when you think the strategy is good to go. 
    #############################
    if probe:
        print "Probing coverage..."
#         for ii in range(len(probes)):
#             cnt_ra = []
#             cnt_dec = []
#             cnt_ra,cnt_dec = probecalc(probes,pcheck_ra,pcheck_dec,hits_ra0,hits_ra1,
#             hits_dec0,hits_dec1,ii)
# 
#             counts.append([cnt_ra,cnt_dec])
        # Number of CPUs (threads)
        ncpu = cpu_count()
        njobs = min(ncpu,len(probes))
        print 'njobs = ',njobs
        counts = Parallel(n_jobs=njobs)(delayed(probecalc)(probes,pcheck_ra,pcheck_dec,hits_ra0,hits_ra1,
            hits_dec0,hits_dec1,ii) for ii in range(len(probes)))
        counts = np.array(counts)
        
        ra0_chk = probes[0][0]+1.
        ra1_chk = probes[0][0]-1.
        print 'Probe 0: ',ra0_chk,ra1_chk 
    
        mask = np.where(np.logical_and(pcheck_ra >= ra1_chk,pcheck_ra <= ra0_chk))
        #print counts[0][0][mask]
        print 'Mean probe0 exptime = ',dit*np.mean(counts[0][0][mask]),dit*np.std(counts[0][0][mask],ddof=1)


        ra0_chk = probes[1][0]+1.
        ra1_chk = probes[1][0]-1.
        print 'Probe 1:',ra0_chk,ra1_chk 
    
        mask = np.where(np.logical_and(pcheck_ra >= ra1_chk,pcheck_ra <= ra0_chk))
        #print counts[0][0][mask]
        print 'Mean probe1 exptime = ',dit*np.mean(counts[1][0][mask]),dit*np.std(counts[1][0][mask],ddof=1)


    ###########################################
    #Everything below is plotting the output.
    ###########################################

    #Plot the predicted shell of ngc3923 (optional)
    pa = 46.
    theta = np.linspace(0,2*np.pi,1e5)
    r = np.arctan(210.e3/20.e6)*180./np.pi
    b = r*0.9
    #print r
    y = r*np.sin(theta)
    x = b*np.cos(theta)
    #x = target_ra-r*np.cos(theta)/np.cos(y*np.pi/180.)
    xp = ngc3923_ra - (x*np.cos((pa)*np.pi/180.) - y*np.sin((pa)*np.pi/180.))
    yp = ngc3923_dec + ( x*np.sin((pa)*np.pi/180.) + y*np.cos((pa)*np.pi/180.))
    #print r, target_ra, target_dec
    #print np.min(x), np.max(x)
    #print np.min(y), np.max(y)

    ax.plot(xp,yp,'r--')

    #Plot the positions of the probes with red dots (even if not calculated), and dashed lines
    #in the RA/Dec directions that, if desired, indicate where the exposure times are calculated.
    for ii in range(len(probes)):
        ax.plot([xlim[0],xlim[1]],[probes[ii][1],probes[ii][1]],'k--')
        ax.plot([probes[ii][0],probes[ii][0]],[ylim[0],ylim[1]],'k--')
        ax.plot([probes[ii][0]],[probes[ii][1]],'ro',ms=5)
        ax.annotate("Probe %i" % (ii), xy=(probes[ii][0],probes[ii][1]),color='red')

    #Plot the position of any targets of interest with orange triangles
    for ii in range(len(gal_coords)):
        ax.plot([gal_coords[ii][0]],[gal_coords[ii][1]],'^',color='orange',ms=7)

    #Plot the position of bright stars with red stars
    for ii in range(len(star_coords)):
        ax.plot([star_coords[ii][0]],[star_coords[ii][1]],'r*',ms=10)

    #Plot the position of the target with a yellow star
    ax.plot([ngc3923_ra],[ngc3923_dec],'y*',ms=10)

    ax.set_xlim(xlim[1],xlim[0])
    ax.set_ylim(ylim[0],ylim[1])
    ax.set_xlabel(r'RA [deg]')
    ax.set_ylabel(r'Dec [deg]')

    plt.savefig('%s_dithering.pdf' % outroot)

    #Plot the probe results, if requested
    if probe:
        plt.figure(figsize=(10,10))
        cnt = 0
        for ii in range(len(probes)):
            cnt = cnt + 1
            if cnt < 10:
                plt.subplot('%i%i%i' % (len(probes),2,cnt))
                plt.plot(pcheck_ra,counts[ii][0]*dit,'b')
                plt.xlim(xlim[1],xlim[0])
                plt.xlabel(r'RA [deg]')
                plt.ylabel(r'Exp. Time [s]')
                plt.annotate("Probe %i" % (ii+1),xy=(0.1,0.9),xycoords='axes fraction')

            cnt = cnt + 1
            if cnt < 10:
                plt.subplot('%i%i%i' % (len(probes),2,cnt))
                plt.plot(pcheck_dec,counts[ii][1]*dit,'b')
                plt.xlim(ylim[0],ylim[1])
                plt.xlabel(r'Dec [deg]')
                plt.ylabel(r'Exp. Time [s]')

        plt.savefig('%s_probes.pdf' % outroot)

    if display:
        plt.show()
    print 'Done'
