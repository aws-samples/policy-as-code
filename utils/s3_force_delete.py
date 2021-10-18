import boto3
import argparse
import sys
import argparse
import botocore

def delete_bucket(session, bucket_name):

    s3 = session.resource('s3')

    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    try:
        bucket.object_versions.delete()
    except:
        pass
    # for obj in bucket.objects.all():
    #    obj.delete()
    bucket.objects.all().delete()
    bucket.delete()

    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bucket", type=str, help="S3 bucket to be deleted")
    parser.add_argument("-p", "--profile", type=str, help="AWS profile used to execute command")
    args = parser.parse_args()
    session = boto3.session.Session()
    bucket = args.bucket
    if args.profile:
        session = boto3.session.Session(profile_name=args.profile)
    try:
        delete_bucket(session, args.bucket)
        print("Deleting Bucket: s3://{}".format(bucket))
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"NoSuchBucket: {bucket}")   
            return
        else:
            print(e.message)
            raise e


    return



if __name__ == '__main__':
    main()