# ****************************************************************************************
# Draw an Analog Clock using a little Rectangular to Polar Coordinate Fun. Uses RTC Clock
# to keep time. 
# ****************************************************************************************
import time
from datetime import datetime
from modules import myfeedparser
from modules.analog_clock import AnalogClock
from modules.open_weather_wrap import CurrentWeather, getCurrentWeatherData
from guizero import App, Drawing, Box, TextBox


def formatNewsItems(feedItems: dict, max_items: int):
    cur_item: int = 0
    ret: str = 'LATEST NEWS:\n----------------------------'

    for item in feedItems:
        cur_item += 1

        print(item)

        if cur_item <= max_items:
            ret += "\n" + item.title + ': ' + item.title_detail.value

    return ret

def app_resize():
    global canvas, clock, weatherCanvas, newsTextBox
    # Resize main canvas objects who also have resize handlers
    canvas.resize(app.width / 2, app.height)
    clock.handle_resize()
    weatherCanvas.resize(app.height / 2, app.width / 2)
    newsTextBox.resize(app.width / 2, app.height / 2)

def weatherResize():
    global weatherCanvas, app
    pass


bgApp: str = '#0000FF'
bgWeather: str = '#FFFFFF'
bgNews: str = '#FFFFFF'

# Create App
app: App = App('Savina\'s Clocl', width=800, height=600, layout="grid", bg=bgApp)

# Create AnalogClock
canvas: Drawing = Drawing(app, app.width / 2, app.width / 2, grid=[0, 0])
clock: AnalogClock = AnalogClock(app, canvas)

# Create CurrentWeather
weatherCanvas: Box = Box(app, grid=[1, 0], width=int(app.width / 2), height=int(app.height / 2),
                         layout="grid")
weatherCanvas.when_resized = weatherResize
weatherCanvas.bg = bgWeather

# Now add areas to display weather
todayWeatherInfo: CurrentWeather = getCurrentWeatherData()

# iconWeatherCanvas: Drawing = Drawing(weatherCanvas, width=int(weatherCanvas.width / 4),
#                                     height=int(weatherCanvas.height / 4), grid=[0, 0])
curTempBox: TextBox = TextBox(weatherCanvas, text=str(todayWeatherInfo.temp) + 'F',
                              width=int(0.75 * weatherCanvas.width),
                              height=int(weatherCanvas.height / 4), grid=[0, 0])

humidityTextBox: TextBox = TextBox(weatherCanvas, text=str(todayWeatherInfo.humidity) + '%',
                                   width=weatherCanvas.width, height=int(weatherCanvas.height / 4),
                                   grid=[0, 1])

WindTextBox: TextBox = TextBox(weatherCanvas, text=str(todayWeatherInfo.wind) + ' mph',
                               width=weatherCanvas.width,
                               height=int(weatherCanvas.height / 4), grid=[0, 2])

descTextBox: TextBox = TextBox(weatherCanvas, text=todayWeatherInfo.description, width=weatherCanvas.width,
                               height=int(weatherCanvas.height / 4), grid=[0, 3])

newsFeed: myfeedparser.MyFeedParser = myfeedparser.MyFeedParser()
newItems = newsFeed.getLatestFeedItems()

newsTextBox = TextBox(app, text=formatNewsItems(newItems, 5), grid=[1, 1],
                      width=int(app.width / 2), height=int(app.height / 2),
                      multiline=True)

newsTextBox.bg = bgNews

app.when_resized = app_resize
app.full_screen = True
app.display()
