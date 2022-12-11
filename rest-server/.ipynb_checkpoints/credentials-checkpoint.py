# #lets try the method from this page: https://api.qualtrics.com/ZG9jOjg3NjYzMg-api-key-authentication
# import urllib
# from urllib import request #default module for Python 3.X

# url = 'https://sjc1.qualtrics.com/API/v3/:collection'
# header = {'X-API-TOKEN': 'zI0snlFFi3ym5HCb8aiax8zPjfNr8CuP9Xo6CucZ'}

# req = urllib.request.Request(url,None,header) #generating the request object

# handler = urllib.request.urlopen(req) #running the request object

# print(handler.status) #print status code
# print(handler.reason)


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


####Let's try OAuth from this page: https://api.qualtrics.com/24d63382c3a88-api-quick-start

import http.client
import mimetypes
import base64

#create the Base64 encoded basic authorization string
clientID= "c270bd0730a2a2d41adf8d0bd13cbcc4"
clientsecret= "ODtx2LmPZKFVP88TUKDWQztuaWcVIvi0u1TJxRZG0KlUH8Sx6McSGJyffE9Y11gN"
auth = "{0}:{1}".format(clientID, clientsecret)
encodedBytes=base64.b64encode(auth.encode("utf-8"))
authStr = str(encodedBytes, "utf-8")

#create the connection 
conn = http.client.HTTPSConnection("st3.qualtrics.com")
body = "grant_type=client_credentials"
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}
headers['Authorization'] = 'Basic {0}'.format(authStr)

#make the request
conn.request("POST", "/oauth2/token", body, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))


#### Let's try the method from this video: https://www.youtube.com/watch?v=_uhY_a4NgNc
# import requests
# import zipfile
# import io

# def get_qualtrics_survey(dir_save_survey, survey_id):
#     """ automatically query the qualtrics survey data
#     guide https://community.alteryx.com/t5/Alteryx-Designer-Discussions/Python-Tool-Downloading-Qualtrics-Survey-Data-using-Python-API/td-p/304898 """

#     # Setting user Parameters
#     api_token = "zI0snlFFi3ym5HCb8aiax8zPjfNr8CuP9Xo6CucZ"
#     file_format = "csv"
#     data_center = 'qfreeaccountssjc1.sjc1' # "<Organization ID>.<Datacenter ID>"

#     # Setting static parameters
#     request_check_progress = 0
#     progress_status = "in progress"
#     base_url = "https://{0}.qualtrics.com/API/v3/responseexports/".format(data_center)
#     headers = {
#         "content-type": "application/json",
#         "x-api-token": api_token,
#     }

#     # Step 1: Creating Data Export
#     download_request_url = base_url
#     download_request_payload = '{"format":"' + file_format + '","surveyId":"' + survey_id + '"}' # you can set useLabels:True to get responses in text format
#     download_request_response = requests.request("POST", download_request_url, data=download_request_payload, headers=headers)
#     progress_id = download_request_response.json()["result"]["id"]
#     # print(download_request_response.text)

#     # Step 2: Checking on Data Export Progress and waiting until export is ready
#     while request_check_progress < 100 and progress_status != "complete":
#         request_check_url = base_url + progress_id
#         request_check_response = requests.request("GET", request_check_url, headers=headers)
#         request_check_progress = request_check_response.json()["result"]["percentComplete"]

#     # Step 3: Downloading file
#     request_download_url = base_url + progress_id + '/file'
#     request_download = requests.request("GET", request_download_url, headers=headers, stream=True)

#     # Step 4: Unzipping the file
#     zipfile.ZipFile(io.BytesIO(request_download.content)).extractall(dir_save_survey)
#     print('Downloaded qualtrics survey')

# # if __name__ == "__main__":

# path = "/Users/emilydoherty/Desktop"
# survey_id = "SV_7QcNXdJrcpd7bBs"

# get_qualtrics_survey(dir_save_survey = path, survey_id = survey_id)