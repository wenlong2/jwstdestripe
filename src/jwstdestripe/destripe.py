from astropy.io import fits
from photutils.background import Background2D
import numpy as np
from astropy.stats import sigma_clipped_stats
from shutil import copyfile

missing_value = np.nan # this convention changed

class destripe:
    def __init__(self, f):
        self.imgfile = f
        hdu = fits.open(f)
        arr = hdu[1].data
        hdr = hdu[1].header
        hdu.close()
        self.arr = arr
        self.hdr = hdr

    def destripe(self, column=False, bgd_scale=25, src_thres=2.5):
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
        idx = np.isnan(self.arr)
        a5[idx] = np.nan
        if column:
            a6, sky = self.jwst_rm2dsky(a5, scale=bgd_scale)
            a7 = self.jwst_mask_src(a6)
            a8 = self.cal_colmedian(a7)
            a5 = a5 - a8
            a4 = a4 + a8
            idx = np.isnan(self.arr)
            a5[idx] = np.nan
        # write results into FITS files
        hdr = self.hdr
        f_out = self.imgfile.replace('.fits', '_sub1of.fits')
        copyfile(self.imgfile, f_out)
        hdu = fits.open(f_out, mode='update')
        hdu[1].data = a5.astype('float32')
        hdu.flush()
        hdu.close()
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

    def cal_colmedian(self, a):
        n = int(a.shape[0])
        cmed = np.nanmedian(a, 0)
        m = np.tile(cmed, (n,1))
        m -= np.nanmedian(m)
        return m

    def jwst_rm2dsky(self, a, scale):
        idx = np.isnan(a)
        sky = Background2D(a, scale).background
        # Convert back to JWST convention
        a[idx] = np.nan
        sky[idx] = np.nan
        return a-sky, sky

    def jwst_mask_src(self, a, threshold=2.5):
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
