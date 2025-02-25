import boto3
from modules.General_func import who_am_i, clear_terminal
import uuid
import concurrent.futures
import tkinter as tk
from tkinter import filedialog


# Sets the bucket policy to be public or private depends on privacy_set
def set_privacy(privacy_set, client, bucket_name):
    client.delete_bucket_policy(Bucket=bucket_name)
    if privacy_set == "public":
        client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False
            }
        )
        print(f"Bucket '{bucket_name}' is now public.")
    else:
        client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            }
        )
        print(f"Bucket '{bucket_name}' is now private.")


# Validates the privacy
def privacy(client, bucket_name):
    privacy_list = ["private", "public", ""]
    sure_list = ["yes", "y"]
    print("(Make sure you type private or public!)")
    private_key = input("Type whether S3 should be private or public (default is private): ").lower()
    while private_key not in privacy_list:
        print("(Make sure you type private or public!)")
        private_key = input("Type whether S3 should be private or public: ").lower()
    if private_key == "public":
        make_sure = input("Are you sure you want to create public bucket?\nType yes to proceed: ")
        if make_sure.lower() in sure_list:
            return set_privacy("public", client, bucket_name)
        else:
            private_key = ""
    return set_privacy("private", client, bucket_name)


# Adds Owner and CreatedBy tags
def add_tag(client, bucket_name, username):
    client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': [
                {'Key': 'Owner', 'Value': username},
                {'Key': 'CreatedBy', 'Value': f'CLI {username}'}
            ]
        }
    )


# Creates the bucket
def create_bucket(s3):
    username = who_am_i().lower()
    unique_id = uuid.uuid4().hex[:6]
    bucket_name = f"s3-{username}-{unique_id}"
    s3.create_bucket(Bucket=bucket_name)
    add_tag(s3, bucket_name, username)
    privacy(s3, bucket_name)


# If was created by this user gets back the bucket name
def get_bucket_if_owner(s3, bucket_name, username):
    try:
        tag_response = s3.get_bucket_tagging(Bucket=bucket_name)
        tags = {tag['Key']: tag['Value'] for tag in tag_response.get('TagSet', [])}
        if tags.get('Owner', '').lower() == username and tags.get('CreatedBy', '') == f"CLI {username.lower()}":
            return bucket_name
    except:
        pass
    return None


# List all buckets created by this user and by CLI
def list_buckets(s3):
    username = who_am_i()
    response = s3.list_buckets()
    bucket_names = [bucket['Name'] for bucket in response['Buckets']]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda bucket: get_bucket_if_owner(s3, bucket, username), bucket_names)

    bucket_list = [bucket for bucket in results if bucket]

    if not bucket_list:
        print("No buckets found.")
    return bucket_list


# Validates you chose only bucket from the list
def valid_bucket(client):
    filtered_buckets = list_buckets(client)
    chosen_bucket = ""
    if filtered_buckets:
        filtered_buckets_string = "This is all the available buckets for you:"
        for bucket in filtered_buckets:
            filtered_buckets_string += f"\n{bucket}"
        print(filtered_buckets_string)
        chosen_bucket = input("Enter your choice, press Enter to exit: ")
        while chosen_bucket and chosen_bucket not in filtered_buckets:
            print(filtered_buckets_string)
            chosen_bucket = input("Enter your choice, press Enter to exit: ")
    return chosen_bucket


# Deletes all objects in a bucket
def delete_all_objects_in_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.objects.all().delete()
        if bucket.object_versions:
            bucket.object_versions.all().delete()
        print(f"AlL Objects  in {bucket_name} have been deleted. ")
    except Exception as e:
        print(f"Error deleting objects: {e} ")
        return


# Deletes buckets created by this user and by CLI
def delete_bucket(client, bucket_name):
    yes_list = ["yes", "y"]
    sure = input(f"Are you sure you want to delete {bucket_name}?\nType yes to proceed: ")
    if sure.lower() in yes_list:
        delete_all_objects_in_bucket(bucket_name)
        client.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' deleted successfully.")
    else:
        print("Deleting the bucket aborted returning to menu.")


# Opens a file explorer window to select a file
def select_file():
    root = tk.Tk()
    root.title("File Selector")
    root.geometry("300x150")
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    file_path = filedialog.askopenfilename(title="Select a file")
    root.destroy()
    return file_path


# Uploads a selected file to an S3 bucket.
def upload_to_s3(s3, bucket_name):
    file_path = select_file()
    if not file_path:
        print("No file selected. Exiting.")
        return
    object_name = file_path.split("/")[-1]
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"File {file_path} uploaded to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Error uploading file: {e}")


# CLI for existing buckets
def manage_buckets(client, bucket_name):
    flag_done = False
    options = ["1", "2", "3", "4"]
    menu = (fr"""How do you want to manage:
1. Upload a file to {bucket_name}.
2. Change privacy setting for {bucket_name}.
3. Delete all files from {bucket_name}.
4. Go back to S3 menu.
Enter your choice:
-------------------------------
""")
    UPLOAD = "1"
    CHANGEPRIVACY = "2"
    DELETE = "3"
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            what_to_do = input(menu)
        clear_terminal()
        if what_to_do == UPLOAD:
            upload_to_s3(client, bucket_name)
            input(f"Enter anything to go back to managing {bucket_name}: ")
        elif what_to_do == CHANGEPRIVACY:
            privacy(client, bucket_name)
            input(f"Enter anything to go back to managing {bucket_name}: ")
        elif what_to_do == DELETE:
            delete_all_objects_in_bucket(bucket_name)
            input(f"Enter anything to go back to managing {bucket_name}: ")
        else:
            flag_done = True


# Interactive CLI for buckets
def cli_bucket():
    client = boto3.client('s3')
    flag_done = False
    options = ["1", "2", "3", "4"]
    CREATE = "1"
    MANAGE = "2"
    DELETE = "3"
    menu = (r"""What do you want to do:
1. Create a bucket.
2. Manage an existing bucket.
3. Delete an existing bucket.
4. Go back to main menu.
Enter your choice:
-------------------------------
""")
    while not flag_done:
        clear_terminal()
        what_to_do = input(menu)
        while what_to_do not in options:
            clear_terminal()
            what_to_do = input(menu)
        if what_to_do == CREATE:
            create_bucket(client)
            input("Enter anything to go back to S3 menu: ")
        elif what_to_do == MANAGE:
            bucket_name = valid_bucket(client)
            if bucket_name:
                manage_buckets(client, bucket_name)
        elif what_to_do == DELETE:
            print("***You are going to ***DELETE*** the chosen bucket!!!***")
            bucket_name = valid_bucket(client)
            if bucket_name:
                delete_bucket(client, bucket_name)
            input("Enter anything to go back to S3 menu: ")
        else:
            flag_done = True

