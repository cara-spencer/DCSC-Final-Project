# import json
# from pickle import APPEND as app
# from urllib import request
# import base64
from flask import Flask, request
# import jsonpickle
# import base64
# import  redis
# import os
# from minio import Minio
# import os,sys
# import hashlib
# import io
#from QualtricsAPI.Survey import Responses

# #instantiate redis
# redisHost = os.getenv("REDIS_HOST") or "localhost"
# redisPort = os.getenv("REDIS_PORT") or 6379
#
# redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
# #redisClient.flushdb()
#
# #instantiate minio
# minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
# minioUser = os.getenv("MINIO_USER") or "rootuser"
# minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
# print("{} {} {}".format(minioHost, minioUser, minioPasswd))
#
# minioclient = Minio(minioHost,
#                secure=False,
#                access_key=minioUser,
#                secret_key=minioPasswd)
#
# bucketname="queue"
# if not minioclient.bucket_exists(bucketname):
#     print(f"Create bucket {bucketname}")
#     minioclient.make_bucket(bucketname)

app = Flask(__name__)

# @app.route('/apiv1/getsurvey/', methods=['GET'])
# def getsurvey(): ###Change to getsurvey
#    #establish creds using the user's api token and datacenter they enter
#     from QualtricsAPI.Setup import Credentials
#     #Create an instance of Credentials
#     c = Credentials()
#     token = request.args.get("token")
#     data_center = request.args.get("data_center")
#     directory_id = request.args.get("directory_id")
#     c.qualtrics_api_credentials(token='gEjVMlVLOJR33JJNnTQLOQTJmwBr0OOGY8mseOum',data_center='ca1',directory_id='POOL_3EQ4ctAv5niLXRT')
#    #request to qualtrics api
#
#     #Create an instance
#     r = Responses()
#
#     #Call the method
#     df = r.get_questions(survey_id='SV_AFakeSurveyID')
#
#    #print the list of surveys in qualtrics so user can copy paste into cleansurvey
#     # log_debug('in separate method')
#     # data = json.loads(request.data.decode('utf-8'))
#     # mp3 = base64.b64decode(data['mp3'])
#     # songhash=hashlib.sha256(mp3)
#     # digest = songhash.hexdigest()
#     # print(digest)
#     # songbytes= io.BytesIO(mp3)
#     # length = len(mp3)
#     # print('about to call put-object')
#     # minioclient.put_object(bucketname, digest, songbytes, length=length)
#     # print('put object successful, about to call redis lpush')
#     # redisClient.lpush('toWorker', digest)
#     # print('redis successful')
#     # response= {'hash' : digest,
#     #         'reason' : 'Song in queue for separation'}
#     # log_debug(response['hash']+ '.' + response['reason'])
#     # response_pickled = jsonpickle.encode(response)
#     # return response_pickled


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


# @app.route('/apiv1/track/<string:songhash>/<int:track>', methods=['GET'])
# def track(songhash, track): # progress logs
#   #checks minio
#     response={'track': track,
#             'songhash': songhash}
#     return response

valid_args = ['datacenter', 'token', 'directory_id']
@app.route('/getSurvey', methods=['GET'])
def getSurvey():
    # Validate.
    args = request.args
    args = args.to_dict()
    for k,v in args.items():
        if k not in valid_args:
            return 'Bad Argument', 400
    if len(args) != 3:
        return 'Missing Argument', 400

    # Perform Task
    try:
        perform_stuff
    except QualtricException e: #check if qualtrics THROWS error codes; may need to parse response if not clear
        if e.code == 403:
            return "Qualtrics threw this error! {}".format(e)
    except otherex:
    except Exception e:
    finally:

    # return to user
    return args

print('hello')
#start flask
app.run(host="0.0.0.0",port=5000)
print('goodbye')

#to test:
#"localhost:5000/getSurvey?datacenter=ca1&token=123&directory_id=myid"