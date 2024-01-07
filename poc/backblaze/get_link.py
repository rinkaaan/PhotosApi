from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve B2 credentials from environment variables
b2_account_id = os.getenv("B2_ACCOUNT_ID")
b2_application_key = os.getenv("B2_APPLICATION_KEY")

info = InMemoryAccountInfo()

if __name__ == "__main__":
    b2_api = B2Api(info)
    b2_api.authorize_account("production", b2_account_id, b2_application_key)
    bucket = b2_api.get_bucket_by_name("nguylinc")
    # url = bucket.get_download_url("hello/world/test.mp4")

    url = bucket.get_download_url("ipas/photos.ipa")
    print(url)
    file = bucket.get_file_info_by_name("ipas/photos.ipa")
    print(file.size)

    url = bucket.get_download_url("altstore.json")
    print(url)
