import pandas as pd
import json
import uuid
df = pd.read_csv(("E:\\streetLights\\GPS\\common.csv"))

print(df)
#
# df.drop(["GPS (Alt.) [m]_x","GPS (2D speed) [m/s]_x","GPS (3D speed) [m/s]_x", "fix_x", "precision_x", "GPS (Alt.) [m]_y", "GPS (2D speed) [m/s]_y",
#
#          "GPS (3D speed) [m/s]_y", "fix_y", "precision_y"], axis=1, inplace=True)

print(df.count())

jsonDict = []



path = "E:\\streetLights\\Data\\29thDecember\\day\\inputs"

for i in range(len(df)):

    jObj = {}

    jObj["id"] = str(uuid.uuid1())

    count = df.loc[i, "Unnamed: 0"]

    oppath = "E:/streetLights/Data/29thDecember/day/merges"

    jObj["imagePath"] = oppath + "/"+str(count)+"_x.jpg"
    jObj["imagePath2"] = oppath + "/"+str(count)+"_y.jpg"

    outputs = {}

    GPS = {}

    Metrics = {}

    Metrics["Day latitude"] = df.loc[i, 'GPS (Lat.) [deg]']

    Metrics["Day Longitude"] = df.loc[i, 'GPS (Long.) [deg]']
    #
    # Metrics["Night latitude"] = df.loc[i, 'GPS (Lat.) [deg]_y']
    #
    # Metrics["Night Longitude"] =df.loc[i, 'GPS (Long.) [deg]_y']

    Metrics["Speed"] = df.loc[i, 'GPS (3D speed) [m/s]_y']


    GPS["metrics"] = Metrics

    outputs["GPS"] = GPS

    jObj["outputs"] = outputs

    jsonDict.append(jObj)
    print(count)

print(jsonDict)

json_object = json.dumps(jsonDict, indent=4)


with open("E:\\streetLights\\GPS\\sample.json", "w") as outfile:
    outfile.write(json_object)

