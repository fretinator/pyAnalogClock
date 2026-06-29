# ****************************************************************************************
# Draw an Analog Clock using a little Rectangular to Polar Coordinate Fun. Uses RTC Clock
# to keep time. 
# ****************************************************************************************
import time
from datetime import datetime
from modules import myfeedparser
from modules.analog_clock import AnalogClock
from guizero import App, Drawing, TitleBox, TextBox
import webbrowser

newsTextBoxes: list[TextBox] = []
feedItems = []

MAX_NEWS_ITEMS = 10

def getLastUpdated():
    now = datetime.now()
    return str(now)

def formatNewsItems():
    global feedItems, newsTitleBox, newsTextBoxes
    
    cur_item: int = 0
    newsTitleBox.text = "LATEST NEWS: Updated at " + getLastUpdated() 

    for item in feedItems:
        txt: str = str(cur_item + 1) + ": " + item.title_detail.value
        newsTextBoxes[cur_item].value = txt
        cur_item += 1

def app_resize():
    global canvas, clock, newsTitleBox, newsTextBoxes
    # Resize main canvas objects who also have resize handlers
    canvas.resize(int(app.width / 2), app.height)
    clock.handle_resize()
    newsTitleBox.resize(int(app.width / 2), app.height)

    #for t in newsTextBoxes:
    #   t.resize(int(app.width / 2), int(app.height/(MAX_NEWS_ITEMS + 1)))

def load_news():
    global feedItems
    
    print("Updating news feed...")
    feedItems = newsFeed.getLatestFeedItems()
    formatNewsItems()
    
def newsItemH():
    return 2

def getTextBoxNumber(textbox: TextBox):
    global newsTextBoxes
    
    cur_item = 0
    
    for txtBox in newsTextBoxes:
        if newsTextBoxes[cur_item] == textbox:
            return cur_item
        
        cur_item += 1
        
    return -1

def showSummary(which_item):
    global newsTextBoxes, feedItems, app
    
    if which_item < len(feedItems):
        webbrowser.open(feedItems[which_item].link)
        

def handleClick(eventData):
    which_widget = eventData.widget
    
    item_number = getTextBoxNumber(which_widget)
    
    if item_number>= 0:
        showSummary(item_number)

bgApp: str = '#0000FF'
bgNews: str = '#FFFFFF'

# Create App
app: App = App('Savina\'s Clocl', width=800, height=600, layout="grid", bg=bgApp)

# Create AnalogClock
canvas: Drawing = Drawing(app, app.width / 2, app.width / 2, grid=[0, 0])
clock: AnalogClock = AnalogClock(app, canvas)


newsFeed: myfeedparser.MyFeedParser = myfeedparser.MyFeedParser()


newsTitleBox = TitleBox(app, grid=[1,0], width=int(app.width / 2), height=app.height,
                      layout="grid", text="News")

newsTitleBox.bg = bgNews

cur_box: int = 0
for i in range(MAX_NEWS_ITEMS):
    newsTextBox = TextBox(newsTitleBox, text=str(cur_box) + "...",
                      width=55, height=3,
                      multiline=True, grid=[0,cur_box])
    newsTextBox.bg = bgNews
    newsTextBox.text_size = 20
    newsTextBox.wrap = True
    newsTextBox.when_clicked = handleClick
    newsTextBoxes.append(newsTextBox)
    cur_box += 1

load_news()

newsTitleBox.repeat(1800000, load_news) # Every 30 minutes

app.when_resized = app_resize
app.full_screen = True
app.display()
