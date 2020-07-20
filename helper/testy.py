# -*- coding: utf-8 -*-
import boto3

def delete_versions(bucket, objects=None): # `objects` is either list of str or None
  bucket = boto3.resource('s3').Bucket(bucket)
  if objects: # delete specified objects
    [version.delete() for version in bucket.object_versions.all() if version.object_key in objects]
  else: # or delete all objects in `bucket`
    [version.delete() for version in bucket.object_versions.all()]