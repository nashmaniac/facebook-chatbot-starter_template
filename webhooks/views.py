from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
import re
import json
import random
import requests

class MessengerApiView(APIView):

    def parse_and_send_fb_message(self, fbid, username, full_name, recevied_message):
        # Remove all punctuations, lower case the text and split it based on space
        tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
        msg = None
        # for token in tokens:
        #     if token in LOGIC_RESPONSES:
        #         msg = random.choice(LOGIC_RESPONSES[token])
        #         break

        if not msg:
            msg = 'Hey %s(%s), Welcome, Please drop your query'%(username, full_name)
        endpoint = f"{getattr(settings, 'FB_ENDPOINT')}/me/messages?access_token={getattr(settings, 'FACEBOOK_PAGE_TOKEN')}"
        response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": msg}})
        status = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            data=response_msg)
        print(status.json())
        return status.json()

    def get(self, request, *args, **kwargs):
        hub_mode = request.query_params.get('hub.mode')
        verify_token = request.query_params.get('hub.verify_token')
        hub_challenge = request.query_params.get('hub.challenge')
        if verify_token != getattr(settings, 'VERIFICATION_TOKEN'):
            data = dict(
                message='Not authenticated'
            )
            return HttpResponse(data, status=403)
        return HttpResponse(hub_challenge, status=200)

    def post(self, request, *args, **kwargs):
        for entry in request.data.get('entry'):
            for message in entry.get('messaging'):
                if 'message' in message:
                    fb_user_id = message['sender']['id']  # sweet!

                    user_urls = 'https://graph.facebook.com/%s?fields=first_name,last_name,name,profile_pic&access_token=%s'\
                                %(fb_user_id, getattr(settings, 'FACEBOOK_PAGE_TOKEN'))
                    r = requests.get(user_urls)
                    user_info = r.json()
                    fb_user_txt = message['message'].get('text')
                    if fb_user_txt:
                        self.parse_and_send_fb_message(fb_user_id,user_info.get('name'), '%s %s'%(user_info.get('first_name'), user_info.get('last_name')), fb_user_txt)
        return HttpResponse("Success", status=200)
