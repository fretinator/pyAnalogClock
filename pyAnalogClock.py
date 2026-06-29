#****************************************************************************************
# Draw an Analog Clock using a little Rectangular to Polar Coordinate Fun. Uses RTC Clock
# to keep time. 
#****************************************************************************************
from guizero import App, Drawing
from dataclasses import dataclass
import numpy as np
from typing import List

# define some colour values
BLACK =       0x0000
BLUE =        0x001F
RED =         0xF800
GREEN =       0x07E0
CYAN =        0x07FF
MAGENTA =     0xF81F
YELLOW =      0xFFE0
WHITE =       0xFFFF
LIGHT_GRAY =  0xA514
DARK_GRAY =   0x2124

SCREEN_BACK_COLOR = BLUE
CLOCK_HASH_COLOR = BLACK
CLOCK_FACE_COLOR = WHITE
HOUR_HAND_COLOR = BLACK
MINUTE_HAND_COLOR = DARK_GRAY
INNER_CIRCLE_COLOR = GREEN
BTN_BACK_COLOR = GREEN
BTN_TEXT_COLOR = RED


curMillis = 0
lastMillis = 0
UPDATE_MILLIS = 5000; # Every second
firstRun = True
prevDayOfMonth = -1
CLOCK_PADDING = 10
HASH_LINE_SIZE = 16
HASH_RECT_HEIGHT = 16
HASH_RECT_WIDTH = 8
INNER_CIRCLE_RADIUS = 8 
HOUR_HAND_BASE = 16
HOUR_HAND_LENGTH = 60
MINUTE_HAND_BASE = 8
MINUTE_HAND_LENGTH = 100
CIRCLE_RADS = 2 * np.pi
APPROXIMATION_VALUE = 0.001
DATE_SEPARATION = 60 # 30 pixels below clock
DATE_SIZE = 3 # How big to write the date
BTN_TEXT_SIZE = 3
BTN_TEXT_PAD = 8

@dataclass
class RectPos:
  x1: int 
  y1: int
  x2: int
  y2: int

@dataclass
class AnalogClockPos:
  x: int
  y: int
  r: int
  hash_pos: List[RectPos]

@dataclass
class HourPos:
  x1: int
  y1: int
  x2: int
  y2: int
  x3: int
  y3: int

@dataclass
class MinutePos:
  x1: int
  y1: int
  x2: int
  y2: int
  x3: int
  y3: int


class Coordinates:
  x: int
  y: int
  r: int
  phi: float
  
  def fromPolar(self, r, phi):
    self.x = r * np.cos(phi)
    self.y = r * np.sin(phi)

daysOfTheWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
point = Coordinates();
lastHourPos: HourPos
lastMinutePos: MinutePos
lastMinute = -1 # used to know when to redraw hands
lastDay = -1    # used to know when to redraw date

clockPos: AnalogClockPos
app = App(title="Clock", layout='grid')
app.full_screen = True
clockCanvas = Drawing(App, width = app.width / 2, height = app.height)

screenWidth = app.width
screenHeight = app.height 

last_touch_millis_check = 0


def approximatelyEqual(f1: float, f2: float):
  return abs(f1 - f2) < APPROXIMATION_VALUE

def eraseDate():
  global clockCanvas, screenWidth, screenHeight
  
  x1 = 0
  y1 = int(clockPos.x + clockPos.r + (DATE_SEPARATION / 2))
  x2 = screenWidth - 1
  y2 = screenHeight - 1
  
  clockCanvas.Fill_Rectangle(x1, y1, x2, y2, SCREEN_BACK_COLOR)

#display date
def drawDate(now: DateTime, firstTime: bool):
  if not firstTime:
    eraseDate()
   
  yPos = clockPos.y + clockPos.r + DATE_SEPARATION
  xPos = 3 * CLOCK_PADDING
  dateStr: str
  strMonth = str(now.month())
  strDay = str(now.day())
  
  if strMonth.length() < 2:
    strMonth = '0' + strMonth

  if strDay.length() < 2:
    strDay = '0' + strDay
  
    dateStr = strMonth + "/" + strDay + \
        "/" + str(now.year()) + " " + \
        daysOfTheWeek[now.dayOfTheWeek()] 
  
  clockCanvas.text(xPos, yPos, dateStr, color = CLOCK_HASH_COLOR,
                   size = DATE_SIZE)

# x and y are output parameters
def getClockPoint(r: int, phi: float, x: int, y: int):
  point.fromPolar(r, phi)
  # The point fromPolar is calculating points based off of a
  # 0,0 origin, but ours is at clockPos.x, clockPos.y,
  # which in a 320 width screen is point 160, 160
  x = point.getX() + clockPos.x
  y = point.getY() + clockPos.y


#returns float
def getAngleForMinute(theMinute: int):
  global CIRCLE_RADS
  
  minuteSlice = CIRCLE_RADS / 60 # Angle measurement in each hour

  # No negative angles
  if theMinute < 15:
    theMinute += 60

  # For minutes, 15 minutes is 0, so we have to take away 15 minutes
  theMinute -= 15 # Rotate my coordiate so 0 is the new "pole"

  return theMinute * minuteSlice

# Returns float to support fractional hours
# Needed because hour keeps moving slightly while minute hand moves
def getAngleForHour(theHour: float):
  global CIRCLE_RADS
  
  hourSlice = CIRCLE_RADS / 12 # Angle measurement in each minute

  # No negative hours
  if theHour < 3:
    theHour += 12

  theHour -= 3 # Rotate my coordiate so 12 is the new "pole"

  return theHour * hourSlice

def  drawInnerCircle():
  global clockCanvas, INNER_CIRCLE_COLOR, clockPos

  
  clockCanvas.oval(clockPos.x, clockPos.y, clockPos.x, clockPos.y, INNER_CIRCLE_COLOR)
  clockCanvas.oval(lockPos.x, clockPos.y, clockPos.x, clockPos.y, INNER_CIRCLE_COLOR / 2)

# Expects hour from 0 to 11, with 0 being 12 AM/PM
def drawTimeHash(theHou: int):
  myPos = clockPos.hash_pos[theHour]

  clockcanvas.Set_Draw_color(CLOCK_HASH_COLOR)
  
  if 0 == (theHour % 3):
    clockCanvas.Fill_Rectangle(myPos.x1, myPos.y1, myPos.x2, myPos.y2)
  else:
    clockCanvas.Draw_Line(myPos.x1, myPos.y1, myPos.x2, myPos.y2)

def drawFace():
  # First draw filled circle to get back color of clock
  clockCanvas.Set_Draw_color(CLOCK_FACE_COLOR)
  clockCanvas.Fill_Circle(clockPos.x, clockPos.y, clockPos.r)

  # Now draw outline of clock in CLOCK_HASH_COLOR
  clockCanvas.Set_Draw_color(CLOCK_HASH_COLOR);
  clockCanvas.Draw_Circle(clockPos.x, clockPos.y, clockPos.r);  

  # Then draw lines for 12 time marks
  for myHour in range(12):
     drawTimeHash(myHour)

def eraseLastMinute():
  clockCanvas.Set_Draw_color(CLOCK_FACE_COLOR)
  clockCanvas.Fill_Triangle(lastMinutePos.x1, lastMinutePos.y1,
    lastMinutePos.x2, lastMinutePos.y2, lastMinutePos.x3, lastMinutePos.y3)

def eraseLastHour():
  clockCanvas.Set_Draw_color(CLOCK_FACE_COLOR)
  clockCanvas.Fill_Triangle(lastHourPos.x1, lastHourPos.y1,
    lastHourPos.x2, lastHourPos.y2, lastHourPos.x3, lastHourPos.y3)

def drawHour(theHour: int, theMinute: int, firstTime: bool):
  if not firstTime:
    eraseLastHour()
  
  # first determine end of the hour hand triangle 
  # which is farthest point away from center of clock.
  # Use (x3,y3)
  fractionalHour = (1.0 * theHour) + (theMinute / 60.0) 
  hourAngle = getAngleForHour(fractionalHour)
  getClockPoint(HOUR_HAND_LENGTH, hourAngle, lastHourPos.x3, lastHourPos.y3)

  # Now get 2 base points, each is perpendicular to hour hand
  firstPhi = hourAngle - (CIRCLE_RADS / 4)
  secondPhi = hourAngle + (CIRCLE_RADS / 4)
  baseR = int(HOUR_HAND_BASE / 2)

  getClockPoint(baseR, firstPhi, lastHourPos.x1, lastHourPos.y1)
  getClockPoint(baseR, secondPhi, lastHourPos.x2, lastHourPos.y2)

  # Now draw hour hand
  clockCanvas.Set_Draw_color(HOUR_HAND_COLOR)
  clockCanvas.Fill_Triangle(lastHourPos.x1, lastHourPos.y1,
    lastHourPos.x2, lastHourPos.y2, lastHourPos.x3, lastHourPos.y3)

def drawMinute(theMinute: int, firstTime: bool):
  if not firstTime:
    eraseLastMinute()

  # first determine end of the minute hand triangle 
  # which is farthest point away from center of clock.
  # Use (x3,y3)
  minuteAngle = getAngleForMinute(theMinute)
  getClockPoint(MINUTE_HAND_LENGTH, minuteAngle, lastMinutePos.x3, lastMinutePos.y3)

  # Now get 2 base points, each is perpendicular to hour hand
  firstPhi = minuteAngle - (CIRCLE_RADS / 4)
  secondPhi = minuteAngle + (CIRCLE_RADS / 4)
  baseR = int(MINUTE_HAND_BASE / 2)

  getClockPoint(baseR, firstPhi, lastMinutePos.x1, lastMinutePos.y1)
  getClockPoint(baseR, secondPhi, lastMinutePos.x2, lastMinutePos.y2)

  # Now draw hour hand
  clockCanvas.Set_Draw_color(MINUTE_HAND_COLOR)
  clockCanvas.Fill_Triangle(lastMinutePos.x1, lastMinutePos.y1,
    lastMinutePos.x2, lastMinutePos.y2, lastMinutePos.x3, lastMinutePos.y3)

def drawHands(now : DateTime, firstTime: bool):
  drawHour(now.hour(), now.minute(), firstTime)
  drawMinute(now.minute(), firstTime)

def drawClock(firstTime: bool, forceDrawHands: bool):
  if firstTime:
    drawFace()

  now = clock.now()
  
  if firstTime or forceDrawHands or (now.minute() != lastMinute): 
    drawHands(now, firstTime)

  drawInnerCircle()
  
  if firstTime or (now.day() != lastDay):
    drawDate(now, firstTime)

  lastMinute = now.minute()
  lastDay = now.day()

# Used to draw lines for 1,2,4,5,7,8,10,11
def calculateRectPosForLine(theHour: int, x1: int, y1: int, x2: int, y2: int):

  phi = getAngleForHour(theHour)

  r = clockPos.r - HASH_LINE_SIZE - 1 # The first point 

  getClockPoint(r, phi, x1, y1)
  
  r = clockPos.r - 1 # The second point
  
  getClockPoint(r, phi, x2, y2);

# Expects hour from 0 to 11, 0 = 12 AM/PM
def calculateRectPos(hash_pos: RectPos, theHour: int):
    if theHour == 0: # RECTANGLE
      hash_pos.x1 = clockPos.x - (HASH_RECT_WIDTH / 2)
      hash_pos.y1 = clockPos.y - clockPos.r + 1
      hash_pos.x2 = hash_pos.x1 +  HASH_RECT_WIDTH
      hash_pos.y2 = hash_pos.y1 + HASH_RECT_HEIGHT
      return
    if theHour == 3: # RECTANGLE sideways
      hash_pos.x1 = clockPos.x + clockPos.r - HASH_RECT_HEIGHT - 1
      hash_pos.y1 = clockPos.y - (HASH_RECT_WIDTH / 2)
      hash_pos.x2 = hash_pos.x1 +  HASH_RECT_HEIGHT
      hash_pos.y2 = hash_pos.y1 + HASH_RECT_WIDTH
      return
    if theHour == 6: # RECTANGLE
      hash_pos.x1 = clockPos.x - (HASH_RECT_WIDTH / 2)
      hash_pos.y1 = clockPos.y + clockPos.r
      hash_pos.x2 = hash_pos.x1 +  HASH_RECT_WIDTH
      hash_pos.y2 = hash_pos.y1 - HASH_RECT_HEIGHT
      return
    if theHour == 9: # RECTANGLE sideways
      hash_pos.x1 = clockPos.x - clockPos.r + 1
      hash_pos.y1 = clockPos.y - (HASH_RECT_WIDTH / 2)
      hash_pos.x2 = hash_pos.x1 +  HASH_RECT_HEIGHT
      hash_pos.y2 = hash_pos.y1 + HASH_RECT_WIDTH     
      return
    # LINE
    calculateRectPosForLine(
        theHour,
        hash_pos.x1,
        hash_pos.y1,
        hash_pos.x2,
        hash_pos.y2)

def calculateClockPosition():
  # We expect to run in vertical position, where width is less than height

  # The x origin
  clockPos.r = (screenWidth - 2 * CLOCK_PADDING) / 2
  clockPos.x = CLOCK_PADDING + clockPos.r
  clockPos.y = CLOCK_PADDING + clockPos.r

  # Now set the positions for the 12 hashes for hours
  for myHour in range(12):
    calculateRectPos(clockPos.hash_pos[myHour], myHour)

def setup(): 
  Serial.begin(9600)
  
  clockCanvas.Init_LCD();
  
  clockCanvas.Set_Rotation(0);
  clockCanvas.Set_Text_Back_colour(BLACK);
  clockCanvas.Fill_Screen(SCREEN_BACK_COLOR);

  # Now setup Analog Clock Info
  calculateClockPosition()

def printTime(msg: str, tm: DateTime):
  hour = tm.hour()
  min = tm.minute()

  Serial.println(msg + " - H=" + String(hour) + ":" + String(min))

setup()

while True:
  curMillis = millis()
  
  #Last condition is mullis rolled over
  if  0 == lastMillis or \
      curMillis < lastMillis or \
      (curMillis - lastMillis) >= UPDATE_MILLIS: 
    
    drawClock(firstRun, False)
    Serial.println("Time to draw the clock!")
    firstRun = False
    lastMillis = curMillis

