import base64
import redis
import os
from minio import Minio
import os,sys

## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

#to do instantiate minio

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"
print("{} {} {}".format(minioHost, minioUser, minioPasswd))

minioclient = Minio(minioHost,
               secure=False,
               access_key=minioUser,
               secret_key=minioPasswd)

def log_debug(message):
    print("DEBUG:", message, file=sys.stdout)
    redisClient.lpush('logging', message)

def log_info(message):
    print("INFO:", message, file=sys.stdout)
    redisClient.lpush('logging', message)

while True:
    try:
        work = redisClient.blpop("toWorker", timeout=0)
        ##
        ## Work will be a tuple. work[0] is the name of the key from which the data is retrieved
        ## and work[1] will be the text log message. The message content is in raw bytes format
        ## e.g. b'foo' and the decoding it into UTF-* makes it print in a nice manner.
        ##
        songhash =  work[1].decode('utf-8')
        cwd=os.getcwd()
        print('songhash created')
        minioclient.fget_object('queue', songhash, cwd+'/{}.mp3'.format(songhash))
        print('minioclient fgetobject successful')
        os.system('python3 -m demucs.separate --mp3 --out /data/output ' + '{}.mp3'.format(songhash))
        print('output successful')
    except Exception as exp:
        print(f"Exception raised in log loop: {str(exp)}")
    sys.stdout.flush()
    sys.stderr.flush()
