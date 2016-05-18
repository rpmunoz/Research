survey_tile = [ {tile:1, coo:['10:05:12.7','-07:42:28.9']} ]

survey = { ob1:{ target:'NGC3115', filter:'u', tile:[1,1], exptime:[30,300]}, $
	ob2:{ target:'NGC3115', filter:'g', tile:[1,1], exptime:[30,300]}, $
	ob3:{ target:'NGC3115', filter:'r', tile:[1,1], exptime:[30,300]}, $
	ob4:{ target:'NGC3115', filter:'i', tile:[1,1], exptime:[30,300]} } 
n_survey=n_tags(survey)

offset_ra = 4.5 * 10 * [0.,-1.,1./3,1.,-1./3,-2./3,2./3,  7./15,-7./15,-12./15,12./15,-3./15,3./15,6./15,-6./15,-2./15,2./15,4./15,-4./15,9./15,-9./15 ]
offset_dec = 5.8 * 10. * [0.,-1./3,-1.,1./3,1.,2./3,-2./3,  12./15,-12./15,3./15,-3./15,7./15,-7./15,6./15,-6./15,-14./15,14./15,-1./15,1./15,9./15,-9./15 ]
;offset_ra = 4.5 * 10 * [0.,-1.,1./3,1.,-1./3,-2./3,2./3,1./2,-1./2,-5./6,5./6] ;, -1./6,1./6, ]
;offset_dec = 5.8 * 10. * [0.,-1./3,-1.,1./3,1.,2./3,-2./3,5./6,-5./6,1./6,-1./6] ;, 1./2,-1./2 ]
n_dither=4;n_elements(offset_ra)

;for i=0L, n_survey-1 do begin
;	for j=0L, n_dither-1 do begin
for i=0L, n_survey-1 do begin
	seqnum=1
	n_tile=n_elements( survey.(i).tile)
	openw, lun, survey.(i).target+'_'+survey.(i).filter+'_dithers'+strn(n_dither)+'.json', /get_lun
	printf, lun, '['
	for k=0L, n_tile-1 do begin
		for j=0L, n_dither-1 do begin
			if k EQ 0 AND j GT 0 then continue
	
			gv=where(survey_tile.tile EQ survey.(i).tile[k], n_gv)
			if n_gv NE 1 then stop
			tile_ra=ten((survey_tile[gv]).coo[0])*360./24.
			tile_dec=ten((survey_tile[gv]).coo[1])

			dither_dec= tile_dec + offset_dec[j]/3600D
			dither_ra = tile_ra + offset_ra[j]/3600D/cos(dither_dec*!DTOR)

			dither_ra=repstr(string(sixty(dither_ra*24./360), FORMAT='(I0,":",I2,":",F4.1)'), ' ','0')
			dither_dec=repstr(string(sixty(dither_dec), FORMAT='(I0,":",I2,":",F4.1)'), ' ','0')

			printf, lun, ' {'
			printf, lun, '  "count": 1, '
			printf, lun, '  "seqtot": '+strn(n_dither+1)+', '
			printf, lun, '  "seqnum": '+strn(seqnum)+', '
			printf, lun, '  "expType": "object", '
			printf, lun, '  "object": "'+survey.(i).target+'_t'+strn(survey.(i).tile[k])+'_d'+strn(j+1)+(survey.(i).exptime[k] LE 30. ? '_short' : '') +'", '
			printf, lun, '  "filter": "'+survey.(i).filter+'", '
			printf, lun, '  "seqid": "'+survey.(i).filter+'_d'+strn(j+1)+'", '
			printf, lun, '  "RA": "'+dither_ra+'", '
			printf, lun, '  "dec": "'+dither_dec+'", '
			printf, lun, '  "expTime": '+string(survey.(i).exptime[k],FORMAT='(I0)')

			seqnum++
			if j EQ n_dither-1 AND k EQ n_tile-1 then printf, lun, ' }' else printf, lun, ' },'
		endfor
	endfor
	printf, lun, ']'
	free_lun, lun
endfor

cgdelete, /all

offset_ra = 4.5 * 10 * [0.,-1.,1./3,1.,-1./3,-2./3,2./3,  7./15,-7./15,-12./15,12./15,-3./15,3./15,6./15,-6./15,-2./15,2./15,4./15,-4./15,9./15,-9./15 ]
offset_dec = 5.8 * 10. * [0.,-1./3,-1.,1./3,1.,2./3,-2./3,  12./15,-12./15,3./15,-3./15,7./15,-7./15,6./15,-6./15,-14./15,14./15,-1./15,1./15,9./15,-9./15 ]
n_dither=n_elements(offset_ra)
offset_label = string(1+indgen(n_dither),Format='(I0)')

forprint, 1+indgen(n_dither), offset_ra, offset_dec, text=2, format='I3,2X,F5.1,2X,F5.1'
cgwindow, wxsize=800, wysize=800
cgplot, offset_ra, offset_dec, xrange=[60,-60], yrange=[-60,60], psym=2, /window, /xstyle, /ystyle, xtitle='R.A. (arcsec)', ytitle='Dec (arcsec)', xticklen=1., yticklen=1., xgridstyle=1, ygridstyle=1
cgtext, offset_ra-1, offset_dec, offset_label, color='red', /window

end
