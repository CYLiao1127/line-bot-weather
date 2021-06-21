# line-bot-weather
天氣跟空氣品質對於我們日常生活的重要秀無庸置疑，我們總是會想知道天氣狀況來決定出門是否需要帶傘，需不需要多帶件外套，或是需不需要擦防曬油、戴一副墨鏡出門等等，不僅如此，近年來由於空氣汙染嚴重，越來越多人會有過敏的情況發生，若是長期待在空氣不好的戶外空間，對身體更是一大傷害。

在現今說到要查看天氣狀況與空氣品質，我們總是會想到鎖定某個時段的新聞天氣預報、或是google查詢天氣、與空氣狀況，不過，這些效果都不是太好...

因此，我決定開發這個line-bot - 天氣e定通，方便使用者查詢天氣狀況與空氣品質。

## Introduction
天氣e定通line-bot 功能有三，
1. 一個簡單查詢的line聊天機器人。
2. 透過串接氣象資料開放平台API，查詢縣市的未來36小時天氣預測。
2. 透過串接環保署資料開放平台API，查詢縣市的目前的空氣品質狀況。
<p align="center">
    <img width=250 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/all.gif" alt="demo gif">
</p>

## Prerequisites
- python 3.8.10
- Flask 2.0.1
- gunicorn 20.1.0
- line-bot-sdk 1.8.0
- numpy 1.20.3
- pandas 1.2.4
- requests 2.25.1


## Getting Started

### Bulid line-bot
- 照著<a href="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/build_Line-bot.pdf" title="Title">line-bot建立步驟</a> 建立一個line-bot。
  
### Installation
- 建立一個虛擬環境:
  ``` bash
  $ conda create --name open-platform python=3.8
  $ conda activate open-platform
  $ pip install -r requirements.txt
  ```
  
### Fill in own API
1. Line-bot Channel secret
   - 打開line-bot，在`Bassic setting`裡，找到 `Channel secret`。
   <p align="center">
     <img width=900 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/Channel_access.png" alt="Channel secret">
   </p>
   
    - 將 `main.py` 中第13行的 `User Channel access token` 改成自己的 `Channel secret`。
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L13
    
2. Line-bot Channel secret
   - 打開line-bot，在`Messaging API`裡，找到 `Channel Access Token`
   <p align="center">
     <img width=900 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/Channel_secret.png" alt="Channel Access Token">
   </p>
   
    - 將 `main.py` 中第14行的 `User Channel secret` 改成自己的 `Channel Access Token`
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L14
    
3. 氣象局API Key
   - 到<a href="https://opendata.cwb.gov.tw/" title="Title">氣象資料開放平台</a>申請帳號。
   - 取得氣象資料開放平台 `API Key`。
   - 將 `main.py` 中第36行的 `WeatherToken` 改成自己的 `API Key`。
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L36
    
4. 環保署API Key
   - 到<a href="https://data.epa.gov.tw/" title="Title">行政院環保署</a>官網申請帳號。
   - 取得行政院環保署資料開放平台 `API Key`。
   - 將 `main.py` 中第49行的 `QualityToken` 改成自己的 `API Key`。
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L49

### Starting line-bot
1. 取得Webhook URL
   這邊有兩種方式，兩種可以二選一，分別是透過ngrok與透過Heroku：
   1. ngrok
      1. 下載<a href="https://ngrok.com/download" title="Title">ngrok</a>。
      2. 解壓縮檔案後將 `ngrok.exe` 放到與 `main.py` 同一資料夾。
      3. 進入虛擬環境 `conda activate open-platform`。
      4. 執行程式 `python main.py`。
      5. 另外開一個命令提示字元，輸入 `ngrok http 5000`，取得Webhook URL。
      <p align="center">
         <img src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/ngrok.png" alt="ngrok">
      </p>
   2. Heroku
      1. 到<a href="https://devcenter.heroku.com/" title="Title">Heroku Dev Center</a>註冊帳號。
      2. 安裝<a href="https://git-scm.com/downloads" title="Title">git</a>。
      3. 安裝<a href="https://devcenter.heroku.com/articles/heroku-cli#download-and-install" title="Title">Heroku CLI</a>。
      3. 進入虛擬環境 `conda activate open-platform`。
      4. 輸入 `heroku login` ，登入Heroku。
      5. 輸入 `heroku create open-platform`，建立一個叫做`open-platform`的應用程式。
      6. 將cmd路徑切換到專案資料夾下。
      7. 輸入以下指令：
         ``` bash
         $ git init
         $ heroku git:remote -a open-platform
         $ git add .
         $ git commit -am "make it better"
         $ git push heroku master
         ```
      8. 取得Webhook URL。
      <p align="center">
         <img src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/heroku.png" alt="Heroku">
      </p>
   
2. 設定Webhook URL
   1. 打開line-bot，在`Messaging API`裡，找到 `Webhook setting`，點擊`Edit`鈕更改值。
   2. 將取得的 `Webhook URL` 貼到 `Webhook URL`欄位中，並在後面將上 `/callback` ，例如：
      `https://open-platform.herokuapp.com/callback`
   4. 點擊`update`鈕。
   5. 點擊`Verify`鈕。
   6. 將 `Use webhook` 更改為「啟用」。
   <p align="center">
      <img src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/verify.png" alt="verify">
   </p>

## Result&Demo
- 未來36小時天氣預報：點選圖文選單中，天氣的部分，並輸入縣市。
<p align="center">
   <img src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/weather_v2.gif" alt="weather">
</p>
- 即時空氣品質資訊：點選圖文選單中，空氣的部分，並輸入縣市。
<p align="center">
   <img src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/quality_v2.gif" alt="weather">
</p>

## Reference
[Day12 LINE BOT & 天氣預報 - 2](https://ithelp.ithome.com.tw/articles/10245154)

[LINE Messaging API SDK for Python](https://github.com/line/line-bot-sdk-python)

[Line Bot 教學](https://github.com/yaoandy107/line-bot-tutorial)
