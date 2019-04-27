import os
import sys
import json
import urllib.parse
import random
import logging

import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, LocationMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, URITemplateAction
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

line_channel_secret_key = os.getenv('LINE_CHANNEL_SECRET_KEY', None)
line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', None)
if line_channel_secret_key is None:
    logger.error('Specify LINE_CHANNEL_SECRET_KEY as environment variable.')
    sys.exit(1)
if line_channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if google_places_api_key is None:
    logger.error('Specify GOOGLE_PLACES_API_KEY as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret_key)

google_places_api_base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"


def _get_spots(lat, lng):
    google_places_api_query = urllib.parse.urlencode({
        "key": google_places_api_key,
        "location": "%s, %s" % (lat, lng),
        "radius": 1500, # 1.5km,
        "language": "ja",
        "opennow": True,
        "types": "cafe"
    })
    request_url = google_places_api_base_url + google_places_api_query
    spots = []
    try:
        res = requests.get(request_url)
        result = json.loads(res.text)
        for spot in result["results"]:
            spots.append(spot)
    except:
        raise LineBotApiError
    return spots


def _carousel_view(spots, lat, lng):

    if len(spots) <= 0:
        return TextSendMessage(text="うーん...近くに今開いているカフェはないね！\nまた違うところで試してね！".strip())
    elif len(spots) > 10:
        spots = random.sample(spots, 10)
    random.Random().shuffle(spots)
    columns = [_create_carousel_column(spot, lat, lng) for spot in spots]
    view = [
        TextSendMessage(text="今開いているカフェが見つかったよ！".strip()),
        TemplateSendMessage(
            alt_text='CloSpots List',
            template=CarouselTemplate(columns=columns)
        )
    ]
    return view


def _create_carousel_column(spot, lat, lng):
    spot_name = spot["name"]
    spot_address = spot["vicinity"]
    spot_lat = spot["geometry"]["location"]["lat"]
    spot_lng = spot["geometry"]["location"]["lng"]

    google_search_url = "https://www.google.co.jp/search?" + urllib.parse.urlencode({"q": spot_name + " " + spot_address})
    google_map_route_url = "http://maps.google.com/maps?" + urllib.parse.urlencode({"saddr": str(lat) + "," + str(lng), "daddr": str(spot_lat) + "," + str(spot_lng), "dirflg": "w"})

    carousel_column = CarouselColumn(
        thumbnail_image_url=spot["icon"],
        title=spot_name,
        text=spot_address,
        actions=[
            URITemplateAction(
               label="Googleで検索",
               uri=google_search_url
            ),
            URITemplateAction(
               label="ここからのルート",
               uri=google_map_route_url
            )
        ]
    )
    return carousel_column


def lambda_handler(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))

    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(line_event):
        line_bot_api.reply_message(
            line_event.reply_token,
            [
                TextSendMessage(text="カフェを探すね！\n今あなたのいる場所を送ってほしいな！".strip()),
                TextSendMessage(text="line://nv/location")
            ]
        )

    @handler.add(MessageEvent, message=LocationMessage)
    def handle_location_message(line_event):
        lat = line_event.message.latitude
        lng = line_event.message.longitude

        spots = _get_spots(lat, lng)
        view = _carousel_view(spots, lat, lng)

        line_bot_api.reply_message(line_event.reply_token,view)

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json
