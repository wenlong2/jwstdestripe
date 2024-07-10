from astropy.io import fits
from photutils.background import Background2D
import numpy as np
from astropy.stats import sigma_clipped_stats

class destripe:
    def __init__(self, f):
        self.imgfile = f
        hdu = fits.open(f)
        arr = hdu[1].data
        hdr = hdu[1].header
        hdu.close()
        self.arr = arr
        self.hdr = hdr

    def destripe(self, bgd_scale=25, src_thres=2.5):
        # Compute and substract the overall sky gradient first,
        # otherwise a direct row median would change the original
        # sky gradient
        a1, sky = self.jwst_rm2dsky(self.arr, scale=bgd_scale)
        # Mask point sources for more robust results
        a2 = self.jwst_mask_src(a1, threshold=src_thres)
        # Split those four amplifiers
        a3s = self.jwst_split_ampl(a2)
        # Subtract row median for each amplifier
        a4 = self.cal_rowmedian(a3s, a1+np.nan)
        a5 = self.arr - a4
        # fix those no-observation pixels
        idx = self.arr == 0
        a5[idx] = 0
        idx = np.isnan(a5)
        a5[idx] = 0
        # write results into FITS files
        hdr = self.hdr
        f_out = self.imgfile.replace('.fits', '_sub1of.fits')
        fits.writeto(f_out, a5.astype('float32'), header=hdr, overwrite=True)
        f_out = self.imgfile.replace('.fits', '_1of.fits')
        fits.writeto(f_out, a4.astype('float32'), header=hdr, overwrite=True)
        return a5, a4

    def cal_rowmedian(self, amps, a):
        n = int(a.shape[1]/4)
        for i in range(4):
            # Compute row median for each amplifier
            rmed = np.nanmedian(amps[i], 1)
            # Combine the row median into a full array
            a[:,n*i:n*(i+1)] = np.transpose(np.tile(rmed, (n,1)))
        # Subtract an overall median offset of those median values, if any
        a -= np.nanmedian(a)
        return a

    def jwst_rm2dsky(self, a, scale):
        # JWST convention: "0" means no data. Mask them first
        idx = a == 0
        a[idx] = np.nan
        sky = Background2D(a, scale).background
        # Convert back to JWST convention
        a[idx] = 0
        sky[idx] = 0
        return a-sky, sky

    def jwst_mask_src(self, a, threshold=2.5):
        # JWST convention: "0" means no data. Mask them first
        idx = a == 0
        a[idx] = np.nan
        mean, median, std = sigma_clipped_stats(a, maxiters=100)
        idx = np.abs(a-median) > std * threshold
        a[idx] = np.nan
        return a
        
    def jwst_split_ampl(self, a):
        n = int(a.shape[1] / 4)
        a1 = a[:,n*0:n*1]
        a2 = a[:,n*1:n*2]
        a3 = a[:,n*2:n*3]
        a4 = a[:,n*3:n*4]
        return a1, a2, a3, a4 
