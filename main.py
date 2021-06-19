import requests
from flask import Flask, request, abort
import pandas as pd

app = Flask(__name__)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    URIAction, FlexSendMessage
import json

line_bot_api = LineBotApi(
    '0zmy7gyoHsmGkRWXJSVWvyPDeKaqxjcPvxvLXCyp/xo'
    '/wG77bSEQxAEuND6tBFuFVHBOgnXjSv4nh2t2bTbbGlJWTeXVRYbneZZcd067IXCUzNRmKkbbHg'
    '+IautAtJlxnXJPDOML2vUXuLQIg4NzEAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fa6e04cd13ab3cdf5c74687c13cae05e')
last_message = ' '


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


cities = ['基隆市', '嘉義市', '臺北市', '嘉義縣', '新北市', '臺南市', '桃園市', '高雄市', '新竹市', '屏東縣', '新竹縣', '臺東縣', '苗栗縣', '花蓮縣', '臺中市',
          '宜蘭縣', '彰化縣', '澎湖縣', '南投縣', '金門縣', '雲林縣', '連江縣']


def get_weather(city):
    token = 'CWB-39044516-A34A-4EFC-B8D6-28132599C10B'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(
        city)
    weather_data = requests.get(url)
    weather_data = (json.loads(weather_data.text, encoding='utf-8'))['records']['location'][0]['weatherElement']
    res = [[], [], []]  # 12個小時為單位
    for j in range(3):
        for weather in weather_data:
            res[j].append(weather['time'][j])
    return res


def get_air_quality(city):
    token = '9be7b239-557b-4c10-9775-78cadfc555e9'
    url = "https://data.epa.gov.tw/api/v1/aqx_p_432?api_key=" + token + "&format=csv"

    df = pd.read_csv(url, encoding="utf-8")
    # df = pd.read_csv("aqx_p_432_20210619133036.csv", encoding="utf-8")
    # df = pd.read_csv("test.csv", encoding="utf-8")
    public_time = df["PublishTime"][1]
    df = pd.DataFrame(data=df, columns=["County", "AQI", "PM2.5", "PM10", "O3", "O3_8hr"])
    df = df[df["County"] == city]
    df[["AQI", "PM2.5", "PM10", "O3", "O3_8hr"]] = df[["AQI", "PM2.5", "PM10", "O3", "O3_8hr"]].apply(pd.to_numeric,
                                                                                                      errors='coerce')
    df = df.mean()

    res = json.load(open('card.json', 'r', encoding='utf-8'))
    bubble = json.load(open('bubble.json', 'r', encoding='utf-8'))
    aqi = round(df["AQI"], 2)

    bubble['body']['contents'][0]['text'] = city + '空氣品質'

    bubble['body']['contents'][1]['text'] = "資料時間: " + public_time

    bubble['body']['contents'][2]['contents'][0]['contents'][1]['text'] = str(round(df["AQI"], 2))

    bubble['body']['contents'][2]['contents'][1]['contents'][1]['text'] = str(round(df["PM2.5"], 2))

    bubble['body']['contents'][2]['contents'][2]['contents'][1]['text'] = str(round(df["PM10"], 2))

    bubble['body']['contents'][2]['contents'][3]['contents'][1]['text'] = str(round(df["O3"], 2))

    bubble['body']['contents'][2]['contents'][4]['contents'][1]['text'] = str(round(df["O3_8hr"], 2))

    if aqi <= 50:
        bubble['body']['contents'][3]['text'] = '空氣品質良好'
        bubble['hero']['url'] = "https://i.imgur.com/owQIOfI.png"
    elif aqi <= 100:
        bubble['body']['contents'][3]['text'] = '空氣品質正常'
        bubble['hero']['url'] = "https://i.imgur.com/owQIOfI.png"
    elif aqi <= 150:
        bubble['body']['contents'][3]['text'] = '敏感族群注意'
        bubble['hero']['url'] = "https://i.imgur.com/IJxyMd3.png"
    elif aqi <= 200:
        bubble['body']['contents'][3]['text'] = '所有人員注意'
        bubble['hero']['url'] = "https://i.imgur.com/IJxyMd3.png"
    elif aqi <= 300:
        bubble['body']['contents'][3]['text'] = '非常不健康'
        bubble['hero']['url'] = "https://i.imgur.com/9CXBRiD.png"
    else:
        bubble['body']['contents'][3]['text'] = '千千萬萬不要出門'
        bubble['hero']['url'] = "https://i.imgur.com/9CXBRiD.png"

    res['contents'].append(bubble)

    return res


# Message event
@handler.add(MessageEvent)
def handle_message(event):
    global last_message
    mtext = event.message.text
    if mtext == '@查詢天氣':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入欲查詢縣市！'))
        last_message = "weather"
    elif mtext == '@查詢空氣品質':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入欲查詢縣市！'))
        last_message = "quality"
    elif last_message == "weather":
        if not (mtext.replace('台', '臺') in cities):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入縣市！'))
        else:
            city = mtext
            city = city.replace('台', '臺')  # 若使用者輸入「台」，則改成「臺」
            res = get_weather(city)
            return_message = weather_reply(city, res)
            line_bot_api.reply_message(event.reply_token, return_message)
            last_message = " "
    elif last_message == "quality":
        if not (mtext.replace('台', '臺') in cities):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入縣市！'))
        else:
            city = mtext
            city = city.replace('台', '臺')  # 若使用者輸入「台」，則改成「臺」
            res = get_air_quality(city)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(city + '空氣品質', res))
            last_message = " "
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先選擇欲查詢項目！"))


def weather_reply(city, res):
    for i in range(len(res)):
        rainy_rate = int(res[i][1]['parameter']['parameterName'])
        if rainy_rate <= 30:
            res[i].append("https://i.imgur.com/oDxY4Jz.png")
        elif rainy_rate <= 70:
            res[i].append("https://i.imgur.com/7AqxoKN.png")
        else:
            res[i].append("https://i.imgur.com/WxZ5sMi.jpg")

    return TemplateSendMessage(
        alt_text=city + '未來 36 小時天氣預測',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url=data[5],
                    title='{} ~ {}'.format(res[0][0]['startTime'][5:-3], res[0][0]['endTime'][5:-3]),
                    text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],
                                                                  data[2]['parameter']['parameterName'],
                                                                  data[4]['parameter']['parameterName'],
                                                                  data[1]['parameter']['parameterName']),
                    actions=[
                        URIAction(
                            label='詳細內容',
                            uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                        )
                    ]
                ) for data in res
            ]
        )
    )


if __name__ == "__main__":
    app.run()
