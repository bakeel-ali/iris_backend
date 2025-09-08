import numpy as np
import cv2

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def crop_iris_image_color(image: np.ndarray) -> np.ndarray:
    # الكود الكامل لدالة الاقتصاص كما قدمته
    if len(image.shape) == 2:
        non_black_pixels_mask = (image > 0)
    elif len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        non_black_pixels_mask = (gray_image > 0)
    else:
        raise ValueError("Unsupported image format.")

    non_black_y_coords, non_black_x_coords = np.where(non_black_pixels_mask)
    if len(non_black_y_coords) == 0:
        return image # Return original image if no object found

    y_min_obj, x_min_obj = np.min(non_black_y_coords), np.min(non_black_x_coords)
    y_max_obj, x_max_obj = np.max(non_black_y_coords), np.max(non_black_x_coords)

    height_obj, width_obj = y_max_obj - y_min_obj + 1, x_max_obj - x_min_obj + 1
    side_length = max(height_obj, width_obj)
    center_y_obj, center_x_obj = y_min_obj + height_obj // 2, x_min_obj + width_obj // 2
    
    img_height, img_width = image.shape[:2]

    pad_y_before = max(0, side_length // 2 - center_y_obj)
    pad_y_after = max(0, center_y_obj + (side_length - side_length // 2) - img_height)
    pad_x_before = max(0, side_length // 2 - center_x_obj)
    pad_x_after = max(0, center_x_obj + (side_length - side_length // 2) - img_width)

    padding_tuple = ((pad_y_before, pad_y_after), (pad_x_before, pad_x_after))
    if len(image.shape) == 3:
        padding_tuple += ((0, 0),)

    padded_image = np.pad(image, padding_tuple, mode='constant', constant_values=0)
    
    padded_center_y = center_y_obj + pad_y_before
    padded_center_x = center_x_obj + pad_x_before

    y_min_crop, y_max_crop = padded_center_y - side_length // 2, padded_center_y + (side_length - side_length // 2)
    x_min_crop, x_max_crop = padded_center_x - side_length // 2, padded_center_x + (side_length - side_length // 2)

    return padded_image[y_min_crop:y_max_crop, x_min_crop:x_max_crop]