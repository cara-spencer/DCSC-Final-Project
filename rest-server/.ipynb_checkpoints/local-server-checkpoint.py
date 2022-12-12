#local-server


global MONGO_CLIENT
import sys

sys.path.append('../DCSC-Final-Project')

from flask import Flask, request
import pymongo as pymagno
from bson.binary import Binary
import pandas as pd
import datetime
import os

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

#import local version of survey results 
survey_df=pd.read_csv('iSAT AICL Survey - Copy2_December 11, 2022_12.37')

cleaning_method_options = ['no_nan', 'no_test', 'tidy_demo', 'simple_summary']


    # Apply cleaning methods.
for method in cleaning_methods:
    if method == 'no_nan':
         survey_df = no_nan(survey_df)
    elif method == 'no_test':
        survey_df = no_test(survey_df)
    elif method == 'tidy_demo':
        survey_df = tidy_demo(survey_df)
    elif method == 'simple_summary':
        survey_df = simple_summary(survey_df)

    # Send data to Mongo.
    survey_csv = survey_df.to_csv()
    mongo_entry = {'survey_id': survey_id, 'survey_csv': Binary(survey_csv)}
    mongo_result = get_mongo_collection().insert_one(mongo_entry)

    # # Return mongo result to user.
    # if not mongo_result.acknowledged:
    #     return 'Mongo error', 400
    # else:
    #     return {"mongo_document_id": mongo_result.inserted_id}

##Not sure if we need this?
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
    survey_df = survey_df.drop(survey_df.columns[0:5, 7, 10:17],axis = 1)
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
