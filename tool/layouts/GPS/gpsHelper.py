import json
import numpy as np
from PIL import Image,ImageOps
import os
import streamlit as st


class gpsHelper:

    def __init__(self,jsonFilePath):


        if not os.path.exists(jsonFilePath):
            # print(jsonFilePath)
            raise FileNotFoundError

        # valid json file path
        self.jsonFilePath = jsonFilePath

        # load data:
        self.JSONdata = self.loadGPSData(self.jsonFilePath)


        # calculate and store the length of the data for easy retrieval
        self.len = len(self.JSONdata)

        if 'outputs' in self.JSONdata[0]:

            self.models = list(self.JSONdata[0]['outputs'].keys())

            
            self.metric_details = {}

            for model in self.models:
                if "metrics" in self.JSONdata[0]["outputs"][model]:
                    self.metric_details[model] = list(self.JSONdata[0]['outputs'][model]["metrics"].keys())
                    self.metric_details[model].append('None')
                else:
                    self.metric_details[model]=['None']
            
            self.sortedSecIndices = {model:{} for model in self.models}

            
            for model in self.metric_details:
                for metric in self.metric_details[model]:
                    if metric!='None':
                        self.sortedSecIndices[model][metric]= [i[0] for i in sorted(enumerate(self.JSONdata), key=lambda x:x[1]['outputs'][model]['metrics'][metric])]
                    else:
                        self.sortedSecIndices[model][metric] = [i for i in range(len(self.JSONdata))]

        else:

            # case where the user uploads data with only image path and posibly the corresponding ground truth.
            self.models = None
            self.sortedSecIndices = [i for i in range(self.len)]

        

    
    def parseGPSJson(self,dataPath):
        with open(dataPath,'r') as dataFile:
            data = json.load(dataFile)
        return data
    

    def getData(self,index):
        return self.JSONdata[index]
    

    def loadGPSData(self,dataPath):
        data = self.parseGPSJson(dataPath)

        return data

    
    def loadImage(self,index):

        """
        on success : saves PIL image data object into the jsonData with corresponding index & returns numpy array of image 
        on failure : returns -1
        """

        if "image" in self.JSONdata[index]:
            try:
                # im = ImageOps.grayscale(self.JSONdata[index]["image"])
                # imageData = np.asarray(im, dtype=np.uint8)
                imageData = np.asarray(Image.open(self.JSONdata[index]["imagePath"]).resize((480, 480), Image.ANTIALIAS), dtype=np.uint8)
                imageData2 = np.asarray(Image.open(self.JSONdata[index]["imagePath2"]).resize((480, 480), Image.ANTIALIAS), dtype=np.uint8)
                return [imageData, imageData2]
            except:
                st.warning('Error in loading image array. ')
                return -1
        


        imagePath = self.JSONdata[index]["imagePath"]

        imagePath2 = self.JSONdata[index]["imagePath2"]

        try:
            im = Image.open(imagePath)

            im2 = Image.open(imagePath2)

        except:
            st.warning('The Image with path {imagePath} either does not exists or is not readable')
            return -1
            
        # im = ImageOps.grayscale(im)
        # img_data = np.asarray(im, dtype=np.uint8)
        #
        # im2 = ImageOps.grayscale(im2)
        # img_data2 = np.asarray(im2, dtype=np.uint8)

        self.JSONdata[index]["image"] = im

        # self.JSONdata[index]["image2"] = im2

        return [np.asarray(im.resize((480, 480), Image.ANTIALIAS), dtype=np.uint8), np.asarray(im2.resize((480, 480), Image.ANTIALIAS), dtype=np.uint8)]
    

    def highlightImage(self,index,model,start,end,hcolor="#00FFFF",threshold=50):

        getRGB = lambda x : tuple(int(x[i:i+2], 16) for i in (0, 2, 4))

        rgbtuple = getRGB(hcolor.lstrip("#"))

        # accounting for backward mouse selection:
        if start > end:
            temp = start
            start = end
            end = start
        
        # load image if not already loaded:
        [imageData, imageData2] = self.loadImage(index)

        
        if type(imageData) == int:
            return -1
        
        # return plain image on no selection
        if start==end :

            return [imageData, imageData2]
