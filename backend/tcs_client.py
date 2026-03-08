import requests
import logging

logger = logging.getLogger(__name__)

import os

AUTH_API_URL = "https://devconnect.tcscourier.com/auth/api/auth"
TRACKING_API_URL = "https://devconnect.tcscourier.com/tracking/api/Tracking/GetDynamicTrackDetail"

# Configured in environment
TCS_CLIENT_ID = os.environ.get("TCS_CLIENT_ID", "")
TCS_CLIENT_SECRET = os.environ.get("TCS_CLIENT_SECRET", "")

_access_token = None

def get_auth_token():
    global _access_token
    if _access_token:
        # In a robust implementation, check expiry here
        return _access_token
        
    try:
        payload = {
            "clientid": TCS_CLIENT_ID,
            "clientsecret": TCS_CLIENT_SECRET
        }
        res = requests.get(AUTH_API_URL, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") is True:
                _access_token = data.get("result", {}).get("accessToken")
                return _access_token
    except Exception as e:
        logger.error(f"Failed to get auth token: {e}")
    return None

def parse_tracking_summary(details: dict) -> dict:
    """Extract relevant summary from raw tracking details."""
    summary = {
        'current_status': 'PENDING',
        'origin': None,
        'destination': None
    }
    
    if not details:
        return summary
        
    if 'checkpoints' in details and len(details['checkpoints']) > 0:
        summary['current_status'] = details['checkpoints'][0].get('status', 'PENDING')
        
        # Alternatively, fetch from summary text just in case
        text_summary = details.get('shipmentsummary', '')
        if 'Current Status: ' in text_summary:
            summary['current_status'] = text_summary.split('\n')[0].replace('Current Status: ', '').strip()
            
    if 'shipmentinfo' in details and details['shipmentinfo']:
        track_info = details['shipmentinfo'][0]
        origin_city = track_info.get('origin', '')
        origin_country = track_info.get('origincountry', '')
        dest_city = track_info.get('destination', '')
        dest_country = track_info.get('destinationcountry', '')
        
        summary['origin'] = f"{origin_city}, {origin_country}".strip(', ')
        summary['destination'] = f"{dest_city}, {dest_country}".strip(', ')
        
    return summary

def get_tracking_details(tracking_number: str, retry=True) -> dict:
    """Fetch tracking details from TCS API."""
    global _access_token
    token = get_auth_token()
    if not token:
        logger.error(f"No valid TCS auth token for querying {tracking_number}.")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    payload = {
        "consignee": [tracking_number]
    }
    
    try:
        response = requests.get(TRACKING_API_URL, headers=headers, json=payload, timeout=10)
        
        # Handle Token Expiration
        if response.status_code == 401 and retry:
            logger.warning("Token expired or unauthorized, retrying fetch...")
            _access_token = None
            return get_tracking_details(tracking_number, retry=False)
            
        if response.status_code == 200:
            data = response.json()
            if data.get('message') == 'SUCCESS':
                return data
            else:
                logger.warning(f"TCS API Tracking returned message for {tracking_number}: {data.get('message')}")
                return None
        else:
            logger.error(f"Error fetching tracking details for {tracking_number}: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception fetching tracking details for {tracking_number}: {e}")
        return None
