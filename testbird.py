import requests
import json

# Bird API configuration
API_KEY = "TZnsd04cQ8RnxVDr8iZXBOG484rQnAKI7veY"
WORKSPACE_ID = "29aec675-550b-4c5e-a7a6-c429b93a4c5b"
CHANNEL_ID = "07c74ef2-c9c9-56fe-bb0b-5a4e523c0076"

# API endpoint
url = f"https://api.bird.com/workspaces/{WORKSPACE_ID}/channels/{CHANNEL_ID}/messages"

# Request headers
headers = {
    "Authorization": f"AccessKey {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "*/*"
}

# Correct message payload according to Bird API docs
payload = {
    "receiver": {
        "contacts": [
            {
                "identifierValue": "+1234567890"  # Recipient phone number in E.164 format
            }
        ]
    },
    "body": {
        "type": "text",
        "text": {
            "text": "Hello! This is a test message sent via Bird API."
        }
    }
}

# Send the SMS
try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    print("SMS sent successfully!")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except requests.exceptions.RequestException as e:
    print(f"Error sending SMS: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Error details: {e.response.text}")


# Function version for reusability
def send_sms(phone_number, message, api_key, workspace_id, channel_id):
    """
    Send an SMS via Bird API
    
    Args:
        phone_number (str): Recipient phone number in E.164 format (e.g., +1234567890)
        message (str): Message text to send
        api_key (str): Your Bird API access key
        workspace_id (str): Your Bird workspace ID
        channel_id (str): Your SMS channel ID
    
    Returns:
        dict: API response or None if error
    """
    url = f"https://api.bird.com/workspaces/{workspace_id}/channels/{channel_id}/messages"
    
    headers = {
        "Authorization": f"AccessKey {api_key}",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    
    payload = {
        "receiver": {
            "contacts": [
                {
                    "identifierValue": phone_number
                }
            ]
        },
        "body": {
            "type": "text",
            "text": {
                "text": message
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")
        return None


# Function to send MMS with image (for US/Canada numbers)
def send_mms_image(phone_number, image_url, text, api_key, workspace_id, channel_id):
    """
    Send an MMS with image via Bird API (US/Canada numbers only)
    
    Args:
        phone_number (str): Recipient phone number in E.164 format
        image_url (str): URL of the image to send
        text (str): Optional text message to accompany the image
        api_key (str): Your Bird API access key
        workspace_id (str): Your Bird workspace ID
        channel_id (str): Your SMS channel ID (must be MMS-capable)
    
    Returns:
        dict: API response or None if error
    """
    url = f"https://api.bird.com/workspaces/{workspace_id}/channels/{channel_id}/messages"
    
    headers = {
        "Authorization": f"AccessKey {api_key}",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    
    payload = {
        "receiver": {
            "contacts": [
                {
                    "identifierValue": phone_number
                }
            ]
        },
        "body": {
            "type": "image",
            "image": {
                "images": [
                    {
                        "mediaUrl": image_url
                    }
                ],
                "text": text
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")
        return None


# Function to send using a template
def send_sms_template(phone_number, project_id, template_params, api_key, workspace_id, channel_id):
    """
    Send an SMS using a Bird template
    
    Args:
        phone_number (str): Recipient phone number in E.164 format
        project_id (str): Template project ID from Bird Studio
        template_params (dict): Dictionary of template parameters (e.g., {"name": "Robert"})
        api_key (str): Your Bird API access key
        workspace_id (str): Your Bird workspace ID
        channel_id (str): Your SMS channel ID
    
    Returns:
        dict: API response or None if error
    """
    url = f"https://api.bird.com/workspaces/{workspace_id}/channels/{channel_id}/messages"
    
    headers = {
        "Authorization": f"AccessKey {api_key}",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    
    # Convert template params to the required format
    parameters = [
        {"type": "string", "key": key, "value": value}
        for key, value in template_params.items()
    ]
    
    payload = {
        "receiver": {
            "contacts": [
                {
                    "identifierValue": phone_number
                }
            ]
        },
        "template": {
            "projectId": project_id,
            "version": "latest",
            "locale": "en",
            "parameters": parameters
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error details: {e.response.text}")
        return None


# Example usage
if __name__ == "__main__":
    # Test basic SMS
    result = send_sms(
        phone_number="+56977997769",
        message="Hello Bennyboy!",
        api_key=API_KEY,
        workspace_id=WORKSPACE_ID,
        channel_id=CHANNEL_ID
    )
    
    if result:
        print("Message sent successfully!")
        print(json.dumps(result, indent=2))