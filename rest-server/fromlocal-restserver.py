# local-server


global MONGO_CLIENT
import sys

sys.path.append('../DCSC-Final-Project')

from flask import Flask, request, send_file, jsonify
import pymongo as pymagno
from bson import ObjectId
from bson.binary import Binary
import pandas as pd
from io import StringIO, BytesIO
import local_secrets as secrets
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

# import local version of survey results
#survey_df = pd.read_csv('iSAT AICL Survey - Copy2_December 11, 2022_12.37.csv')

##Clean survey method
clean_survey_args = ['cleaning_methods']
cleaning_method_options = ['no_na', 'no_test', 'tidy_md', 'simple_summary']


@app.route('/cleanSurvey', methods=['POST'])
def cleanSurvey():
    # Validate.
    args = request.args
    args = args.to_dict()
    for k, v in args.items():
        if k not in clean_survey_args:
            return 'Bad Argument', 400
    if len(args) != 1:
        return 'Missing Argument', 400
    cleaning_methods = args.get('cleaning_methods').split(',')
    for method in cleaning_methods:
        if method not in cleaning_method_options:
            return 'Valid options for cleaning methods are {}'.format(cleaning_method_options)

    # import local version of survey results
    try:
        data = request.files['data']
    except Exception as e:
        return "You must supply the form in the 'data' parameter of the body.", 400

    try:
        survey_df = pd.read_csv(data)
    except Exception as e:
        return "Can't read as csv", 400

    print(survey_df.head())

    # Apply cleaning methods.
    for method in cleaning_methods:
        if method == 'no_na':
            survey_df = no_na(survey_df)
            print("Done dropping rows with NAs")
            print(survey_df.head())
        elif method == 'no_test':
            survey_df = no_test(survey_df)
            print("Done dropping tests")
            print(survey_df.head())
        elif method == 'tidy_md':
            survey_df = tidy_md(survey_df)
            print("Done tidying the metadata")
            print(survey_df.head())
    print("Done cleaning")

    # Send data to Mongo.
    survey_csv = survey_df.to_csv()
    print("Made survey dataframe into csv")
    mongo_entry = {'survey_csv': Binary(bytes(survey_csv, encoding='utf-8'))}
    print("Binarized the csv")
    print(mongo_entry)
    mongo_result = get_mongo_collection().insert_one(mongo_entry)
    print("Sent to MongoDB!")

    # Return mongo result to user.
    if not mongo_result.acknowledged:
        return 'Mongo error', 400
    else:
        return {"mongo_document_id": str(mongo_result.inserted_id)}


##Get cleaned survey back from MongoDB
@app.route('/retrieveMDBSurvey/<string:mongo_document_id>', methods=['GET'])
def retrieveMDBSurvey(mongo_document_id):
    # Read MongoDB through pymongo API to retrieve cleaned survey
    mongo_doc = get_mongo_collection().find_one({"_id": ObjectId(mongo_document_id)})

    # retrieve file from MongoDB and write to a BytesIO object to prepare for sending file to client.
    ret_bytes = BytesIO()
    ret_bytes.write(mongo_doc['survey_csv'])  # might need encoding='utf-8'
    ret_bytes.seek(0)

    # Send file to client
    return send_file(ret_bytes, download_name='cleaned_survey.csv', mimetype='text/csv')


##Get a summary of metadata from file
@app.route('/simpleSummary', methods=['POST'])
def simpleSummary():
    # import local version of survey results
    try:
        data = request.files['data']
        print("Successfully requested the data")
    except Exception as e:
        return jsonify(error=str(e)), 400

    try:
        survey_df = pd.read_csv(data)
    except Exception as e:
        return "Can't read as csv", 400

    print(survey_df.head())

    return simple_summary(survey_df)


##HELPERS

# remove NaN values from entire survey
def no_na(survey_df):
    c = survey_df.columns[18:217]
    survey_df = survey_df.dropna(subset=c, how='any')
    return survey_df


# remove test response from 'status' column
def no_test(survey_df):
    survey_df = survey_df.drop((survey_df["Status"] == 2), axis=1)
    return survey_df


# remove all metadata columns except survey duration, recorded date and recorded id
def tidy_md(survey_df):
    survey_df = survey_df.drop(survey_df.columns[0:5, 7, 10:17], axis=1)
    return survey_df


# retuns date range, number of rows (responses), any with finish code 0, avg duration
def simple_summary(survey_df):
    daterange_first = survey_df['RecordedDate'].iloc[0]  # first element
    daterange_last = survey_df['RecordedDate'].iloc[-1]  # last element
    response_n = len(survey_df.index)
    unfinished_n = (survey_df["Finished"] == 0).sum()
    avgduration = (survey_df["Duration (in seconds)"]).mean
    return {"Date_Range": "{}:{}".format(daterange_first, daterange_last),
            "Number_of_Response": response_n,
            "Number_of_Unfinished_Responses": unfinished_n,
            "Average_Response_Duration": avgduration}


print('Starting server...')
connect_to_mongo()
get_mongo_collection()
# start flask
app.run(host="0.0.0.0", port=5000)

# to test:
# curl -F data=@"C:/Users/caraa/OneDrive/Desktop/gradschool/dcsc/testsurvey.csv" -X POST localhost:5000/cleanSurvey?cleaning_methods=no_nan
# curl localhost:5000/retrieveMDBSurvey/6396d08b260345aa73278a16 > tmp
