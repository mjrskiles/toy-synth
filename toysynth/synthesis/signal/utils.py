import numpy as np

def squish(val, min_val=0, max_val=1):
        return (((val + 1) / 2 ) * (max_val - min_val)) + min_val

def normalize(array: np.ndarray):
    min_val = array.min()
    max_val = array.max()
    range_val = max_val - min_val

    if range_val == 0:
        return np.zeros(array.shape)

    normalized_array = 2 * (array - min_val) / range_val - 1
    return normalized_array

def seconds_to_frames(seconds, sample_rate):
    return int(seconds * sample_rate)

def frames_to_seconds(frames, sample_rate):
    return frames / sample_rate