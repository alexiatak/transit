
import numpy as np
import cv2
from astropy.io import fits
import time

fits_path = '/media/caro/lindata/tmp/Capella/Field5-0001.fit'

class Image():
    def __init__(self, fits_path):
        self.full_path = fits_path
        self.raw_data  = None
        self.header    = None
        self.cv2rgb    = None

    def read_fits(self):
        with fits.open(self.full_path) as hdul:
            self.raw_data = hdul[0].data

    def write_fits(self, data, fits_path):
        hdu = fits.PrimaryHDU(data)
        hdul = fits.HDUList([hdu])
        hdul.writeto(fits_path)

    def split_channels(self):
        g1 = self.raw_data[::2, 1::2]
        g2 = self.raw_data[1::2, ::2]
        b  = self.raw_data[::2, ::2]
        r  = self.raw_data[1::2, 1::2]

        self.write_fits(g1, '/media/caro/lindata/tmp/Capella/g1.fits')
        self.write_fits(b, '/media/caro/lindata/tmp/Capella/b.fits')
        self.write_fits(r, '/media/caro/lindata/tmp/Capella/r.fits')
        self.write_fits(g2, '/media/caro/lindata/tmp/Capella/g2.fits')

    def convert_color_png(self):
        rgb = cv2.cvtColor(self.raw_data, cv2.COLOR_BayerBG2BGR) # COLOR_BayerBG2BGR  COLOR_BayerGB2BGR  COLOR_BayerRG2BGR COLOR_BayerGR2BGR
        cv2.imwrite('test.png', rgb)

if __name__ == "__main__":
    im = Image(fits_path)
    im.read_fits()
    im.split_channels()
    im.convert_color_png()


