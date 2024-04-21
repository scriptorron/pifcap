"""
command line program to convert pifcap internal image format to FITS
"""

import sys
import os.path
import pickle
import glob
import numpy as np
import argparse
import multiprocessing
import time
import datetime
from astropy.io import fits


def convert(input_filename, remove, skip_existing):
    output_filename = input_filename.rsplit(".", maxsplit=1)[0] + ".fits"
    if not(skip_existing and os.path.isfile(output_filename)):
        # convert
        retrials = 20
        while True:
            try:
                with open(input_filename, "rb") as fh:
                    img = pickle.load(fh)
            except EOFError:
                retrials -= 1
                if retrials > 0:
                    time.sleep(0.1)
                else:
                    print(f'ERROR: Can not open {input_filename}', file=sys.stderr)
                    return input_filename
            else:
                break
        array = img["array"]
        format = img["format"]
        metadata = img["metadata"]
        # we expect uncompressed format here
        if format.count("_") > 0:
            raise NotImplementedError(f'got unsupported raw image format {format}')
        if format[0] not in ["S", "R"]:
            raise NotImplementedError(f'got unsupported raw image format {format}')
        # Bayer or mono format
        if format[0] == "S":
            # Bayer pattern format
            BayerPattern = format[1:5]
            bit_depth = int(format[5:])
        else:
            # mono format
            BayerPattern = None
            bit_depth = int(format[1:])
        # left adjust if needed
        if bit_depth > 8:
            bit_pix = 16
            array = array.view(np.uint16)
        else:
            bit_pix = 8
            array = array.view(np.uint8)
        # convert to FITS
        hdu = fits.PrimaryHDU(array)
        hdu.header["BZERO"] = (2 ** (bit_pix - 1), "offset data range")
        hdu.header["BSCALE"] = (1, "default scaling factor")
        hdu.header["ROWORDER"] = ("TOP-DOWN", "Row order")
        hdu.header["INSTRUME"] = (metadata["CameraModel"], "CCD Name")
        hdu.header["EXPTIME"] = (metadata["ExposureTime"]/1e6, "[s] Total Exposure Time")
        hdu.header["DATE-OBS"] = (
            (metadata["DateEnd"] - datetime.timedelta(seconds=metadata["ExposureTime"]/1e6)).isoformat(timespec="milliseconds"),
            "UTC time of observation start"
        )
        hdu.header["DATE-END"] = (metadata["DateEnd"].isoformat(timespec="milliseconds"), "UTC time at end of observation")
        #hdu.header["CCD-TEMP"] = (metadata.get('SensorTemperature', 0), "[degC] CCD Temperature")
        hdu.header["PIXSIZE1"] = (metadata["UnitCellSize"][0] / 1e3, "[um] Pixel Size 1")
        hdu.header["PIXSIZE2"] = (metadata["UnitCellSize"][1] / 1e3, "[um] Pixel Size 2")
        hdu.header["XBINNING"] = (metadata["Binning"][0], "Binning factor in width")
        hdu.header["YBINNING"] = (metadata["Binning"][1], "Binning factor in height")
        hdu.header["XPIXSZ"] = (metadata["UnitCellSize"][0] / 1e3 * metadata["Binning"][0], "[um] X binned pixel size")
        hdu.header["YPIXSZ"] = (metadata["UnitCellSize"][1] / 1e3 * metadata["Binning"][1], "[um] Y binned pixel size")
        hdu.header["FRAME"] = (metadata["FrameType"], "Frame Type")
        hdu.header["IMAGETYP"] = (metadata["FrameType"] + " Frame", "Frame Type")
        hdu.header["GAIN"] = (metadata["AnalogueGain"], "Gain")
        if BayerPattern is not None:
            hdu.header["XBAYROFF"] = (0, "[px] X offset of Bayer array")
            hdu.header["YBAYROFF"] = (0, "[px] Y offset of Bayer array")
            hdu.header["BAYERPAT"] = (BayerPattern, "Bayer color pattern")
        if "SensorBlackLevels" in metadata:
            SensorBlackLevels = metadata["SensorBlackLevels"]
            if len(SensorBlackLevels) == 4:
                # according to picamera2 documentation:
                #   "The black levels of the raw sensor image. This
                #    control appears only in captured image
                #    metadata and is read-only. One value is
                #    reported for each of the four Bayer channels,
                #    scaled up as if the full pixel range were 16 bits
                #    (so 4096 represents a black level of 16 in 10-
                #    bit raw data)."
                # When image data is stored as 16bit it is not needed to scale SensorBlackLevels again.
                # But when we store image with 8bit/pixel we need to divide by 2**8.
                SensorBlackLevelScaling = 2 ** (bit_pix - 16)
                hdu.header["OFFSET_0"] = (SensorBlackLevels[0] * SensorBlackLevelScaling, "[DN] Sensor Black Level 0")
                hdu.header["OFFSET_1"] = (SensorBlackLevels[1] * SensorBlackLevelScaling, "[DN] Sensor Black Level 1")
                hdu.header["OFFSET_2"] = (SensorBlackLevels[2] * SensorBlackLevelScaling, "[DN] Sensor Black Level 2")
                hdu.header["OFFSET_3"] = (SensorBlackLevels[3] * SensorBlackLevelScaling, "[DN] Sensor Black Level 3")
        hdu.header["comment"] = img["comment"]
        hdul = fits.HDUList([hdu])
        # save FITS
        hdul.writeto(output_filename, overwrite=True)
        # remove input if requested
        if remove:
            os.remove(input_filename)
    return input_filename


def main():
    # command line parser
    parser = argparse.ArgumentParser(description='convert pifcap to FITS')
    parser.add_argument('-s', '--skip_existing', action="store_true",
                        help='skip conversion when output exists')
    parser.add_argument('-r', '--remove', action="store_true",
                        help='remove input file after conversion')
    parser.add_argument('-d', '--demon', action="store_true",
                        help='convert existing files, stay running and convert all upcoming new files; exit with CTRL-C')
    parser.add_argument('-j', '--jobs', type=int, default=1,
                        help='number of parallel running conversion jobs (default: 1)')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='verbose messages')
    parser.add_argument('files', metavar="path", default='*.pfc',
                        help='files to convert; accepts "?", "*" and character ranges like "[a-z]" (default "*.pfc")')
    args = parser.parse_args()
    if args.demon:
        print("Demon mode. Exit with CTRL+C.")
    # file lists
    pending_files = list()
    pending_processes = list()
    finished_files = list()
    # multiprocessing pool
    pool = multiprocessing.Pool(processes=args.jobs)
    # demon loop
    while True:
        # start conversion for all new input files
        all_filenames = glob.glob(args.files)
        for fn in all_filenames:
            if (fn not in finished_files) and (fn not in pending_files):
                pending_processes.append(
                    pool.apply_async(
                        convert,
                        kwds={
                            "input_filename": fn,
                            "remove": args.remove,
                            "skip_existing": args.skip_existing,
                        }
                    )
                )
                pending_files.append(fn)
        # tell what is going on
        if args.verbose:
            print(f'{len(pending_processes)} files pending, {len(finished_files)} files converted   ', end='\r')
        # release CPU
        time.sleep(0.1)
        # pending process loop
        while len(pending_processes) > 0:
            still_pending_processes = list()
            for pp in pending_processes:
                if pp.ready():
                    finished_file = pp.get()
                    finished_files.append(finished_file)
                    pending_files.remove(finished_file)
                else:
                    still_pending_processes.append(pp)
            pending_processes = still_pending_processes
            if args.demon:
                # demon mode allows to start more processes before pending are done
                break
            else:
                # non-demon: stay in pending process loop
                if args.verbose:
                    print(f'{len(pending_processes)} files pending, {len(finished_files)} files converted   ', end='\r')
                time.sleep(0.1)
        # non-demon: finished
        if not args.demon:
            break
    print()


if __name__ == '__main__':
    main()
    sys.exit(0)
