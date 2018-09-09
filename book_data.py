import tflearn
from tflearn.data_utils import build_hdf5_image_dataset
dataset_file = 'book_data.txt'
build_hdf5_image_dataset(dataset_file, image_shape=(128, 128), mode='file', output_path='dataset.h5', categorical_labels=True, normalize=True)