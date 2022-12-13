
import sys

# setting path
sys.path.append('../DCSC-Final-Project')

from flask import Flask, request
from QualtricsAPI.Survey import Responses, Credentials
import pymongo as pymagno
from bson.binary import Binary
import pandas as pd
import http.client

# NOTE: consider renaming to DCSC_final_project or DCSCfinalproject so that you can import normally
secrets = __import__("DCSC-Final-Project.secrets")


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

get_survey_args = ['datacenter', 'token', 'directory_id']
@app.route('/apiv1/getsurvey/', methods=['GET'])
def getsurvey():
    # Validate.
    args = request.args
    args = args.to_dict()
    for k, v in args.items():
        if k not in get_survey_args:
            return 'Bad Argument', 400
    if len(args) != 3:
        return 'Missing Argument', 400
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
conn = http.client.HTTPSConnection("sjc1.qualtrics.com")

headers = {
    'Content-Type': "application/json",
    'X-API-TOKEN': "zI0snlFFi3ym5HCb8aiax8zPjfNr8CuP9Xo6CucZ"
    }

conn.request("GET", "/API/v3/surveys?offset=0", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

##Clean survey method
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
    mongo_entry = {'survey_id': survey_id, 'survey_csv': Binary(survey_csv)}
    mongo_result = get_mongo_collection().insert_one(mongo_entry)

    # Return mongo result to user.
    if not mongo_result.acknowledged:
        return 'Mongo error', 400
    else:
        return {"mongo_document_id": mongo_result.inserted_id}

@app.route('/retrieveMDBSurvey/<string:mongo_document_id>', methods=['GET'])
def retrieveMDBSurvey(mongo_document_id):
    # Read MongoDB through pymongo API to retrieve cleaned survey
    mongo_doc = get_mongo_collection().find_one({"_id": ObjectId(mongo_document_id)})

    # retrieve file from MongoDB and write to a BytesIO object to prepare for sending file to client.
    ret_bytes = BytesIO()
    ret_bytes.write(mongo_doc['survey_csv']) #might need encoding='utf-8'
    ret_bytes.seek(0)

    # Send file to client
    return send_file(ret_bytes, download_name='cleaned_survey.csv', mimetype='text/csv')


@app.route('/simpleSummary', methods=['POST'])
def simpleSummary():
    # Validate.
    args = request.args
    args = args.to_dict()
    if len(args) != 1:
        return 'Missing Argument', 400

    # import local version of survey results
    data = request.data
    try:
        survey_df = pd.read_csv(data)
    except Exception as e:
        return "Can't read as CSV", 400

    return simple_summary(survey_df)


##HELPERS
# Make qualtrics credentials using the user-provided token, datacenter and directory ID
def create_qualtrics_credentials(args):
    c = Credentials()
    c.qualtrics_api_credentials(token=args.get('token'), data_center=args.get('datacenter'),
                                directory_id=args.get('directory_id'))
    
#remove NaN values from entire survey    
def no_nan(survey_df):
    c = survey_df.columns[18:217]
    survey_df = survey_df.dropna(subset=c, how='any')
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

