import json
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

import slack

iam = boto3.client('iam')


def lambda_handler(event, context):
    print(os.environ)
    today = datetime.now()
    num_of_days = os.environ.get('NO_OF_DAYS')
    webhook = os.environ.get('WEBHOOK_URL')
    delete_access_keys = os.environ.get('DELETE_ACCESS_KEYS')
    if num_of_days:
        print(num_of_days)

        iam_users = list(filter(lambda user: 'PasswordLastUsed' in user,
                                iam.list_users()['Users']))

        inactive_user_list = list(filter(lambda inactive_user: abs((
            today.date() - inactive_user['PasswordLastUsed'].date()).days) > int(num_of_days), iam_users))

        user_list = list(map(lambda u: u['UserName'], inactive_user_list))
        slack_user_list = []
        print(user_list)
        for user in user_list:
            try:
                iam.delete_login_profile(UserName=user)
                slack_user_list.append(user)
            except ClientError:
                print(user + " is already disabled")

        if delete_access_keys:
            for user in user.list:
                try:
                    for key in iam.list_access_keys(
                            UserName=user).get('AccessKeyMetadata'):
                        iam.delete_access_keys(
                            UserName=user,
                            AccessKeyId=key)
                except ClientError as e:
                    print(e)

        message = ""
        for index, value in enumerate(slack_user_list):
            message = message + str(index + 1) + "." + value + "\n"

        if slack_user_list and webhook:
            slack.message("green", "Disabled Inactive IAM Users",
                          "Below user are not active for " + num_of_days + " days", message, webhook)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Disabled Inactive IAM Users Execution successful",
            }),
        }
    return {
        "statusCode": 500,
        "body": json.dumps({
            "message": "NumberOfDays unset"
        })
    }
