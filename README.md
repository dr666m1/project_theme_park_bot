# テーマパークbot
<img src="https://user-images.githubusercontent.com/26474260/78467641-a010e080-7749-11ea-9bda-d87bf7bf6935.png" width="500px">

## コンセプト
友人と遊園地で遊ぶときに便利なLINEbotです。

割り勘やアトラクションのペア分けが、LINEグループやトークルーム内で完結します。

## 準備
上のQRコードやID（`@541rhynx`）からbotをグループやトークルームに招待するだけです。

## 割り勘
<img src="https://user-images.githubusercontent.com/26474260/78037475-93396900-73a6-11ea-8d23-c19a1988614b.png" width="250px">

### 出費の記録
`Y`に続けて半角数字を入力すると自分の出費を記録できます（`Y`はYenの頭文字）。

完了すると、現在のあなたの合計出費額が表示されます。

### 出費の確認
`YY`と入力すると全員の出費額と、誰が誰にいくら払うべきか表示されます。

出費を一切記録していない人は割り勘に含まれません（含みたい場合は`Y0`で0円の出費を記録してください）。

### 出費の初期化
`bye`と入力すると、出費の記録を削除してbotが退出します。

## ペア分け
<img src="https://user-images.githubusercontent.com/26474260/76966746-c6710680-6969-11ea-9eef-97345d50239e.jpg" width="250px">

一行目に`C`、二行目以降にメンバーを入力するとランダムにペア分けされます（`C`はCombinationの頭文字）。

メンバーを省略し`C`だけ送信すると、直前と同じメンバーが指定されたことになります。

スペース区切りで属性（性別など）を入力すると、なるべく別の属性同士でペア分けします。

## Q and A
### 自分の出費額を間違えたので取り消したい
`Y-1000`のように入力すると減額できます。

### botを退会させたのに出費が初期化されない
LINEのメニューから退会させても出費は初期化されないので、
botがグループやトークルームにいる状態で`bye`と入力してください。

### 3人乗り以上のアトラクションのグループ分けはできる？
`C3`のように、Cの後に何人乗りか数字で指定してください。

### ペア分けの属性は性別以外でもいいの？
性別だけでなく、単順に`A` `B` `C`など何を指定しても大丈夫です。

### botが応答しない！
数字や`Y` `C`といったキーワードが半角になっているか、
余計なスペースや空行が含まれていないかをご確認ください。

### 使い方を覚えきれない！
`help`と入力すると説明書が確認できるので、それだけ覚えると便利です。
