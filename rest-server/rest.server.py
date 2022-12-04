

import json
from pickle import APPEND as app
from urllib import request
import base64
from flask import Flask, request
import jsonpickle
import base64
import  redis
import os
from minio import Minio
import os,sys
import hashlib
import io


#instantiate redis
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
#redisClient.flushdb()

#instantiate minio
minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
print("{} {} {}".format(minioHost, minioUser, minioPasswd))

minioclient = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

bucketname="queue"
if not minioclient.bucket_exists(bucketname):
    print(f"Create bucket {bucketname}")
    minioclient.make_bucket(bucketname)

def log_debug(message):
    print("DEBUG:", message, file=sys.stdout)
    redisClient.lpush('logging', message)

def log_info(message):
    print("INFO:", message, file=sys.stdout)
    redisClient.lpush('logging', message)

app = Flask(__name__)

@app.route('/apiv1/separate/', methods=['POST'])
def separate():
    log_debug('in separate method')
    data = json.loads(request.data.decode('utf-8'))
    mp3 = base64.b64decode(data['mp3'])
    songhash=hashlib.sha256(mp3)
    digest = songhash.hexdigest()
    print(digest)
    songbytes= io.BytesIO(mp3)
    length = len(mp3)
    print('about to call put-object')
    minioclient.put_object(bucketname, digest, songbytes, length=length)
    print('put object successful, about to call redis lpush')
    redisClient.lpush('toWorker', digest)
    print('redis successful')
    response= {'hash' : digest,
            'reason' : 'Song in queue for separation'}
    log_debug(response['hash']+ '.' + response['reason'])
    response_pickled = jsonpickle.encode(response)
    return response_pickled


@app.route('/apiv1/queue/', methods=['GET'])
def queue():
    queue= []
    log_debug('in queue method')
    for i in range(0, redisClient.llen('toWorker')):
        queue.append(str(redisClient.lindex('toWorker',i).decode('utf-8')))
    response= {'queue': queue}
    response_pickled = jsonpickle.encode(response)
    # log_info('queue info') fix later
    return response_pickled


@app.route('/apiv1/track/<string:songhash>/<int:track>', methods=['GET'])
def track(songhash, track):
    response={'track': track,
            'songhash': songhash}
    return response

@app.route('/apiv1/remove/<string:songhash>/<int:track>', methods=['DELETE'])
def delete(songhash, track):
    response={'track': track,
            'songhash': songhash}
    return response

#start flask
app.run(host="0.0.0.0",port=5000)
