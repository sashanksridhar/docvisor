import pandas as pd
import cv2
import os
from tqdm.contrib.concurrent import process_map
import tqdm

df = pd.read_csv(("E:\\streetLights\\GPS\\sample1.csv"))
def extract_images(point):

    path = "E:\\streetLights\\Data\\29thDecember\\day\\inputs"
    dayFile = "GH012684_Hero7 Black-GPS5.csv"
    dayFile = dayFile.split(".")[0].split("_")[0] + ".avi"
    cap = cv2.VideoCapture(os.path.join(path, dayFile))

    cts_day = df.loc[point, "cts_x"]

    count = df.loc[point, "Unnamed: 0"]

    cap.set(cv2.CAP_PROP_POS_MSEC, cts_day)

    success, image = cap.read()

    oppath = "E:\\streetLights\\Data\\29thDecember\\day\\newMerges"

    cv2.imwrite(oppath + "/%d_x.jpg" % count, image)

    nightFile = "GH012691_Hero7 Black-GPS5.csv"
    nightFile = nightFile.split(".")[0].split("_")[0] + ".avi"
    cap = cv2.VideoCapture(os.path.join(path, nightFile))

    cts_night = df.loc[point, "cts_y"]

    cap.set(cv2.CAP_PROP_POS_MSEC, cts_night)

    success, image = cap.read()

    cv2.imwrite(oppath + "/%d_y.jpg" % count, image)
    return

if __name__ == '__main__':
    process_map(extract_images, [point for point in range(len(df))], chunksize=1)



