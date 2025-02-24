import boto3
import os
import platform


# Returns you IAM username
def who_am_i():
    iam = boto3.client("iam")
    try:
        user_response = iam.get_user()
        return user_response['User']['UserName']
    except Exception as e:
        print(f"Error fetching IAM user: {e}")
        return []


# Cleans the terminal
def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

