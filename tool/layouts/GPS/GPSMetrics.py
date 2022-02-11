import streamlit as st

def displayGPSMetrics(gps,index,model):
    
    no_of_metrics = len(gps.metric_details[model])

    metricStrings = []
    # st.text(model)
    for  metric in gps.metric_details[model]:
        if metric !="None":

            if metric =="speed":
                mstring = f'**{metric} :** {gps.JSONdata[index]["outputs"][model]["metrics"][metric]:.4f}'
                mstring+= " m/s"

            else:
                mstring = f'**{metric} :** {gps.JSONdata[index]["outputs"][model]["metrics"][metric]:.6f}'

            metricStrings.append(mstring)

    st.markdown(' , '.join(metricStrings))