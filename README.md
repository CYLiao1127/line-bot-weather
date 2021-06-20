# line-bot-weather

開放平台軟體期末專題-天氣e定通line-bot

可以用於查詢縣市的未來36小時天氣預測與目前的空氣品質狀況。
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
- 照著<a href="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/build_Line-bot.pdf" title="Title">line-bot建立步驟</a> 建立一個line-bot
  
### Installation
- 建立一個虛擬環境:
  ``` python
  conda create --name open-platform python=3.8
  conda activate open-platform
  pip install -r requirements.txt
  ```
  
### Fill in own api
1. Line-bot Channel secret
   - 打開line-bot，在`Bassic setting`裡，找到Channel secret
   <p align="center">
     <img width=800 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/access.png" alt="Channel secret">
   </p>
   
    - 將 `User Channel access token` 改成自己的 `Channel secret`
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L13
    
2. Line-bot Channel secret
   - 打開line-bot，在`Messaging API`裡，找到 `Channel Access Token`
   <p align="center">
     <img width=800 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/secret.png" alt="Channel Access Token">
   </p>
   
    - 將 `User Channel secret` 改成自己的 `Channel Access Token`
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L14
    
3. 氣象局API Key
   - 到<a href="https://opendata.cwb.gov.tw/" title="Title">氣象資料開放平台</a>申請帳號。
   - 取得氣象資料開放平台 `API Key`。
   - 將 `WeatherToken` 改成自己的 `API Key`。
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L36
    
4. 環保署API Key
   - 到<a href="https://data.epa.gov.tw/" title="Title">行政院環保署</a>官網申請帳號。
   - 取得行政院環保署資料開放平台 `API Key`。
   - 將 `QualityToken` 改成自己的 `API Key`。
      - https://github.com/CYLiao1127/line-bot-weather/blob/master/main.py#L49

### Starting line-bot


