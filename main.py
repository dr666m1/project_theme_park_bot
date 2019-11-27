# https://github.com/line/line-bot-sdk-python
try:
  import googleclouddebugger # debugger for google app engine
  googleclouddebugger.enable()
except ImportError:
  pass
from google.cloud import datastore
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import config
import json
import math
import random
import numpy as np

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

def error(event, msg=None):
    if msg is None:
        msg = 'sorry, something went wrong. if you need help, type ":help" and check the usage.'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg)
    )

def combination(event, n_rider=2):
    client = datastore.Client()
    try:
        id = event.source.group_id
        table ="CombinationGroup" 
    except AttributeError as e:
        try:
            id = event.source.room_id
            table = "CombinationTalkRoom"
        except AttributeError as e:
            error(event)
            return
    key = client.key(table, id)
    persons = [m.split() for m in event.message.text.split("\n") if m != ""][1:]
    if persons == []: # fetch cache data
        entity = client.get(key)
        if entity is None:
            error(event)
            return
        persons = json.loads(entity["msg"])
    else: # upsert data
        entity = datastore.Entity(key, exclude_from_indexes=("msg",))
        entity.update({
            "msg": json.dumps(persons),
        })
        client.put(entity)
    n_attr = max([len(p) for p in persons]) - 1
    persons_completed = [p + ([""] * (n_attr + 1 - len(p))) for p in persons]
    random.shuffle(persons_completed)
    for i in range(1, n_attr + 1):
        persons_completed.sort(key=lambda x:x[-1 * i])
    n_person = len(persons_completed)
    n_group = -(-n_person // n_rider) # roundup
    i = 0
    groups = [[""] * n_rider for _ in range(n_group)]
    for r in range(n_rider):
        for g in range(n_group):
            try:
                groups[g][r] = persons_completed[i][0]
                i += 1
            except IndexError as e:
                break
    reply = "\n".join([" ".join(["[ " + str(i) + " ]"] + g) for i, g in enumerate(groups, 1)])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
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
        try:
            line_bot_api.leave_room(event.source.room_id)
        except AttributeError as e:
            error(event)

def spend(event):
    msg = event.message.text
    client = datastore.Client()
    user = event.source.user_id # old version of line app may cause problem
    try:
        id = event.source.group_id
        table = "SpendGroup" 
    except AttributeError as e:
        try:
            id = event.source.room_id
            table = "SpendTalkRoom"
        except AttributeError as e:
            error(event)
            return
    try:
        price = int(msg.split()[1])
    except (ValueError, IndexError) as e:
        error(event)
        return
    key = client.key(table, id)
    entity = client.get(key)
    if entity is None:
        data = {}
    else:
        data = json.loads(entity["data"])
    try:
        data[user] += price
    except KeyError as e:
        data[user] = price
    entity = datastore.Entity(key, exclude_from_indexes=("data",))
    entity.update({
        "data": json.dumps(data),
    })
    client.put(entity)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(data[user]))
    )

def clear(event):
    client = datastore.Client()
    try:
        id = event.source.group_id
        table = "SpendGroup" 
    except AttributeError as e:
        try:
            id = event.source.room_id
            table = "SpendTalkRoom"
        except AttributeError as e:
            error(event)
            return
    key = client.key(table, id)
    client.delete(key)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="done!")
    )

def split(event):
    msg = event.message.text
    client = datastore.Client()
    try:
        id = event.source.group_id
        table = "SpendGroup" 
    except AttributeError as e:
        try:
            id = event.source.room_id
            table = "SpendTalkRoom"
        except AttributeError as e:
            error(event)
            return
    key = client.key(table, id)
    entity = client.get(key)
    if entity is None:
        error(event)
        return
    data = json.loads(entity["data"])
    replys = []
    # show total
    replys.append("# total price")
    names = []
    for k, v in data.items():
        try:
            names.append(line_bot_api.get_profile(k).display_name)
        except LineBotApiError as e:
            names.append(k)
        replys.append(names[-1] + " : " + "{:>9,d}".format(v))
        # lower than 9,999,999 is expected
    # payment
    replys.append("# payment")
    try:
        n_person = int(msg.split()[1])
    except IndexError as e:
        n_person = len(data)
    except ValueError as e:
        error(event)
        return
    matrix = np.zeros((n_person, n_person), dtype=np.int64)
    for i, v in enumerate(data.values()):
        matrix[:, i] += v // n_person
        matrix[i, :] -= v // n_person
    for i in range(n_person):
        flg = False
        try:
            replys_personal = [names[i]]
        except IndexError as e:
            replys_personal = ["unknown"]
        for j in range(n_person):
            if matrix[i, j] > 0:
                flg = True
                replys_personal.append("  " + "{:>9,d}".format(matrix[i, j]) + " -> " + names[j])
                # lower than 9,999,999 is expected
        if flg:
            replys += replys_personal
    reply = "\n".join(replys)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

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
    elif cmd[0] in [":comb", ":combination"]:
        combination(event)
    elif cmd[0] == ":split":
        split(event)
    elif cmd[0] == ":clear":
        clear(event)
    elif cmd[0] == ":spend":
        spend(event)
    elif cmd[0][0] == ":":
        error(event)

if __name__ == "__main__":
    app.run()

