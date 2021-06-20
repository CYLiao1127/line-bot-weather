# line-bot-weather

開放平台軟體期末專題-天氣e定通line-bot

可以用於查詢縣市的未來36小時天氣預測與目前的空氣品質狀況。
<p align="center">
  <img width=250 src="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/all.gif" alt="Air Quality">
</p>

## Prerequisites
  * python 3.8.10
  * Flask 2.0.1
  * gunicorn 20.1.0
  * line-bot-sdk 1.8.0
  * numpy 1.20.3
  * pandas 1.2.4
  * requests 2.25.1


## Getting Started

  ### bulid line-bot
  * 照著<a href="https://github.com/CYLiao1127/line-bot-weather/blob/master/ref/build_Line-bot.pdf" title="Title">line-bot建立步驟</a> 建立一個line-bot
  
  ### Installation
   * 建立一個虛擬環境:
        ``` python
        conda create --name open-platform python=3.8
        conda activate open-platform
        conda install -r requirements.txt
        ```
  
  ### Starting line-bot
  
  
