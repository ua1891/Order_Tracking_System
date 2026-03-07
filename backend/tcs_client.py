import requests
import logging

logger = logging.getLogger(__name__)

TCS_API_URL = "https://api.tcscourier.com/sandbox/track/v1/shipments/detail"
CLIENT_ID = "YOUR_CLIENT_ID" # Will be replaced or configured via env in production

REQUEST_TIMEOUT = 10
SUCCESS_STATUS_CODE = "0200"

def get_tracking_details(tracking_number: str) -> dict:
    """Fetch tracking details from TCS API."""
    headers = {
        "X-IBM-Client-Id": CLIENT_ID,
        "Accept": "application/json"
    }
    params = {
        "consignmentNo": tracking_number
    }
    
    try:
        response = requests.get(TCS_API_URL, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        # Sandbox API might return specific codes. But according to Swagger, 200 is successful.
        if response.status_code == 200:
            data = response.json()
            # Swagger schema outlines returned status is in 'returnStatus', and actual reply in 'TrackDetailReply'
            if data.get('returnStatus', {}).get('code') == SUCCESS_STATUS_CODE:
                return data.get('TrackDetailReply')
            else:
                logger.warning(f"TCS API returned non-success code for {tracking_number}: {data.get('returnStatus')}")
                return None
        else:
            logger.error(f"Error fetching tracking details for {tracking_number}: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception fetching tracking details for {tracking_number}: {e}")
        return None
