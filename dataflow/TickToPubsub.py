from google.auth import jwt
from google.cloud import pubsub_v1
import json
import os
import pandas as pd
import shutil


TICK_PATH = 'C:/Users/brianmo/AppData/Roaming/MetaQuotes/Terminal/DA3C92B1779898CC0CACD726A655BECB/MQL4/Files/data/'
PROCESSING = 'processing/'
ACCOUNT_AUTH = 'C:/Users/brianmo/OneDrive/studio/workplace/FXML/forex-pubsub_key.json'
PROJECT = 'etl-practice-283400'
TOPIC = 'forex_tick_topic'

# if __name__=='__main__':
file_list = os.listdir(TICK_PATH)   
tick_df = pd.DataFrame()
processing_list = []
for file in file_list:
    if file[-8:] == 'Tick.csv':
        staging_file = TICK_PATH+file
        processing_file = TICK_PATH+PROCESSING+file
        shutil.move(staging_file, processing_file)
        processing_list.append(processing_file)
        tmp_df = pd.read_csv(processing_file)
        if len(tick_df) == 0:
            tick_df = tmp_df
        else:
            tick_df = tick_df.append(tmp_df)

# de-duplicate records
# convert to json format
tick_df.drop_duplicates(['TickTime','Symbol'],keep='last',inplace=True)
tick_json = tick_df.to_json(orient='records')
          
#------------------------------------------------------------------------------
# P U B L I S H
#---------------
# Authentication
#---------------
service_account_info = json.load(open(ACCOUNT_AUTH))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)
publisher = pubsub_v1.PublisherClient(credentials=credentials)

#---------------
# publishing
#---------------
topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id=PROJECT,
    topic=TOPIC,  # Set this to something appropriate.
)
try:
    future = publisher.publish(topic_name, bytes(tick_json,'utf-8'))#, spam='eggs')
    print(future.result())
    # clean up success file
    for file in processing_list:
        os.remove(file)
except:
    print('Exception')
    # move back to staging
    for file in processing_list:
        shutil.move(file,TICK_PATH)