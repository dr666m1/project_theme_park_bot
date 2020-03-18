# https://github.com/line/line-bot-sdk-python
try:
  import googleclouddebugger # debugger for google app engine
  googleclouddebugger.enable()
except ImportError:
  pass
from google.cloud import datastore
from flask import Flask, request, abort, redirect
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import config
import random
import numpy as np
import re

app = Flask(__name__)
client = datastore.Client()

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

def reply(event, reply_msg=None):
    if reply_msg is None:
        reply_msg = '何かお困りですか？\n使い方は説明書をご確認ください。\n※環境によってはView all of README.mdを押さないと全文表示されません。\n{}'.format(url_github)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_msg)
    )

def spend(event):
    receive_msg = event.message.text
    user_id = event.source.user_id
    if hasattr(event.source, "group_id"):
        group_id = event.source.group_id
    elif hasattr(event.source, "room_id"):
        group_id = event.source.room_id
    else:
        reply(event)
        return
    price = int(re.search(r"^[y|Y]([-|ー]?[0-9,]+)$", receive_msg).groups()[0].replace(",", ""))
    user_key = client.key("ThemeParkGroup", group_id, "ThemeParkUser", user_id)
    user_entity = client.get(user_key)
    if user_entity is None:
        user_entity = datastore.Entity(key = user_key, exclude_from_indexes=("price",))
    else:
        price += user_entity["price"]
    if price < 0:
        reply(event, "出費が0円を下回ります。\n金額を確認してください。")
        return
    user_entity.update({
        "price": price
    })
    client.put(user_entity)
    reply(event, "{:,d}".format(price))

def split(event):
    receive_msg = event.message.text
    if hasattr(event.source, "group_id"):
        group_id = event.source.group_id
    elif hasattr(event.source, "room_id"):
        group_id = event.source.room_id
    else:
        reply(event)
        return
    group_key = client.key("ThemeParkGroup", group_id)
    query = client.query(kind="ThemeParkUser", ancestor=group_key)
    user_infos = [{
        "name": line_bot_api.get_profile(x.key.name).display_name,
        "price": x["price"],
    } for x in query.fetch()]
    if user_infos == []:
        reply(event, "出費の履歴が見つかりません。")
        return
    reply_msg = []
    # show total
    reply_msg.append("【出費】\n")
    for i in user_infos:
        reply_msg.append("{}: {:,d}\n".format(i["name"], i["price"]))
    # payment
    reply_msg.append("【精算】\n")
    n_member = len(user_infos)
    matrix = np.zeros((n_member, n_member), dtype=np.int64)
    for i, v in enumerate(user_infos):
        matrix[:, i] += v["price"] // n_member
        matrix[i, :] -= v["price"] // n_member
    for i in range(n_member):
        gt0 = False
        personal_msg = ""
        for j in range(n_member):
            if matrix[i, j] > 0:
                gt0 = True
                personal_msg += "  {:,d} -> {}\n".format(matrix[i, j], user_infos[j]["name"])
        if gt0:
            reply_msg.append(user_infos[i]["name"] + "\n")
            reply_msg.append(personal_msg)
    reply(event, "".join(reply_msg))

def combination(event):
    if hasattr(event.source, "group_id"):
        group_id = event.source.group_id
    elif hasattr(event.source, "room_id"):
        group_id = event.source.room_id
    else:
        reply(event)
        return
    group_key = client.key("ThemeParkGroup", group_id)
    try:
        n_rider = int(event.message.text.split("\n")[0][1:])
    except ValueError as e:
        n_rider = 2 # default
    members = [re.sub(r"[ 　]+", " ", m) for m in event.message.text.split("\n") if re.search(r"^[ 　]+$", m) is None][1:]
    if members == []: # fetch cache data
        group_entity = client.get(group_key)
        if group_entity is None:
            reply(event, "メンバーが指定されておらず、履歴も見つかりません。")
            return
        else:
            members = group_entity["members"]
    else: # upsert data
        group_entity = datastore.Entity(group_key, exclude_from_indexes=("members",))
        group_entity.update({
            "members": members,
        })
        client.put(group_entity)
    members_parsed = [m.split(" ") for m in members]
    n_attr = max([len(m) for m in members_parsed]) - 1
    members_completed = [m + ([""] * (n_attr + 1 - len(m))) for m in members_parsed]
    random.shuffle(members_completed)
    for i in range(1, n_attr + 1):
        members_completed.sort(key=lambda x: x[-1 * i])
    n_member = len(members_completed)
    n_pair = -(-n_member // n_rider) # roundup
    i = 0
    pairs = [[""] * n_rider for _ in range(n_pair)]
    for r in range(n_rider):
        for p in range(n_pair):
            try:
                pairs[p][r] = members_completed[i][0]
                i += 1
            except IndexError as e:
                break
    reply_msg = "\n".join([" ".join(["[ {} ]".format(i + 1)] + p) for i, p in enumerate(pairs)])
    reply(event, reply_msg)

def bye(event):
    if hasattr(event.source, "group_id"):
        group_id = event.source.group_id
        line_bot_api.leave_group(group_id)
    elif hasattr(event.source, "room_id"):
        group_id = event.source.room_id
        line_bot_api.leave_room(group_id)
    else:
        reply(event)
        return
    group_key = client.key("ThemeParkGroup", group_id)
    query = client.query(kind="ThemeParkUser", ancestor=group_key)
    res = query.fetch()
    for i in res:
        client.delete(i.key)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    lines = event.message.text.split()
    n_lines = len(lines)
    if (n_lines == 1 and re.search(r"^[y|Y][-|ー]?[0-9,]+$", lines[0]) is not None):
        spend(event)
    elif (n_lines == 1 and re.search(r"^[y|Y]{2}$", lines[0]) is not None):
        split(event)
    elif re.search(r"^[c|C][0-9]*$", lines[0]) is not None:
        combination(event)
    elif (n_lines >= 1 and re.search(r"^[B|b]ye$", lines[0]) is not None):
        bye(event)
    elif (n_lines >= 1 and re.search(r"^[H|h]elp$", lines[0]) is not None):
        reply(event)
    else:
        pass

if __name__ == "__main__":
    app.run()
