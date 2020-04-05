from download_sample_data import download_lung1_sample
import os
from dcmrtstruct2nii import dcmrtstruct2nii
from glob import glob
import pydicom
import nibabel as ni
import matplotlib.pyplot as plt
import numpy as np


class Opts:
    def __init__(self):
        self.username = None
        self.password = None

def convert_to_nii(path):
    dcmrtstruct2nii('LUNG1-001/LUNG1-001_20190225_CT/scans/3-unknown/resources/secondary/files/1.3.6.1.4.1.40744.29.239341353911714368772597187099978969331-3-2-1mxpufu.dcm', 'LUNG1-001/LUNG1-001_20190225_CT/scans/0-unknown/resources/DICOM/files', path)

def normalize(image):
    # https://stats.stackexchange.com/questions/178626/how-to-normalize-data-between-1-and-1
    image_min = image.min()
    image_max = image.max()
    image = (image - image_min) / (image_max - image_min)
    image = image * 255
    return image.astype(np.int16)
    
def load_images(ct_path, mask_paths):
    # CT
    ct_volume = ni.load(ct_path)
    ct_volume = ct_volume.get_fdata()
    # ct_volume = get_hu_from_pixels(ct_volume)
    ct_volume = normalize(ct_volume)
    ct_volume = ct_volume.transpose(2, 1, 0)
    # Mask
    mask_volumes = []
    for mask_path in mask_paths:
        mask_volume = ni.load(mask_path)
        mask_volume = mask_volume.get_fdata()
        mask_volume = mask_volume.transpose(2, 1, 0)
        mask_volumes.append(mask_volume)

    return ct_volume, mask_volumes

def main(opts):
    ct_volume, mask_volumes = load_images("{}/image.nii.gz".format(opts.patient), glob("{}/mask_*.nii.gz".format(opts.patient)))
    fig = plt.figure(figsize=(15, 15)) #insert settings
    slice_index = 0
    for ct_slice, mask_slice in zip(ct_volume, mask_volumes[0]):
        slice_index += 1
        if slice_index < 60:
            continue
        print("Processing Slice: {}".format(slice_index))

        plt.imshow(ct_slice, cmap='gray', interpolation='none')
        plt.imshow(mask_slice, alpha=0.2, cmap='copper', interpolation='none')

        #save the figure
        plt.show() 




if __name__ == "__main__":
    opts = Opts()
    opts.download_path = '.'
    opts.project_id = 'stwstrategyln1'

    opts.patient = 'LUNG1-001'
    # Download sample data from XNAT
    if not(os.path.isdir(opts.patient)):
        download_lung1_sample(opts)

    convert_to_nii(opts.patient)
    
    main(opts)

