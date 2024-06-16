from dotenv import load_dotenv
import os
load_dotenv()

secret_key = os.environ.get('SECRET_KEY')

usernames = os.environ.get('USERNAMES').split(',')
passwords = os.environ.get('PASSWORDS').split(',')

username_password_pairs = {usernames[i]:passwords[i] for i in range(min(len(usernames), len(passwords)))}
