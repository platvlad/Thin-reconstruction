import PhotoScan as ps
import os

path = 'PhotoScanProjects/P117_1804_MskHighway_2018_04_09_g201b20087_f001/'
mask_path = path + '/Masks'
files = os.listdir(mask_path)

chunk = ps.app.document.chunk
for camera in chunk.cameras:
    photo = camera.photo
    path = photo.path
    slash_index = path.rfind('/')
    file_name = path[slash_index + 1::]
    if file_name in files:
        if camera.mask:
            print(1)
        else:
            print(0)
            mask = ps.Mask()
            mask.load(mask_path + '/' + file_name)
            camera.mask = mask
