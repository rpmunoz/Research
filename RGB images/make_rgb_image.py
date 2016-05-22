#!/usr/bin/python

import sys, os, getopt, string
import pyfits
import astropy
import aplpy
import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import skimage.io as io
from skimage import exposure
from PIL import Image
from PIL import ImageEnhance

def main(argv):

	prefix=''
	config_file=''
	filters=('z','g','u')
	stack_name='scabs'
	stack_version='1'

	try:
		opts, args = getopt.getopt(argv,"hp:c:f:",["prefix=","config=","filters="])
	except getopt.GetoptError:
		print 'make_rgb_image.py -p <prefix> -c <configuration_file> -f <filters>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'make_rgb_image.py -p <prefix> -c <configuration_file> -f <filters>'
			sys.exit()
		elif opt in ("-p", "--prefix"):
			prefix = arg
		elif opt in ("-c", "--config"):
			config_file = arg
		elif opt in ("-f", "--filters"):
			filters = string.split(arg,',')

	print 'Prefix path is "', prefix
	print 'Configuration file is "', config_file

	config_data = np.loadtxt(config_file, dtype={'names': ('tile', 'filter', 'image', 'weight'), 'formats': ('S10', 'S10', 'S50', 'S50')})
#	gv_sort=np.argsort(config_data['filter'])[::-1]
#	config_data=config_data[gv_sort]
#	print config_data

	tile_uniq=np.unique(config_data['tile'])
	filter_uniq=np.unique(config_data['filter'])

	print tile_uniq
	print filter_uniq

	# stack_dir='/Volumes/Q6/NGFS/DECam/stacks'
	# stack_tile=['1','4'] #,'2','3','4','5','6','7','10','13']
	# stack_tile_ref='1'
	# stack_filter=['i','g','u']
	# stack_filter_ref='i'
	# stack_version='4'

	# stack_im_file=['ss_fornax_tileX_i_long.003.fits','ss_fornax_tileX_g_long_ALIGNi.003.fits','ss_fornax_tileX_u_long_ALIGNi.003.fits']
	# stack_weight_file=['ss_fornax_tileX_i_long.003.WEIGHT.fits','ss_fornax_tileX_g_long_ALIGNi.003.WEIGHT.fits','ss_fornax_tileX_u_long_ALIGNi.003.WEIGHT.fits']
	# stack_mask_file=['ss_fornax_tileX_i_long.003.MASK.fits','ss_fornax_tileX_g_long_ALIGNi.003.MASK.fits','ss_fornax_tileX_u_long_ALIGNi.003.MASK.fits']

	for i in range(len(tile_uniq)):

		stack_im_file=[prefix+'/'+config_data['image'][np.where( (config_data['tile'] == tile_uniq[i]) & (config_data['filter'] == f) )][0] for f in filters]
		stack_weight_file=[prefix+'/'+config_data['weight'][np.where( (config_data['tile'] == tile_uniq[i]) & (config_data['filter'] == f) )][0] for f in filters]
		stack_rgb_file=prefix+'/'+stack_name+'_TILE'+tile_uniq[i]+'_FILTERS'+string.join(filters,'')+'.fits'
		stack_rgb_limit=np.zeros((3,2), dtype=np.float32)
		stack_filter=filters
		#gv1=np.where( (config_data['tile'] == tile_uniq[i]) & (config_data['filter'] == filters[0]) )
		#gv1=np.where( (config_data['tile'] == tile_uniq[i]) & (config_data['filter'] == filters[0]) )
		 # & ( (config_data['filter'] == filters[0]) | (config_data['filter'] == filters[1]) | (config_data['filter'] == filters[2]) ) )
		#gv_sort=np.argsort(config_data[gv_tile]['filter'])[::-1]

		#im_file=  config_data['image'][gv_tile][np.where( (config_data['filter'][gv_tile] == filters[i]) )] for i in range(len(filters))
		#print im_file

		#stack_im_file=   [prefix+im_file for im_file in config_data[gv]]
		#stack_weight_file=stack_weight_file_full[i]
		#stack_mask_file=stack_mask_file_full[i]
		#stack_rgb_file=stack_rgb_file_full[i]
		#stack_rgb_limit=np.zeros((3,2), dtype=np.float32)

	# stack_im_file_full = [[prefix+'/'+im_file.replace('tileX','tile'+im_tile) for im_file in stack_im_file] for im_tile in stack_tile]
	# stack_weight_file_full = [[prefix+'/'+im_file.replace('tileX','tile'+im_tile) for im_file in stack_weight_file] for im_tile in stack_tile]
	# stack_mask_file_full = [[prefix+'/'+im_file.replace('tileX','tile'+im_tile) for im_file in stack_mask_file] for im_tile in stack_tile]
	# stack_rgb_file_full=[prefix+'/ngfs_tile'+im_tile+'_rgb.fits' for im_tile in stack_tile]

	# for i in range(len(stack_im_file_full)):

	# 	stack_im_file=stack_im_file_full[i]
	# 	stack_weight_file=stack_weight_file_full[i]
	# 	stack_mask_file=stack_mask_file_full[i]
	# 	stack_rgb_file=stack_rgb_file_full[i]
	# 	stack_rgb_limit=np.zeros((3,2), dtype=np.float32)

	#	if not ( (im_tile=='1') | (im_tile=='4') ):
	#		stack_im_file=stack_im_file[0:2]
	#		stack_weight_file=stack_weight_file[0:2]
	#		stack_filter=['i','g+i','g']
	#	else:
	#		stack_filter=stack_filter_orig
		
		hist_nbin=200
		hist_percentile=[0.25,99.5] #[0.25,99.8] #[0.25,99.5]  #([0.25,99.5],[0.25,99.55],[0.22,99.8])
		
		hdulist = pyfits.open(stack_im_file[0])
		im_h=hdulist[0].header
		hdulist.close()
		
		nx = int(im_h['NAXIS1'])
		ny = int(im_h['NAXIS2'])
		im_data_cube = np.zeros((3, ny, nx), dtype=np.float32)
		
	#	for f in stack_im_file:
	#		if not os.path.exists(f):
	#			raise Exception("File does not exist : " + f)
		
		if not os.path.exists(stack_rgb_file):
		
			print '\nCreating rgb cube ', stack_rgb_file
			for j in range(len(stack_filter)):
		
				print '\nProcessing image ', stack_im_file[j], ' - filter ', stack_filter[j]
				im_file=stack_im_file[j]
				weight_file=stack_weight_file[j]
				#mask_file=stack_mask_file[j]
			
				if os.path.exists(im_file):
					print '\nReading image file ', im_file
					hdulist = pyfits.open(im_file)
					im_data=hdulist[0].data
					im_h=hdulist[0].header
					hdulist.close()
			
					print 'Reading weight file ', weight_file
					hdulist = pyfits.open(weight_file)
					weight_data=hdulist[0].data
					hdulist.close()
			
					bv_weight = (weight_data==0.)
					im_data[bv_weight]=np.nan
			
					print 'Image size along X-axis ', im_h['NAXIS1']
					print 'Image size along Y-axis ', im_h['NAXIS2']
			
					ypad = ny - im_data.shape[0]
					xpad = nx - im_data.shape[1]
					pad_width = ((0, ypad), (0, xpad))

					im_data_pad = np.pad(im_data, pad_width, mode='constant', constant_values=[np.nan])
					im_data_cube[j,:,:]=im_data_pad
				else:
					print 'The image file does not exists ', im_file
		
					nim_data = np.empty((ny, nx), dtype=np.float32)
					nim_data[:] = np.nan
					try:
						gv = stack_tile.index(stack_tile_ref)
						im_file=stack_im_file_full[gv][j]
						weight_file=stack_weight_file_full[gv][j]
						mask_file=stack_mask_file_full[gv][j]

						print '\nReading image file ', im_file
						hdulist = pyfits.open(im_file)
						im_data=hdulist[0].data
						hdulist.close()
			
						print 'Reading weight file ', weight_file
						hdulist = pyfits.open(weight_file)
						weight_data=hdulist[0].data
						hdulist.close()
			
						print 'Reading mask file ', mask_file
						hdulist = pyfits.open(mask_file)
						mask_data=hdulist[0].data
						hdulist.close()

						gv = np.logical_and(weight_data>0,mask_data==0)
				
						if np.count_nonzero(gv)>1:
							sky_data=im_data[gv]
							hist_limit= np.abs(np.percentile(sky_data, 0.001))
							hist_xmin=-1.*hist_limit
							hist_xmax=1.*hist_limit
							hist, bin_edges = np.histogram( sky_data, bins=np.linspace(hist_xmin, hist_xmax, hist_nbin), range=(hist_xmin, hist_xmax))
							plt.bar(bin_edges[:-1], hist, width = bin_edges[1]-bin_edges[0], linewidth=0., log=True)
							plt.xlim(hist_xmin, hist_xmax)
							plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
							plt.xlabel('Flux')
							plt.ylabel('Number count')
							plt.savefig(stack_dir+'/ngfs_tile'+stack_tile_ref+'_histogram_sky.pdf')

							weight_file=stack_weight_file[0]
							print 'Reading weight file ', weight_file
							hdulist = pyfits.open(weight_file)
							weight_data=hdulist[0].data
							hdulist.close()

							print 'Random sample from the reference image'
							gv=(weight_data>0)
							nim_data[gv]=np.random.choice(sky_data, np.count_nonzero(gv))
							im_data_cube[j,:,:]=nim_data

					except ValueError:
						print 'Adding gaussian model'
						im_data_cube[j,:,:]= 6. * np.random.randn(ny, nx)
						im_data_cube[j,:,:][bv_weight]=np.nan

			
			print 'Saving the rgb cube file ', stack_rgb_file
			pyfits.writeto(stack_rgb_file, im_data_cube, header=im_h)
		

		im_rgb_file=stack_rgb_file.replace('.fits','_asinh_v'+stack_version+'.jpg')
		if not os.path.exists(im_rgb_file):

			print "Reading the RGB fits cube file: ", stack_rgb_file		
			hdulist = pyfits.open(stack_rgb_file)
			im_data_cube=hdulist[0].data
			im_h_cube=hdulist[0].header
			hdulist.close()

			try:
				stack_rgb_limit=stack_rgb_limit_ref
			except:	
				print '\nComputing the RGB limits using the actual image'

				w, h = 2*matplotlib.figure.figaspect(1.2)
				fig = plt.figure(figsize=(w,h))
				for j in range(len(stack_filter)):
					print '\nProcessing filter ', stack_filter[j]
					im_data=im_data_cube[j,:,:]
					gv=np.isfinite(im_data)
		
					if np.count_nonzero(gv)>1:
		
						if os.path.exists(stack_im_file[j]):
		
							stack_rgb_limit[j,:]= np.percentile(im_data[gv], hist_percentile)  #[plot_xmin, plot_xmax]
							if stack_rgb_limit[j,0]==stack_rgb_limit[j,1]:
								print 'The data seems to contain a constant value. Filter '+stack_filter[j]
								continue
		
							hist_xmin=np.amin(im_data[gv])
							hist_xmax=np.amax(im_data[gv])
			
							print 'Percentiles for computing RGB min and max ', hist_percentile
							print 'Histogram min and max ', hist_xmin, hist_xmax
							print 'RGB image min and max ', stack_rgb_limit[j,:]
			
			#hist_min=np.nanmin(im_data)
			#hist_max=np.nanmax(im_data)
			#fig = plt.figure()
			#ax = fig.add_subplot(1,1,1,)
			#n, bins, patches = ax.hist( np.ravel(im_data), bins=2., range=(hist_min, hist_max), histtype='bar')
			
							hist, bin_edges = np.histogram( im_data, bins=np.linspace(hist_xmin, hist_xmax, hist_nbin), range=(hist_xmin, hist_xmax))
				
			#	ax = fig.add_subplot(2,3,1+2*i,)
							plt.subplot(3,2,1+2*j)
							plt.bar(bin_edges[:-1], hist, width = bin_edges[1]-bin_edges[0], linewidth=0., log=True)
							plt.xlim(hist_xmin, hist_xmax)
							plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
			#	ax.set_yscale('log')
							plt.title('Tile '+stack_tile[i]+' - '+stack_filter[j])
							plt.xlabel('Flux')
							plt.ylabel('Number count')
			
							if stack_filter[j]=='i':
								hist, bin_edges = np.histogram( im_data, bins=np.linspace(stack_rgb_limit[j,0], stack_rgb_limit[j,1], hist_nbin), range=stack_rgb_limit[j,:] )
								stack_rgb_ratio_ref= [ hist[0]*1./np.amax(hist), hist[-1]*1./np.amax(hist) ]
								gv_max=np.argmax(hist)
								stack_rgb_limit_ratio_ref= (bin_edges[gv_max]-stack_rgb_limit[j,0])*1./(stack_rgb_limit[j,1]-stack_rgb_limit[j,0])
								print 'stack_rgb_ratio_ref ', stack_rgb_ratio_ref
								print 'stack_rgb_limit_ratio_ref ', stack_rgb_limit_ratio_ref
							else:
			#		if stack_filter[i]=='u': stack_rgb_ratio=[ stack_rgb_ratio_ref[0]**0.25, stack_rgb_ratio_ref[1] ]
			#		else: stack_rgb_ratio=stack_rgb_ratio_ref
								stack_rgb_ratio=stack_rgb_ratio_ref
								print 'stack_rgb_ratio ', stack_rgb_ratio
			
								delta=stack_rgb_limit[j,1]-stack_rgb_limit[j,0]
								if stack_filter[j]=='u':
									stack_rgb_limit[j,0] -= delta/8.
									stack_rgb_limit[j,1] += 2*delta
								else:
									stack_rgb_limit[j,0] -= delta/8.
									stack_rgb_limit[j,1] += delta/4.
			
								print "Guess RGB image min and max ", stack_rgb_limit[j,:]
						
								hist, bin_edges = np.histogram( im_data, bins=np.linspace(stack_rgb_limit[j,0], stack_rgb_limit[j,1], 2*hist_nbin), range=stack_rgb_limit[j,:] )
								gv_max=np.argmax(hist)
			#		stack_rgb_limit[i,:]= [ bin_edges[ np.argmin( np.abs(hist[0:gv_max]*1./np.amax(hist) - stack_rgb_ratio[0]) )], bin_edges[ gv_max + np.argmin( np.abs(hist[gv_max:-1]*1./np.amax(hist) - stack_rgb_ratio[1]) ) ] ]
								gv_limit_max=gv_max + np.argmin( np.abs(hist[gv_max:-1]*1./np.amax(hist) - stack_rgb_ratio[1]) )
								gv_limit_min=np.argmin( np.abs( (bin_edges[gv_max]- bin_edges[0:gv_max])*1./(bin_edges[gv_limit_max]-bin_edges[0:gv_max]) - stack_rgb_limit_ratio_ref) )
								stack_rgb_limit[j,:]=bin_edges[[gv_limit_min,gv_limit_max]]
								print "Computed RGB limit ", stack_rgb_limit[j,:]
		#						print "New stack_rgb_ratio ", hist[gv_limit_min]*1./hist[gv_max], hist[gv_limit_max]*1./hist[gv_max]
		
						else:
							print 'Computing the rgb limit using the reference tile'
		
							gv_tile = stack_tile.index(stack_tile_ref)
							gv_filter = stack_filter.index(stack_filter_ref)
							hdulist = pyfits.open(stack_rgb_file_full[gv_tile])
							im_h=hdulist[0].header
							hdulist.close()
		
							stack_rgb_limit[j,:]=np.asarray(im_h['RGB_'+stack_filter[j]].split(',')).astype(np.float)
							delta=stack_rgb_limit[j,1]-stack_rgb_limit[j,0]
							stack_rgb_limit[j,0] -= delta/4.
							stack_rgb_limit[j,1] += delta/4.
		
							hist, bin_edges = np.histogram( im_data, bins=np.linspace(stack_rgb_limit[j,0], stack_rgb_limit[j,1], hist_nbin), range=stack_rgb_limit[j,:] )
							gv_max=np.argmax(hist)
		
							stack_rgb_limit[j,1]= np.asarray(im_h['RGB_'+stack_filter[j]].split(',')).astype(np.float)[1]/np.asarray(im_h['RGB_'+stack_filter_ref].split(',')).astype(np.float)[1]*stack_rgb_limit[gv_filter,1]
							stack_rgb_limit[j,0]= bin_edges[ np.argmin( np.abs( (bin_edges[gv_max]- bin_edges[0:gv_max])*1./(stack_rgb_limit[j,1]-bin_edges[0:gv_max]) - stack_rgb_limit_ratio_ref) ) ]
							print "Computed RGB limit ", stack_rgb_limit[j,:]
		#					stack_rgb_limit[j,:]=np.asarray(im_h['RGB_'+stack_filter[j]].split(',')).astype(np.float)
							
						hist, bin_edges = np.histogram( im_data, bins=np.linspace(stack_rgb_limit[j,0], stack_rgb_limit[j,1], hist_nbin), range=stack_rgb_limit[j,:] )
			
			#	ax = fig.add_subplot(2,3,1+2*i+1,)
		
						plt.subplot(3,2,1+2*j+1)
						plt.bar(bin_edges[:-1], hist, width = bin_edges[1]-bin_edges[0], linewidth=0., log=True)
						plt.xlim(stack_rgb_limit[j,0], stack_rgb_limit[j,1])
						plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
			#	ax.set_yscale('log')
						plt.title('Tile '+stack_tile[i]+' - '+stack_filter[j])
						plt.xlabel('Flux')
						plt.ylabel('Number count')
		
					else:
						print '\nNo valid pixels for filter '+stack_filter[j]
			else:
				print '\nReading the RGB limits from the reference tile'

			if stack_tile[i]==stack_tile_ref:
				stack_rgb_limit_ref=stack_rgb_limit

			print 'Updating the rgb cube file ', stack_rgb_file

			for j in range(len(stack_filter)):
				print "\nFilter "+stack_filter[j]
				print stack_rgb_limit[j,:]
				im_h_cube['RGB_'+stack_filter[j]]= ','.join(np.char.mod('%.2f', stack_rgb_limit[j,:]))

			pyfits.writeto(stack_rgb_file, im_data_cube, header=im_h_cube, clobber=True)
		
			plt.tight_layout()
			plt.savefig(stack_dir+'/ngfs_tile'+stack_tile[i]+'_histogram_v'+stack_version+'.pdf')
			plt.close(fig)
		
			print "stack_rgb_limit: \n", stack_rgb_limit
			
			im_rgb_file=stack_rgb_file.replace('.fits','_asinh_v'+stack_version+'.jpg')
			print 'Creating RGB image file ', im_rgb_file
			aplpy.make_rgb_image(stack_rgb_file, im_rgb_file, stretch_r='arcsinh', stretch_g='arcsinh', stretch_b='arcsinh', vmin_r=stack_rgb_limit[0,0], vmin_g=stack_rgb_limit[1,0], vmin_b=stack_rgb_limit[2,0], vmax_r=stack_rgb_limit[0,1], vmax_g=stack_rgb_limit[1,1], vmax_b=stack_rgb_limit[2,1], vmid_r=-0.07, vmid_g=-0.07, vmid_b=-0.07, make_nans_transparent=True, embed_avm_tags=True)

	#		im=io.imread(im_rgb_file)
	#		exposure.rescale_intensity(im, out_range=(30, 255))
	#		io.imsave(im_rgb_file.replace('.jpg','_rescale.jpg'), im)

	#		im=Image.open(im_rgb_file)
	#		enh = ImageEnhance.Contrast(im)
	#		im = enh.enhance(1.6)
	#		enh = ImageEnhance.Brightness(im)
	#		im = enh.enhance(0.8)
	#		im_rgb_file=stack_rgb_file.replace('.fits','_asinh_v1_enh.jpg')
	#		im.save(im_rgb_file.replace('.jpg','_brightness.jpg'), "JPEG", quality=90, optimize=True, progressive=True)

	#		im_rgb_file=stack_rgb_file.replace('.fits','_linear_v'+stack_version+'.jpg')
	#		print 'Creating RGB image file ', im_rgb_file
	#		aplpy.make_rgb_image(stack_rgb_file, im_rgb_file, stretch_r='linear', stretch_g='linear', stretch_b='linear', vmin_r=stack_rgb_limit[0,0], vmin_g=stack_rgb_limit[1,0], vmin_b=stack_rgb_limit[2,0], vmax_r=stack_rgb_limit[0,1], vmax_g=stack_rgb_limit[1,1], vmax_b=stack_rgb_limit[2,1], make_nans_transparent=True, embed_avm_tags=True)

			


if __name__ == "__main__":
   main(sys.argv[1:])
