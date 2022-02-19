import streamlit as st
import SessionState

from layouts.GPS.gpsHelper import gpsHelper
import numpy as np
import json
import csv
from io import StringIO
import os
from config import defaultThreshold
from shutil import copyfile

from layouts.OCR.src.gif import *
from layouts.GPS.GPSMetrics import displayGPSMetrics
from layouts.OCR.src.diffVisualizer import *
from layouts.OCR.src.frontendbuilds import *
from layouts.OCR.src.interactiveImage import *
from layouts.OCR.src.interactiveText import *
from layouts.OCR.src.headingDisplay import *
from layouts.OCR.src.info import *



def saveDoc(data, metaData):
    savefile = metaData["metaData"]["savePath"] + '/' + 'save.txt'
    dataClass = list(data.keys())[0]
    index = list(data.values())[0]
    line = dataClass + " " + str(index)
    with open(savefile, 'a') as f:
        f.write(line + '\n')

    # save the json file too:
    src = metaData["metaData"]["dataPaths"][dataClass]
    dest = metaData["metaData"]["savePath"] + '/' + dataClass + ".json"
    if not os.path.exists(dest):
        print(f"I am copying {src} file to {dest} file")
        copyfile(src, dest)

"""
Definition of APP Layout:
"""


def app(metaData=None):
    if metaData is None:
        st.error("Got None object Metadata for GPS Layout")

    key = metaData["metaData"]["key"]

    # page layout data loader
    # data loads once -- gets cached.
    # if user wants to keep the app dynamic to changes in json file
    # comment out the @st.cache call above the initGPSHelper() function

    # @st.cache(allow_output_mutation=True, suppress_st_warning=True)
    def initGPSHelper():

        """
        Input agrs: None

        output : Dictionary with GPSHelper objects initalized for each
                 dataclass defined in the jsonData file.

                Check gpsHelper file in the same directory for more details
        """

        print(f"Loading Data for {metaData['metaData']['pageName']}")

        subGPSs = {}

        for datasetClass in metaData["metaData"]["dataPaths"]:
            jsonFile = metaData["metaData"]["dataPaths"][datasetClass]
            gps = gpsHelper(jsonFile)
            subGPSs[datasetClass] = gps
        return subGPSs

    gpsObjects = initGPSHelper()

    if gpsObjects != -1:
        dataTypes = list(gpsObjects.keys())
        dataTypes.append('bookmarks')

        state = SessionState._get_state()

        # state = SessionState._get_state()

        ## Page Heading:

        # add a bookmarks variable:

        if state.bookmarks is None:

            state.bookmarks = {
                key: []
            }



        elif key not in state.bookmarks:
            state.bookmarks[key] = []  # [{"train":index}]

        if state.savedData is None:
            state.savedData = {
                key: []
            }
        if key not in state.savedData:
            state.savedData[key] = []

        dataClass = st.sidebar.selectbox(
            "Choose the Dataset Class",
            dataTypes,
            index=0
        )
        # print('--->',dataClass)
        if dataClass != 'bookmarks':
            gps = gpsObjects[dataClass]
        else:
            if state.bookmarks is None or len(state.bookmarks[key]) == 0:
                st.warning('There are no book marked images in for this OCR Page.')
                return
            gps = gpsObjects[list(state.bookmarks[key][state.pageDetails[key][dataClass]].keys())[0]]

        if gps.models is not None:

            if dataClass != "bookmarks":
                model = st.sidebar.selectbox(
                    'Choose Model to Sort By',
                    gps.models,
                    index=0
                )

                sort_by = st.sidebar.selectbox(
                    "Choose Metrics to Sort By",
                    gps.metric_details[model],
                    index=0
                )

                if sort_by != 'None':
                    order = st.sidebar.selectbox(
                        "Order",
                        ["ascending", "descending"],
                        index=0
                    )

                else:
                    order = 'ascending'

            if state.pageDetails is None:
                state.pageDetails = {
                    key: {
                        dataClass: {
                            model: {
                                "ascending": {x: 0 for x in gps.metric_details[model]},
                                "descending": {x: 0 for x in gps.metric_details[model]}
                            }
                        }
                    }
                }

            if key not in state.pageDetails:
                state.pageDetails[key] = {
                    dataClass: {
                        model: {
                            "ascending": {x: 0 for x in gps.metric_details[model]},
                            "descending": {x: 0 for x in gps.metric_details[model]}
                        }
                    }
                }

            if dataClass not in state.pageDetails[key]:
                if dataClass != "bookmarks":
                    state.pageDetails[key][dataClass] = {
                        model: {
                            "ascending": {x: 0 for x in gps.metric_details[model]},
                            "descending": {x: 0 for x in gps.metric_details[model]}
                        }
                    }

                else:
                    state.pageDetails[key][dataClass] = 0

            if dataClass != 'bookmarks' and model not in state.pageDetails[key][dataClass]:
                state.pageDetails[key][dataClass][model] = {
                    "ascending": {x: 0 for x in gps.metric_details[model]},
                    "descending": {x: 0 for x in gps.metric_details[model]}
                }

            if dataClass != "bookmarks":

                if order == 'ascending':

                    index = gps.sortedSecIndices[model][sort_by][
                        state.pageDetails[key][dataClass][model][order][sort_by]]

                else:

                    index = gps.sortedSecIndices[model][sort_by][
                        gps.len - 1 - state.pageDetails[key][dataClass][model][order][sort_by]]

            else:

                index = list(state.bookmarks[key][state.pageDetails[key][dataClass]].values())[0]

                gps = gpsObjects[list(state.bookmarks[key][state.pageDetails[key][dataClass]].keys())[0]]

            if dataClass != "bookmarks":
                currentLoc = state.pageDetails[key][dataClass][model][order][sort_by]
            else:
                currentLoc = state.pageDetails[key][dataClass]

            if gps.len > 1:
                if dataClass != "bookmarks":
                    state.pageDetails[key][dataClass][model][order][sort_by] = st.slider(
                        "Select image Index",
                        0,
                        gps.len - 1,
                        state.pageDetails[key][dataClass][model][order][sort_by]
                    )

                    prev, _, next = st.beta_columns([1, 0.1, 20])

                    if next.button("Next", key=key):

                        if state.pageDetails[key][dataClass][model][order][sort_by] + 1 >= gps.len:
                            st.warning('This is the last image.')
                        else:
                            state.pageDetails[key][dataClass][model][order][sort_by] += 1

                            # re-initialize all your data
                            # :)

                            state.selection_data = None
                            state.textRange = None
                            state.crop_range = None

                    if prev.button("Previous", key=key):

                        if state.pageDetails[key][dataClass][model][order][sort_by] - 1 < 0:

                            st.warning('This is the First image. Cannot go backwards')

                        else:
                            state.pageDetails[key][dataClass][model][order][sort_by] -= 1
                            state.selection_data = None
                            state.textRange = None
                            state.crop_range = None

                else:
                    if len(state.bookmarks[key]) > 1:
                        currentLoc = state.pageDetails[key][dataClass]
                        state.pageDetails[key][dataClass] = st.slider(
                            "Select image Index",
                            0,
                            len(state.bookmarks[key]) - 1,
                            state.pageDetails[key][dataClass]
                        )
                        if state.pageDetails[key][dataClass] != currentLoc:
                            state.selection_data = None
                            state.textRange = None
                            state.crop_range = None

                        prev, _, next = st.beta_columns([1, 0.1, 20])

                        if next.button("Next", key=key):

                            if state.pageDetails[key][dataClass] + 1 >= len(state.bookmarks[key]):
                                st.warning('This is the last image.')
                            else:
                                state.pageDetails[key][dataClass] += 1
                                state.selection_data = None
                                state.textRange = None
                                state.crop_range = None

                        if prev.button("Previous", key=key):

                            if state.pageDetails[key][dataClass] - 1 < 0:

                                st.warning('This is the First image. Cannot go backwards')

                            else:
                                state.pageDetails[key][dataClass] -= 1
                                state.selection_data = None
                                state.textRange = None
                                state.crop_range = None


                    else:

                        st.warning("Note: There is only one image in your bookmarks for this layout.")

            if state.crop_range is None:
                state.crop_range = {
                    key: {
                        "start_px": -1,
                        "end_px": -1
                    }
                }
            elif key not in state.crop_range:
                # state.crop_range = None
                state.crop_range[key] = {
                    "start_px": -1,
                    "end_px": -1
                }

            st.sidebar.markdown("## Settings:")

            if state.fontSize is None:
                state.fontSize = {
                    "playground": 30,
                    "diffViz": 20
                }
            if state.commonFontSize is None:
                state.commonFontSize = False

            if state.highlightColor is None:
                state.highlightColor = "#00FFFF"

            if state.threshold is None:
                state.threshold = {key: defaultThreshold}

            if key not in state.threshold:
                state.threshold[key] = defaultThreshold
            # Font Size Input
            with st.sidebar.beta_expander("Render:"):
                st.markdown("### Text Font Size:")
                state.fontSize["playground"] = st.slider("Choose Font Size(px) for the text playground via slide bar",
                                                         10, 300, state.fontSize["playground"])

                pgfontInput = st.text_input("Or enter a font value", state.fontSize["playground"], key="playground")
                if pgfontInput != '':
                    try:
                        state.fontSize["playground"] = int(pgfontInput)
                    except:
                        st.warning("Kindly input a valid font size : non-negative integer")
                # print('LINE 363 set fontSize to ',state.fontSize['playground'])

                st.markdown("---------")
                st.markdown("### Image Threshold :")
                state.threshold[key] = st.slider(
                    "Choose threshold Value (to avoid pixels getting over-written by color)",
                    0, 255, state.threshold[key])

                threshInput = st.text_input("Or enter a threshold value", state.threshold[key], key=key)
                if threshInput != '':
                    threshInput = int(threshInput)
                    try:
                        if threshInput > 255:
                            raise Exception
                        state.threshold[key] = threshInput

                    except:
                        st.warning("Kindly input a valid threshold vale : integer between 0 and 255")

                st.markdown("---------")
                st.markdown("### highlighted image color")
                state.highlightColor = st.color_picker("Choose a color", value=state.highlightColor)

            with st.sidebar.beta_expander("diff Visualizer:"):
                st.markdown("### Diff Visualizer Font Size:")

                if st.checkbox("Set Font Size same as that of text-playground?", value=state.commonFontSize):
                    state.commonFontSize = True
                    state.fontSize["diffViz"] = state.fontSize["playground"]
                else:
                    state.fontSize["diffViz"] = st.slider("Choose Font Size(px) for the diff visualizer via slide bar",
                                                          10, 300, state.fontSize["diffViz"])
                    diffVizfontInput = st.text_input("Or enter a font value", state.fontSize["diffViz"], key="diffViz")
                    if diffVizfontInput != '':
                        try:
                            state.fontSize["diffViz"] = int(diffVizfontInput)
                        except:
                            st.warning("Kindly input a valid font size : non-negative integer")

                st.markdown("Image Settings:")

                if state.displayImageDiff is None:
                    state.displayImageDiff = False

                state.displayImageDiff = st.checkbox('Display Image in Diff View Area?')

            try:
                ground = gps.JSONdata[index]["groundTruth"]
            except:
                ground = None


            for model_no in range(len(gps.models)):
                disp_model = gps.models[model_no]

                uploaded_file = st.file_uploader("Upload GPS Json", type = ["json"])

                if uploaded_file is not None:


                    # To convert to a string based IO:
                    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

                    json_obj = json.load(stringio)

                    with open("example/jsonData/GPS/GPS.json", "w") as outfile:
                        json.dump(json_obj, outfile)

                if model_no == 0 :

                    [img_data, img_data2] = gps.highlightImage(index, disp_model, -1, -1)

                    # ensure that the data receieved from the OCRhelper function is actually valid
                    if type(img_data) == np.ndarray:

                        # cool feature where the user can see if he has already bookmarked/saved the image.
                        extraChars = ''

                        if dataClass != "bookmarks":

                            if {dataClass: index} in state.bookmarks[key]:
                                extraChars += '🔖'

                            if {dataClass: index} in state.savedData[key]:
                                extraChars += '💾'
                        else:
                            extraChars += '🔖'
                            if state.bookmarks[key][state.pageDetails[key][dataClass]] in state.savedData[key]:
                                extraChars += '💾'

                        st.markdown(f"## {extraChars} Image")
                        st.markdown('-----------------')

                        # imageLocation1 = st.empty()
                        # imageLocation2 = st.empty()
                        #
                        # imageLocation1.image(img_data)
                        # imageLocation2.image(img_data2)
                        #
                        imageLocation = st.empty()
                        imageLocation.image([img_data, img_data2])



                        # if st.button("Rotate by 90"):
                        #     img_data = np.rot90(img_data)
                        #     img_data2 = np.rot90(img_data2)
                        #     # imageLocation.image([img_data, img_data2])
                        #     imageLocation1.image(img_data)
                        #     imageLocation2.image(img_data2)

                        # st.image(img_data)
                        # st.image(img_data2)

                        if type(ground) == str:

                            # displayModelHeading('Ground Truth','ground-truth')


                            styleString = "<style>.big-font {font-size:" + str(
                                state.fontSize["playground"]) + "px; !important;}</style>"
                            st.markdown(styleString, unsafe_allow_html=True)

                            st.markdown(f'<p class="big-font">{ground}</p>', unsafe_allow_html=True)


                displayModelHeading(disp_model, 'normal-model')


                if "metrics" in gps.JSONdata[index]['outputs'][disp_model]:
                    st.markdown('#### Metrics (in fractions):')
                    displayGPSMetrics(gps, index, disp_model)

            if dataClass != 'bookmarks':

                bookMarkButton, _, saveButton = st.beta_columns([3, 0.1, 30])

                if bookMarkButton.button("Bookmark 🔖"):

                    bookMarkData = {dataClass: index}

                    if bookMarkData in state.bookmarks[key]:

                        st.warning("Page already bookmarked")

                    else:

                        state.bookmarks[key].append({dataClass: index})
                        # print(dataClass)
                        if 'bookmarks' not in state.pageDetails[key]:
                            # print('initialized bookmark')
                            state.pageDetails[key]['bookmarks'] = len(state.bookmarks[key]) - 1
                        st.success("Successfully bookmarked")

                if saveButton.button("Save 💾"):

                    toSave = {dataClass: index}

                    if toSave not in state.savedData[key]:

                        saveDoc(data=toSave, metaData=metaData)
                        state.savedData[key].append(toSave)
                        st.success("Image saved successfully")
                    else:
                        st.warning("Page already saved")
            else:
                saveSingle, _, saveAll = st.beta_columns([3, 0.1, 30])
                # if the dataclass is a book mark location
                if saveSingle.button("Save this Image 💾"):
                    toSave = state.bookmarks[key][state.pageDetails[key][dataClass]]
                    if toSave in state.savedData[key]:
                        st.warning("Page already saved")
                    else:

                        saveDoc(data=toSave, metaData=metaData)
                        state.savedData[key].append(toSave)
                        st.success("Successfully bookmarked")

                if saveAll.button("Save all bookmarks 💾"):
                    for sdata in state.bookmarks[key]:
                        if sdata not in state.savedData[key]:
                            saveDoc(data=sdata, metaData=metaData)
                            state.savedData[key].append(sdata)
                    st.success("All bookmarks Saved successfully")

            if 'info' in gps.JSONdata[index]:
                displayInfo(index, gps)

            if dataClass != "bookmarks":
                if state.pageDetails[key][dataClass][model][order][sort_by] != currentLoc or state.prevIndex != index:
                    # print('Line 649')
                    # state.selection_data = None
                    state.textRange = None
                    state.crop_range = None
            else:

                if state.prevDataClass != dataClass or state.prevIndex != index or state.pageDetails[key][
                    dataClass] != currentLoc:
                    # print('Setting None')

                    state.textRange = None
                    state.crop_range = None

            state.prevKey = key
            state.prevDataClass = dataClass
            state.prevIndex = index
            state.prevPrimaryModel = model
            state.prevTextRange = state.textRange



        elif gps.models is None:

            if state.pageDetails is None:
                state.pageDetails = {
                    key: {
                        dataClass: {
                            'None': 0
                        }
                    }
                }
            if key not in state.pageDetails:
                state.pageDetails[key] = {
                    dataClass: {
                        'None': 0
                    }
                }

            if dataClass not in state.pageDetails[key]:

                if dataClass != 'bookmarks':
                    state.pageDetails[key][dataClass] = {
                        'None': 0
                    }
                else:
                    state.pageDetails[key][dataClass] = 0

            if dataClass != 'bookmarks':
                index = state.pageDetails[key][dataClass]['None']
            else:
                index = list(state.bookmarks[key][state.pageDetails[key][dataClass]].values())[0]

            image_data = gps.loadImage(index)

            if gps.len > 1:
                if dataClass != "bookmarks":

                    state.pageDetails[key][dataClass]['None'] = st.slider(
                        "Select image Index",
                        0,
                        gps.len - 1,
                        state.pageDetails[key][dataClass]['None']
                    )

                    prev, _, next = st.beta_columns([1, 0.1, 20])

                    if next.button("Next", key=key):

                        # print('hi')

                        if state.pageDetails[key][dataClass]['None'] + 1 >= gps.len:
                            st.warning('This is the last image.')
                        else:
                            state.pageDetails[key][dataClass]['None'] += 1

                    if prev.button("Previous", key=key):

                        if state.pageDetails[key][dataClass]['None'] - 1 < 0:

                            st.warning('This is the First image. Cannot go backwards')

                        else:
                            state.pageDetails[key][dataClass]['None'] -= 1




                else:
                    if len(state.bookmarks[key]) > 1:
                        currentLoc = state.pageDetails[key][dataClass]
                        state.pageDetails[key][dataClass] = st.slider(
                            "Select image Index",
                            0,
                            len(state.bookmarks[key]) - 1,
                            state.pageDetails[key][dataClass]
                        )

                        prev, _, next = st.beta_columns([1, 0.1, 20])

                        if next.button("Next", key=key):

                            if state.pageDetails[key][dataClass] + 1 >= len(state.bookmarks[key]):
                                st.warning('This is the last image.')
                            else:
                                state.pageDetails[key][dataClass] += 1

                        if prev.button("Previous", key=key):

                            if state.pageDetails[key][dataClass] - 1 < 0:

                                st.warning('This is the First image. Cannot go backwards')

                            else:
                                state.pageDetails[key][dataClass] -= 1


            else:

                st.warning(f"Note: There is only one image in {dataClass} for this layout.")

            extraChars = ''

            if dataClass != "bookmarks":

                if {dataClass: index} in state.bookmarks[key]:
                    extraChars += '🔖'

                if {dataClass: index} in state.savedData[key]:
                    extraChars += '💾'
            else:
                extraChars += '🔖'
                if state.bookmarks[key][state.pageDetails[key][dataClass]] in state.savedData[key]:
                    extraChars += '💾'
            st.markdown(f"## {extraChars} Image")
            st.markdown('-----------------')
            st.image(image_data)

            if 'groundTruth' in gps.JSONdata[index]:
                ground = gps.JSONdata[index]['groundTruth']
                displayModelHeading('Ground Truth', 'ground-truth')

                if state.fontSize is None:
                    state.fontSize = {"playground": 30, "diffViz": 20}

                if ground is not None:
                    with st.sidebar.beta_expander("Render:"):
                        st.markdown("### Text Font Size:")
                        state.fontSize["playground"] = st.slider(
                            "Choose Font Size(px) for the text playground via slide bar",
                            10,
                            300,
                            state.fontSize["playground"])

                        pgfontInput = st.text_input("Or enter a font value", state.fontSize["playground"],
                                                    key="playground")
                        if pgfontInput != '':
                            try:
                                state.fontSize["playground"] = int(pgfontInput)
                            except:
                                st.warning("Kindly input a valid font size : non-negative integer")

                    styleString = "<style>.big-font {font-size:" + str(
                        state.fontSize["playground"]) + "px; !important;}</style>"
                    st.markdown(styleString, unsafe_allow_html=True)
                    st.markdown(f'<p class="big-font">{ground}</p>', unsafe_allow_html=True)

            if dataClass != 'bookmarks':

                bookMarkButton, _, saveButton = st.beta_columns([3, 0.1, 30])

                if bookMarkButton.button("Bookmark 🔖"):

                    bookMarkData = {dataClass: index}

                    if bookMarkData in state.bookmarks[key]:

                        st.warning("Page already bookmarked")

                    else:

                        state.bookmarks[key].append({dataClass: index})
                        if 'bookmarks' not in state.pageDetails[key]:
                            state.pageDetails[key]['bookmarks'] = 0
                        st.success("Successfully bookmarked")

                if saveButton.button("Save 💾"):

                    toSave = {dataClass: index}

                    if toSave not in state.savedData[key]:

                        saveDoc(data=toSave, metaData=metaData)
                        state.savedData[key].append(toSave)
                        st.success("Image saved successfully")
                    else:
                        st.warning("Page already saved")
            else:
                saveSingle, _, saveAll = st.beta_columns([3, 0.1, 30])
                # if the dataclass is a book mark location
                if saveSingle.button("Save this Image 💾"):
                    toSave = state.bookmarks[key][state.pageDetails[key][dataClass]]
                    if toSave in state.savedData[key]:
                        st.warning("Page already saved")
                    else:

                        saveDoc(data=toSave, metaData=metaData)
                        state.savedData[key].append(toSave)
                        st.success("Successfully bookmarked")

                if saveAll.button("Save all bookmarks 💾"):
                    for sdata in state.bookmarks[key]:
                        if sdata not in state.savedData[key]:
                            saveDoc(data=sdata, metaData=metaData)
                            state.savedData[key].append(sdata)
                    st.success("All bookmarks Saved successfully")

            if 'info' in gps.JSONdata[index]:
                displayInfo(index, gps)

            state.sync()

    state.sync()
