import argparse
import requests

from io import BytesIO
from openai import OpenAI

# Replace these with your actual API keys and access tokens
OPENAI_API_KEY = ''
MEURAL_ACCESS_TOKEN = ''

# Replace with your canvas id name
MEURAL_CANVAS_ID = 'cezanne-000'

client = OpenAI(api_key=OPENAI_API_KEY)
def generate_image(prompt):
    """
    Generate an image using DALL-E based on a given prompt.
    """
    response = client.images.generate(prompt=prompt,
    n=1,  # Number of images to generate
    size="1024x1024",
    model="dall-e-3")

    # Assuming the response contains a URL to the generated image
    image_url = response.data[0].url
    return image_url

def add_to_playlist(item_id, playlist_id, token):
    """
    Add an uploaded image to a specific playlist on Meural.
    """
    add_to_playlist_url = f"https://api.meural.com/v0/galleries/{playlist_id}/items/{item_id}"
    headers = {
        'Authorization': f'{token}'
    }
    response = requests.post(add_to_playlist_url, headers=headers, json={})

    if response.status_code != 200:
        raise Exception("Failed to add image to playlist: " + response.text)

    return "Image added to playlist successfully"

def send_to_canvas(playlist_id, canvas_id, token):
    """
    Send a playlist to the Meural Canvas.
    """
    send_to_canvas_url = f"https://api.meural.com/v0/devices/{canvas_id}/galleries/{playlist_id}"
    headers = {
        'Authorization': f'{token}'
    }
    response = requests.post(send_to_canvas_url, headers=headers, json={})
    print(send_to_canvas_url)
    if response.status_code != 200:
        raise Exception("Failed to send playlist to canvas: " + response.text)

    return "Playlist sent to canvas successfully"

def upload_to_meural(image_url):
    """
    Download an image from a URL and upload it to Meural.
    """
    meural_upload_url = "https://api.meural.com/v0/items"  # Replace with the actual URL
    headers = {
        'Authorization': f'{MEURAL_ACCESS_TOKEN}'
    }

    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception("Failed to download image from URL")

    # Upload the image to Meural
    files = {'image': ('image.jpg', BytesIO(response.content), 'image/jpeg')}
    upload_response = requests.post(meural_upload_url, headers=headers, files=files)

    if upload_response.status_code != 201:
        raise Exception("Failed to upload image to Meural: " + upload_response.text)

    # Assuming the response contains the ID of the uploaded item
    item_id = upload_response.json().get('data').get('id')
    return item_id

def main(prompt, send_to_canvas_flag):
    image_url = generate_image(prompt)
    item_id = upload_to_meural(image_url)
    print(f"Image uploaded. Item ID: {item_id}")

    # Replace 'GPT_PLAYLIST_ID' with the actual ID of your 'GPT' playlist
    GPT_PLAYLIST_ID = '000000'
    result = add_to_playlist(item_id, GPT_PLAYLIST_ID, MEURAL_ACCESS_TOKEN)
    print(result)

    if send_to_canvas_flag:
        # Replace with your canvas ID (from https://my.meural.netgear.com/canvases/CANVAS_ID_HERE/)
        MEURAL_CANVAS_ID='00000'
        result = send_to_canvas(GPT_PLAYLIST_ID, MEURAL_CANVAS_ID, MEURAL_ACCESS_TOKEN)
        print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload an image to Meural and optionally send it to a canvas.")
    parser.add_argument("prompt", type=str, help="The prompt to generate an image")
    parser.add_argument("--send_to_canvas", action="store_true", help="Flag to send the playlist to the Meural Canvas")

    args = parser.parse_args()

    main(args.prompt, args.send_to_canvas)
