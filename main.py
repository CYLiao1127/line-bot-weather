import requests
from flask import Flask, request, abort
import pandas as pd

app = Flask(__name__)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, \
    URIAction, FlexSendMessage
import json

line_bot_api = LineBotApi('User Channel access token')
handler = WebhookHandler('User Channel secret')
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


# 紀錄有哪些城市
cities = ['基隆市', '嘉義市', '臺北市', '嘉義縣', '新北市', '臺南市', '桃園市', '高雄市', '新竹市', '屏東縣', '新竹縣', '臺東縣', '苗栗縣', '花蓮縣', '臺中市',
          '宜蘭縣', '彰化縣', '澎湖縣', '南投縣', '金門縣', '雲林縣', '連江縣']



# 目標：撈取天氣資料，並整理後並回傳
# 透過API KEY到氣象資料開放平台撈取資料
# 撈取下來的是json format
# 撈取的過程中直接透過參數locationName取使用者要的縣市資料
# 針對我們要的36小時天氣資料進行萃取
# 將資料整理完回傳
def get_weather(city):
    weather_token = 'WeatherToken'  # From https://opendata.cwb.gov.tw/
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + weather_token + '&format=JSON&locationName=' + str(
        city)
    weather_data = requests.get(url)
    weather_data = (json.loads(weather_data.text, encoding='utf-8'))['records']['location'][0]['weatherElement']
    res = [[], [], []]  # 抓下來的資料為每2個小時一個單位，共36小時，所以創3個位置來存
    for j in range(3):
        for weather in weather_data:
            res[j].append(weather['time'][j])
    return res


# 目標：撈取空氣品質資料，並將資訊整理到輸出格式部分(bubble.json)方便後續回傳給使用者
# 透過API KEY到環保署資料開放平台撈取資料
# 撈取下來的是csv format
# 針對我們要的 AQI, PM2.5, PM10, O3, O3_8hr進行萃取
# 由於我們撈取的資料並非縣市，而是各個測站，因此將資料根據使用者選取的縣市取平均
# 將資料統整到bubble.json裡面，方便後續透過格式FlexSendMessage回傳資料到line-bot上
# 將資料回傳到給使用者
def get_air_quality(city):
    quality_token = 'QualityToken'  # From https://data.epa.gov.tw/
    url = "https://data.epa.gov.tw/api/v1/aqx_p_432?api_key=" + token + "&format=csv"

    df = pd.read_csv(url, encoding="utf-8")
    
    public_time = df["PublishTime"][1]  # 資料時間
    df = pd.DataFrame(data=df, columns=["County", "AQI", "PM2.5", "PM10", "O3", "O3_8hr"])  # 選取我們要的資料
    df = df[df["County"] == city]  # 選取城市
    df[["AQI", "PM2.5", "PM10", "O3", "O3_8hr"]] = df[["AQI", "PM2.5", "PM10", "O3", "O3_8hr"]].apply(pd.to_numeric, errors='coerce')  # 將資料轉成numeric
    df = df.mean()  # 計算平均值
    
    # 空氣品質輸出格式
    res = json.load(open('./temmplate/card.json', 'r', encoding='utf-8'))
    bubble = json.load(open('./temmplate/bubble.json', 'r', encoding='utf-8'))
   
    aqi = round(df["AQI"], 2)

    bubble['body']['contents'][0]['text'] = city + '空氣品質'
    bubble['body']['contents'][1]['text'] = "資料時間: " + public_time
    bubble['body']['contents'][2]['contents'][0]['contents'][1]['text'] = str(round(df["AQI"], 2))
    bubble['body']['contents'][2]['contents'][1]['contents'][1]['text'] = str(round(df["PM2.5"], 2))
    bubble['body']['contents'][2]['contents'][2]['contents'][1]['text'] = str(round(df["PM10"], 2))
    bubble['body']['contents'][2]['contents'][3]['contents'][1]['text'] = str(round(df["O3"], 2))
    bubble['body']['contents'][2]['contents'][4]['contents'][1]['text'] = str(round(df["O3_8hr"], 2))
 
    #  判斷空氣品質狀況，根據不同狀況，給不同的圖片
    if aqi <= 50:
        bubble['body']['contents'][3]['text'] = '空氣品質良好'
        bubble['hero']['url'] = "https://i.imgur.com/WflHpXo.png"
    elif aqi <= 100:
        bubble['body']['contents'][3]['text'] = '空氣品質正常'
        bubble['hero']['url'] = "https://i.imgur.com/WflHpXo.png"
    elif aqi <= 150:
        bubble['body']['contents'][3]['text'] = '敏感族群注意'
        bubble['hero']['url'] = "https://i.imgur.com/Hel2tvh.png"
    elif aqi <= 200:
        bubble['body']['contents'][3]['text'] = '所有人員注意'
        bubble['hero']['url'] = "https://i.imgur.com/Hel2tvh.png"
    elif aqi <= 300:
        bubble['body']['contents'][3]['text'] = '非常不健康'
        bubble['hero']['url'] = "https://i.imgur.com/QecWI3e.png"
    else:
        bubble['body']['contents'][3]['text'] = '千千萬萬不要出門'
        bubble['hero']['url'] = "https://i.imgur.com/QecWI3e.png"


    res['contents'].append(bubble)

    return res

# Message event
# 再輸出天氣狀況跟空氣品質的部分，這邊嘗試兩種不同的格式來做輸出
# 1. 天氣狀況的部分是使用定義好的格式：TemplateSendMessage
# 2. 而空氣品質的部分則是使用我們自訂億的格式：FlexSendMessage
@handler.add(MessageEvent)
def handle_message(event):
    global last_message  # 記錄使用者準備查詢的是天氣狀況還是空氣品質
    mtext = event.message.text
    if mtext == '@查詢天氣':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入欲查詢縣市！'))
        last_message = "weather"
    elif mtext == '@查詢空氣品質':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入欲查詢縣市！'))
        last_message = "quality"
    elif last_message == "weather":  
        if not (mtext.replace('台', '臺') in cities):  # 判斷輸入的是否為存在的縣市名稱
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入縣市！'))
        else:
            city = mtext
            city = city.replace('台', '臺')  # 避免使用者輸入小寫「台」，若使用者輸入「台」，則改成「臺」
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

# 將資料填入天氣預報輸出格式中
def weather_reply(city, res):
    
    # 根據降雨機率高或低，給不同的圖片
    for i in range(len(res)):
        rainy_rate = int(res[i][1]['parameter']['parameterName'])
        if rainy_rate <= 30:
            res[i].append("https://i.imgur.com/b6aTCiw.png")
        elif rainy_rate <= 70:
            res[i].append("https://i.imgur.com/Zsr9ec6.png")
        else:
            res[i].append("https://i.imgur.com/PO9TUMX.png")

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
