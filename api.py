import virustotal_python
import hashlib
import asyncio
from base64 import urlsafe_b64encode
from decouple import config


#############
#   Keys    #
#############
API_KEY = config('API_KEY')


#############
# Functions #
#############
def hash_file(file_name):
    hash_object = hashlib.sha256()

    with open(file_name, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            hash_object.update(chunk)

    print(hash_object.hexdigest())
    return hash_object.hexdigest()


#############
# EndPoints #
#############
async def scan_url(url):
    with virustotal_python.Virustotal(API_KEY) as vtotal:
        try:
            resp = vtotal.request("urls", data={"url":url}, method='POST')
            url_id = urlsafe_b64encode(url.encode()).decode().strip("=")

            report = vtotal.request(f"urls/{url_id}")

            count = 1
            while report.data['attributes']['last_analysis_results'] == {}:
                print(count)
                count = count + 1
                await asyncio.sleep(10)
                report = vtotal.request(f"urls/{url_id}")

            return report.data
        except virustotal_python.VirustotalError as err:
            await asyncio.sleep(10)
            report = vtotal.request(f"urls/{url_id}")

            count = 1
            while report.data['attributes']['last_analysis_results'] == {}:
                print(count)
                count = count + 1
                await asyncio.sleep(10)
                report = vtotal.request(f"urls/{url_id}")

            return report.data


async def scan_file(file_name):
    files = {"file": (file_name, open(file_name, "rb"))}

    with virustotal_python.Virustotal(API_KEY) as vtotal:
        resp = vtotal.request("files", files=files, method="POST")

        return resp.data


async def retrieve_file(file_name):
    file_hash = hash_file(file_name)

    with virustotal_python.Virustotal(API_KEY) as vtotal:
        resp = vtotal.request(f"files/{file_hash}")

        count = 1
        while resp.data['attributes']['last_analysis_results'] == {}:
            print(count)
            count = count + 1
            await asyncio.sleep(30)
            resp = vtotal.request(f"files/{file_hash}")

        return resp.data


#############
# Debugging #
#############
if __name__ == "__main__":
    print("Debugging:")
