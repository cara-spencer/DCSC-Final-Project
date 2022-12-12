# import json
# from pickle import APPEND as app
# from urllib import request
# import base64
import sys

# setting path
sys.path.append('../DCSC-Final-Project')

from flask import Flask, request
from QualtricsAPI.Survey import Responses, Credentials
import pymongo as pymagno
from bson.binary import Binary
import pandas as pd
import datetime
import os
# NOTE: consider renaming to DCSC_final_project or DCSCfinalproject so that you can import normally
secrets = __import__("DCSC-Final-Project.secrets")

# import jsonpickle
# import base64
# import os
# import os,sys
# import hashlib
# import io

#all the creds in the git ignore

global MONGO_CLIENT


def connect_to_mongo():
    global MONGO_CLIENT
    MONGO_CLIENT = pymagno.MongoClient(secrets.MONGO_ATLAS_CONNECTION_URL, serverSelectionTimeoutMS=5000)
    try:
        print(MONGO_CLIENT.server_info())
    except Exception as e:
        print('Unable to connect!')
        print(e)


def get_mongo_collection():
    return MONGO_CLIENT[secrets.MONGO_DB_NAME][secrets.MONGO_DB_COLLECTION]


app = Flask(__name__)

@app.route('/apiv1/getsurvey/', methods=['GET'])
def getsurvey(): 
   #establish creds using the user's api token and datacenter they enter
    from QualtricsAPI.Setup import Credentials
    #Create an instance of Credentials
    c = Credentials()
    token = request.args.get("token")
    data_center = request.args.get("data_center")
    directory_id = request.args.get("directory_id")
    c.qualtrics_api_credentials(token='token',data_center='dc',directory_id='d_id')
   #request to qualtrics api

    #Create an instance
    r = Responses()

    #Call the method
    df = r.get_questions(survey_id='SV_AFakeSurveyID')
    
#### let's try this method: https://api.qualtrics.com/2c55b7ff8b0c7-list-surveys
# import http.client

# conn = http.client.HTTPSConnection("sjc1.qualtrics.com")

# headers = {
#     'Content-Type': "application/json",
#     'X-API-TOKEN': "zI0snlFFi3ym5HCb8aiax8zPjfNr8CuP9Xo6CucZ"
#     }

# conn.request("GET", "/API/v3/surveys?offset=0", headers=headers)

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))



# @app.route('/apiv1/cleansurvey/', methods=['POST'])
# def cleansurvey(): ## cleansurvey
#      #establish creds using the user's api token and datacenter they enter
#     from QualtricsAPI.Setup import Credentials
#     #Create an instance of Credentials
#     c = Credentials()
#     #Call the qualtrics_api_credentials() method
#     c.qualtrics_api_credentials(token='Your API Token',data_center='Your Data Center',directory_id='Your Directory ID')
#
#     # fetch survey using user input
#     #if statements for each cleaning method based on if it was included in the cleansurvey request
#     # queue= []
#     # log_debug('in queue method')
#     # for i in range(0, redisClient.llen('toWorker')):
#     #     queue.append(str(redisClient.lindex('toWorker',i).decode('utf-8')))
#     # response= {'queue': queue}
#     # response_pickled = jsonpickle.encode(response)
#     # # log_info('queue info') fix later
#     # return response_pickled


get_survey_args = ['datacenter', 'token', 'directory_id']


@app.route('/getSurveys', methods=['GET'])
def getSurvey():
    # Validate.
    args = request.args
    args = args.to_dict()
    for k, v in args.items():
        if k not in get_survey_args:
            return 'Bad Argument', 400
    if len(args) != 3:
        return 'Missing Argument', 400

    # create_qualtrics_credentials(args)
    # survey_df = r.get(survey=survey_id)

    # # Perform Task
    # try:
    #     perform_stuff
    # except QualtricException e: #check if qualtrics THROWS error codes; may need to parse response if not clear
    #     if e.code == 403:
    #         return "Qualtrics threw this error! {}".format(e)
    # except otherex:
    # except Exception e:
    # finally:

    # return to user
    return args


clean_survey_args = ['datacenter', 'token', 'directory_id', 'cleaning_methods']
cleaning_method_options = ['no_nan', 'no_test', 'tidy_demo', 'simple_summary']

@app.route('/cleanSurvey/<string:survey_id>', methods=['POST'])
def cleanSurvey(survey_id):
    # Validate.
    args = request.args
    args = args.to_dict()
    for k, v in args.items():
        if k not in clean_survey_args:
            return 'Bad Argument', 400
    if len(args) != 4:
        return 'Missing Argument', 400
    cleaning_methods = args.get('cleaning_methods').split(',')
    for method in cleaning_methods:
        if method not in cleaning_method_options:
            return 'Valid options for cleaning methods are {}'.format(cleaning_method_options)

    create_qualtrics_credentials(args)
    r = Responses()
    survey_df = r.get_survey_responses(survey=survey_id)

    # Apply cleaning methods.
    for method in cleaning_methods:
        if method == 'no_nan':
            survey_df = no_nan(survey_df)
        elif method == 'no_test':
            survey_df = no_test(survey_df)
        elif method == 'tidy_demo':
            survey_df = tidy_demo(survey_df)
        elif method == 'simple_summary':
            return simple_summary(survey_df)

    # Send data to Mongo.
    survey_csv = survey_df.to_csv()
    mongo_entry = {'survey_id': survey_id, 'survey_csv': Binary(survey_csv)}
    mongo_result = get_mongo_collection().insert_one(mongo_entry)

    # Return mongo result to user.
    if not mongo_result.acknowledged:
        return 'Mongo error', 400
    else:
        return {"mongo_document_id": mongo_result.inserted_id}

@app.route('/retrieveMDBSurvey/<string:mongo_document_id>', methods=['GET'])
def retrieveMDBSurvey(mongo_document_id):
    # Validate.
    args = request.args
    args = args.to_dict()
    for k, v in args.items():
        if k not in clean_survey_args:
            return 'Bad Argument', 400
    if len(args) != 1:
        return 'Missing Argument', 400

    # Set up before connecting
    today = datetime.today()
    today = today.strftime("%m-%d-%Y")
    _, _, instance_col = set_db()
    # make an API call to the MongoDB server
    mongo_docs = instance_col.find()

    # Convert the mongo docs to a DataFrame
    docs = pd.DataFrame(mongo_docs)
    # Discard the Mongo ID for the documents
    docs.pop("_id")

    # compute the output file directory and name
    output_dir = os.path.join('..', '..', 'output_files', 'aws_instance_list', 'csv', '')
    output_file = os.path.join(output_dir, 'aws-instance-master-list-' + today +'.csv')

    # export MongoDB documents to a CSV file, leaving out the row "labels" (row numbers)
    docs.to_csv(output_file, ",", index=False) # CSV delimited by commas


##HELPERS
# Make qualtrics credentials using the user-provided token, datacenter and directory ID
def create_qualtrics_credentials(args):
    c = Credentials()
    c.qualtrics_api_credentials(token=args.get('token'), data_center=args.get('datacenter'),
                                directory_id=args.get('directory_id'))
    
#remove NaN values from entire survey    
def no_nan(survey_df):
    survey_df = survey_df.dropna(survey_df)
    return survey_df

#remove test response from 'status' column
def no_test(survey_df):
    survey_df = survey_df.drop((survey_df["Status"] == 2), axis=1) 
    return survey_df
    

#remove all metadata columns except survey duration, recorded date and recorded id
def tidy_demo(survey_df):
    survey_df = survey_df.drop(survey_df.columns[[0:5, 7, 10:17]],axis = 1)
    return survey_df

#retuns date range, number of rows (responses), any with finish code 0, avg duration
def simple_summary(survey_df):
    daterange_first = survey_df['RecordedDate'].iloc[0]  # first element
    daterange_last = survey_df['RecordedDate'].iloc[-1]  # last element
    response_n = len(survey_df.index)
    unfinished_n = (survey_df["Finished"] == 0).sum()
    avgduration = pd.mean(survey_df["Duration (in seconds)"])
    print("Date range:", daterange_first, ":", daterange_last,
          "Number of Responses:", response_n,
          "Number of Unfinished Responses (Finished = F)", unfinished_n,
          "Average Response Duration:", avgduration)


print('Starting server...')
connect_to_mongo()
get_mongo_collection()
# start flask
app.run(host="0.0.0.0", port=5000)

# to test:
# "localhost:5000/getSurvey?datacenter=ca1&token=123&directory_id=myid"
