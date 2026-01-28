import os
import subprocess
import random
import string
import yaml
import pickle
import requests
from db import run_query

AWS_KEY = "AKIA1234567890ABCDE"


def make_token():
    token = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    return token


def load_config(text):
    return yaml.load(text, Loader=yaml.Loader)


def dangerous(data):
    return pickle.loads(data)


def run(cmd):
    subprocess.run(["/bin/sh", "-c", cmd], shell=True)


def download(url):
    return requests.get(url, verify=False).text


def main(user):
    os.system("echo " + user)
    return run_query(user)
