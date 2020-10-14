import requests
from flask import Flask, request, abort
app = Flask(__name__)

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

line_bot_api = LineBotApi('hqEl585SGIBhx6uT76NDejSR9raDAisjEd0gRw8M2WTWWtpKVrHVfDIeOrlYLS2IWnoGqPOLPTRv9dbpfkc0RZolRtqYVyRCVvMHW5bG/oKLnpqp+KkxK6PiflqzF/cUofwFYm1+uTIFiZ4QRe3l8wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('04edcbc7ae06600d0c12e2b7800fdf2e')


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    if mtext == '@輸入發票最後三碼':
        try:
            message = TextSendMessage(
                text='請輸入發票最後三碼進行對獎！'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif mtext == '@前期中獎號碼':
        try:
            message = TextSendMessage(
                text=monoNum(1)
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif mtext == '@本期中獎號碼':
        try:
            message = TextSendMessage(
                text=monoNum(0)
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif len(mtext) == 3 and mtext.isdigit():
        try:
            message = TextSendMessage(
                text=checkincvoicce(mtext)
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='讀取發票發生錯誤！'))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發跳最後三碼進行對獎！'))


def checkincvoicce(n):
    content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)
    items = list(tree.iter(tag='item'))
    ptext = items[0][2].text
    ptext = ptext.replace('<p>', '').replace('</p>', '\n')
    temlist = ptext.spilt(':')
    prizelist = []
    prizelist.append(temlist[1][5:8])
    prizelist.append(temlist[5][5:8])
    for i in range(3):
        prizelist.append(temlist[3][9*i+5 : 9*i+8])
    sixlist = temlist[4].split('`')
    for i in range(len(sixlist)):
        prizelist.append(sixlist[i])
    if n in prizelist:
        message = '符合某獎項後三碼，請自行核對發票前五碼！\n\n'
        message += monoNum(0)
    else:
        message = '很可惜，未中獎。請輸入下一張發票最後三碼。'
    return message

def monoNum(n):
    content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)
    items = list(tree.iter(tag='item'))
    title = items[n][0].text
    ptext = items[n][2].text
    ptext = ptext.replace('<p>', '').replace('</p>', '\n')
    print(title + '月\n' + ptext[:-1])
    return title + '月\n' + ptext[:-1]

if __name__ == "__main__":
    app.run()
