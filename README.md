#Qualtrics Survey Data Cleaning Pipeline
The purpose of these servers are to provide survey cleaning and storage as a service. 
Two rest-servers are built using Flask and python. 
A MongoDB cluster is provided by the server for user usage but code can be modified to use your own. 
We store our MongoDB creds and names in a secrets file so make one with your own with your creds if you want.
You'll see where the secrets file is referenced in each server script. 

Instructions and requirements for usage:

1. fromQualtrics-restsever.py

Requires that you have authorization to use the API. 
** We did not and could not test it.

API methods included:

getSurvey: takes your Qualtrics credentials to web scrape Qualtrics for a list of your surveys. 
Use this to get your Survey ID for usage in cleanSurvey if you don't have one in mind. 
You supply from Qualtrics: datacenter', token, and directory_id

Example call: 
curl localhost:5000/getsurvey?datacenter=ca1,token=ehfoweojfjweof,directory_id=fhfhwhjfhefuf


cleanSurvey: takes the Qualtrics creds, now including the Survey ID, AND your cleaning functions to 
1. retrieve the survey
2. perform the specified cleaning
3. send the cleaned survey to MongoDB
4. return the MongoDB document ID

Cleaning functions:
1. no_na: removes NA's in non-metadata columns (AKA the response data)
2. no_test: filters out the tests according to the metadata Status column
3. tidy_md: removes all metadata columns except Survey_Duration, RecordedData and ResponseID

Example call:
curl localhost:5000/cleanSurvey?datacenter=ca1,token=ehfoweojfjweof,directory_id=fhfhwhjfhefuf,surveyID=idjaijsdfijg,cleaning_methods=no_na


retrieveMDBsurvey: takes your MongoDB ID and a file name for your cleaned survey. 
Will send the cleaned survey to location of server code. 

Example call:
curl localhost:5000/retrieveMDBSurvey/6396d08b260345aa73278a16 > tmp

simpleSummary: takes your survey (can use clean or raw/original) and provides metadata summary

Computes:Date range, Number of Responses, Number of Unfinished Responses (Finished = F) and Average Response Duration.

Example call: 
curl -F data=@"C:/Users/you/dcsc/testsurvey.csv" -X POST localhost:5000/simpleSummary

--
2. fromlocal-restserver.py

The outcome is the same, just the source of the survey data is different. 

API methods included:

cleanSurvey: takes a file's location, AND your cleaning functions
Follows the same flow as the Qualtrics version and has the same cleaning function options. 

Example call for removing NA's:
curl -F data=@"C:/Users/you/dcsc/testsurvey.csv" -X POST localhost:5000/cleanSurvey?cleanSurvey?cleaning_methods=no_na

retrieveMDBsurvey: takes your MongoDB ID and a file name for your cleaned survey. 
Will send the cleaned survey to location of server code. 

Example call:
curl localhost:5000/retrieveMDBSurvey/6396d08b260345aa73278a16 > tmp

simpleSummary: takes your survey (can use clean or raw/original) and provides metadata summary

Computes: Date range, Number of Responses, Number of Unfinished Responses (Finished = F) and Average Response Duration.

Example call: 
curl -F data=@"C:/Users/you/dcsc/testsurvey.csv" -X POST localhost:5000/simpleSummary
