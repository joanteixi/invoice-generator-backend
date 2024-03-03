import os
import json
import aiohttp
from dotenv import load_dotenv

base_path =os.path.join(os.getcwd())

load_dotenv(dotenv_path=os.path.join(base_path, 'instance', '.env'))


async def send_message(phone_number, url):
    
    data = get_text_message_input(phone_number, url)
    
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
        }
  
    async with aiohttp.ClientSession() as session:
        url = f"https://graph.facebook.com/{os.getenv('WHATSAPP_VERSION')}/{os.getenv('WHATSAPP_NUMBER_ID')}/messages"
        
        try:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    
                
                    print("Status:", response.status)
                    print("Content-type:", response.headers['content-type'])

                    html = await response.text()
                    
                    print("Body:", html)
                
                else:
                    print(response.status)          
                    print(response)        
        
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))

def get_text_message_input(recipient, url):
  return json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "preview_url": True,
    "to": recipient,
    "type": "template",
    "template": {
        "name": "factura", 
        "language": {
            "code": "ca"
        },
        "components": [
         {
           "type": "body",
           "parameters": [
               {
                   "type": "text",
                   "text": url
               }
           ]
         }
       ]
    }
    
  })