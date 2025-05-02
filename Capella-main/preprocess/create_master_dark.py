
import numpy as np
from astropy.io import fits
import os
from astropy import units as u
from astropy.nddata import CCDData
from ccdproc import Combiner

#RAW_DARK_DIR = os.environ['CAPELLA_RAW']
#MASTER_DARK_DIR = os.path.join( os.environ['CAPELLA_PROC'], 'darks' )

#RAW_DARK_DIR = 'C:\\Users\\User\\Desktop\\blinov\\Capella_data\\raw'
#MASTER_DARK_DIR = 'C:\\Users\\User\\Desktop\\blinov\\Capella_data\\processed'

RAW_DARK_DIR = '/home/alexia/Desktop/blinov/Capella_data/raw'
MASTER_DARK_DIR = '/home/alexia/Desktop/blinov/Capella_data/processed'

class Image():
    def __init__(self, fits_path):
        self.full_path = fits_path
        self.raw_data  = None
        self.header    = None
        self.data_g    = None
        self.data_r    = None
        self.data_b    = None
        self.exposure  = None

    def read_fits(self):
        print("Reading ", self.full_path)
        with fits.open(self.full_path) as hdul:
            self.header   = hdul[0].header

            if self.header['IMAGETYP'] != 'Dark Frame':
                print(self.full_path, " doesn't seem to be a dark frame")
                exit(0)

            self.exposure = self.header['EXPTIME']

            # normalizing data by exposure time
            self.raw_data = hdul[0].data / float(self.exposure)

    def write_fits(self, data, fits_path):
        hdu = fits.PrimaryHDU(data)
        hdul = fits.HDUList([hdu])
        hdul.writeto(fits_path)

    def split_channels(self):
        g1 = self.raw_data[::2, 1::2]
        g2 = self.raw_data[1::2, ::2]
        self.data_g = np.add(g1, g2)
        self.data_b = self.raw_data[::2, ::2]
        self.data_r = self.raw_data[1::2, 1::2]
    
    def create_CCDdata(self):
        self.ccd_g = CCDData(self.data_g, unit=u.adu)
        self.ccd_b = CCDData(self.data_b, unit=u.adu)
        self.ccd_r = CCDData(self.data_r, unit=u.adu)

def get_filenames():
    """ 
    Checks the RAW_DARK_DIR folder for subfolders in YYYY_MM_DD formats
    Then looks for these subfolders in MASTER_DARK_DIR 
      if some of them are missing it will find the fits files and create the master darks
      for corresponding dates 
    """

    darks_to_proc = []
    days_raw    = os.listdir(RAW_DARK_DIR)
    days_master = os.listdir(MASTER_DARK_DIR)
    for day in days_raw:
        if day not in days_master:
            files = list( filter(lambda x: x.startswith("Dark") and x.endswith(".fit"), os.listdir(os.path.join(RAW_DARK_DIR, day) ) ) )
            darks_files = list( map(lambda x: os.path.join(RAW_DARK_DIR, day, x), files) )
            darks_to_proc.append([day, darks_files])
    return darks_to_proc

if __name__ == "__main__":
    darks_to_proc = get_filenames()

    for dark_info in darks_to_proc:
        day, darks_files = dark_info

        images_g = []
        images_b = []
        images_r = []
        for dark_file in darks_files:
            img = Image(dark_file)
            img.read_fits()
            img.split_channels()
            img.create_CCDdata()
            images_g.append(img.ccd_g)
            images_b.append(img.ccd_b)
            images_r.append(img.ccd_r)

        combiner_g = Combiner(images_g)
        combiner_b = Combiner(images_b)
        combiner_r = Combiner(images_r)

        combined_median_g = combiner_g.median_combine()
        combined_median_b = combiner_b.median_combine()
        combined_median_r = combiner_r.median_combine()

        OUT_FOLDER = os.path.join(MASTER_DARK_DIR, day)
        if not os.path.exists(OUT_FOLDER):
            os.makedirs(OUT_FOLDER)

        combined_median_g.write(os.path.join(OUT_FOLDER, 'Dark_g.fits'))
        combined_median_b.write(os.path.join(OUT_FOLDER, 'Dark_b.fits'))
        combined_median_r.write(os.path.join(OUT_FOLDER, 'Dark_r.fits'))
