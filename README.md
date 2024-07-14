# jwstdestripe

A NIRCam 1/f Noise Removal package

## Features:

- Robustly remove the JWST NIRCam 1/f Noise
- Preserve originall background gradient
- Preserve overall background level
- Subtract row median for each amplifier
- Pixels with zero counts are excluded from calculation
- Point sources are excluded from the median derivation
- Results saved to FITS files

## Installation

``pip install git+https://github.com/wenlong2/jwstdestripe``

## Tutorial & Example

``` Python
from jwstdestripe import destripe as ds

f = 'path/to/cal.fits/file'
a=ds.destripe(f)
newarr, stripe = a.destripe()
```
## Reference
[NIRCam 1/f Noise Removal Methods](https://jwst-docs.stsci.edu/known-issues-with-jwst-data/nircam-known-issues/nircam-1-f-noise-removal-methods#NIRCam1/fNoiseRemovalMethods-1/fsoftwarepackages)