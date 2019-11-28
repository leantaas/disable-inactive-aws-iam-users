import slack
import boto3
import json
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
iam = boto3.client('iam')


def lambda_handler(event, context):
    print(os.environ)
    today = datetime.now()
    num_of_days = os.environ['NO_OF_DAYS']
    webhook = os.environ['WEBHOOK_URL']
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
        except ClientError as e:
            print(user + " is already disabled")

    message = ""
    for index, value in enumerate(slack_user_list):
        message = message + str(index + 1) + "." + value + "\n"

    if len(slack_user_list) > 0:
        slack.message("green", "Disabled Inactive IAM Users",
                      "Below user are not active for " + num_of_days + " days", message, webhook)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Disabled Inactive IAM Users Execution successful",
        }),
    }
