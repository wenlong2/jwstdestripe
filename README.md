# jwstdestripe

A NIRCam 1/f Noise Removal package

## Features:

- Robustly remove the JWST NIRCam 1/f Noise
- Preserve original background gradient
- Preserve overall background level
- Subtract row 1/f noise for each amplifier
- With the option to remove column 1/f noise altogether
- Pixels with zero counts are excluded from calculation
- Point sources are excluded from the median calculation
- Results saved to FITS files and new arrays returned

## Installation

``pip install git+https://github.com/wenlong2/jwstdestripe``

## Tutorial & Example

``` Python
from jwstdestripe import destripe

f = 'path/to/cal.fits/file_cal.fits' # only applies to cal.fits
a=destripe.destripe(f)
newarr, stripe = a.destripe(column=False) # default, if remove row noise only
newarr, stripe = a.destripe(column=True) # if remove column noise as well
```
## Reference
[NIRCam 1/f Noise Removal Methods](https://jwst-docs.stsci.edu/known-issues-with-jwst-data/nircam-known-issues/nircam-1-f-noise-removal-methods#NIRCam1/fNoiseRemovalMethods-1/fsoftwarepackages)