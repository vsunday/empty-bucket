# -*- coding: utf-8 -*-
import boto3, json, traceback, threading
from urllib.request import urlopen, Request

cf = boto3.client('cloudformation')
s3 = boto3.resource('s3')

def empty_buckets(stackname):
  # get bucket names under `stackname`
  rs = [r['PhysicalResourceId'] for r in cf.list_stack_resources(StackName=stackname)['StackResourceSummaries'] if r['ResourceType'] == 'AWS::S3::Bucket']
  
  threads = []
  for r in rs:
    t = threading.Thread(target=empty_bucket, args=(r,))
    threads.append(t)
    t.start()
  [t.join() for t in threads]
  
def empty_bucket(bucket):
  return [object.delete() for object in s3.Bucket(bucket).object_versions.all()]
      
def send_response(url, responseObjects):
  req = Request(url,
    data=bytes(json.dumps(responseObjects), encoding='utf-8'),
    headers={'Content-Type': 'application/json'},
    method='PUT')
  return urlopen(req)
  
def handler(event, context):
  status = 'FAILED'
  reason = ''
  try:
    if event['RequestType'] == 'Delete':
      empty_buckets(event['StackId'])
    status = 'SUCCESS'
  except Exception as e:
    print('some error')
    print(e)
    reason = 'See CloudWatch Logs!!!'
  except:
    print('yet another error')
    traceback.print_exc()
    reason = 'See CloudWatch Logs!!!'
  finally:
    responseObjects = {
      'Status': status,
      'Reason': reason,
      'PhysicalResourceId': event.get('PhysicalResourceId', False) or event['RequestId'],
      'StackId': event['StackId'],
      'RequestId': event['RequestId'],
      'LogicalResourceId': event['LogicalResourceId']
    }
    
    send_response(event['ResponseURL'], responseObjects)