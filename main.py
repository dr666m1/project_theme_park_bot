# from https://github.com/line/line-bot-sdk-python
try:
  import googleclouddebugger # debugger for google app engine
  googleclouddebugger.enable()
except ImportError:
  pass
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import config

app = Flask(__name__)

line_bot_api = LineBotApi(config.token)
handler = WebhookHandler(config.secret)
url_github = "https://github.com/dr666m1/project_theme_park_bot"

@app.route("/")
def github():
    return redirect(url_github)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body) # output log to stdout
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

def error(event):
    msg = 'sorry, something went wrong. if you need help, type ":help" and check the usage.'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg)
    )

def help(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=url_github)
    )

def bye(event):
    try:
        line_bot_api.leave_group(event.source.group_id)
    except AttributeError as e:
        pass
    try:
        line_bot_api.leave_room(event.source.source_id)
    except AttributeError as e:
        pass

def birthday(event):
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="なんと..."),
            TextSendMessage(text="今日はゆっこちゃんに..."),
            TextSendMessage(text="誕生日プレゼントがあります！！"),
            #ImageSendMessage(
            #    original_content_url="",
            #    preview_image_url="",
            #),
        ]
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    cmd = event.message.text.split()
    if cmd[0] == ":help":
        help(event)
    elif cmd[0] == ":bye":
        bye(event)
    elif cmd[0] == ":birthday":
        birthday(event)
    elif cmd[0][0] == ":":
        error(event)

if __name__ == "__main__":
    app.run()

