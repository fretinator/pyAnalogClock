# ****************************************************************************************
# Draw an Analog Clock using a little Rectangular to Polar Coordinate Fun. Uses RTC Clock
# to keep time. 
# ****************************************************************************************
import time
from datetime import datetime

from guizero import App, Drawing
from dataclasses import dataclass
import numpy as np
from typing import List

SCREEN_BACK_COLOR = "BLUE"
CLOCK_HASH_COLOR = "BLACK"
CLOCK_FACE_COLOR = "WHITE"
HOUR_HAND_COLOR = "BLACK"
MINUTE_HAND_COLOR = "GRAY"
INNER_CIRCLE_COLOR = "GREEN"

curMillis = 0
lastMillis = 0
UPDATE_MILLIS = 5000  # Every second
firstRun = True
prevDayOfMonth = -1
CLOCK_PADDING = 10
HASH_LINE_SIZE = 16
HASH_RECT_HEIGHT = 16
HASH_RECT_WIDTH = 8
INNER_CIRCLE_RADIUS = 8
HOUR_HAND_BASE = 24
HOUR_HAND_LENGTH = 60
MINUTE_HAND_BASE = 12
MINUTE_HAND_LENGTH = 100
CIRCLE_RADS = 2 * np.pi
APPROXIMATION_VALUE = 0.001
DATE_SEPARATION = 60  # 30 pixels below clock
DATE_SIZE = 3  # How big to write the date
BTN_TEXT_SIZE = 3
BTN_TEXT_PAD = 8



@dataclass
class RectPos:
    x1: int
    y1: int
    x2: int
    y2: int


class AnalogClockPos:

    hash_positions = []
    x: int
    y: int
    r: int

    def add_pos(rect_pos: RectPos):
        AnalogClockPos.hash_positions.append(rect_pos)

    def get_pos(the_hour: int):
        return AnalogClockPos.hash_positions[the_hour]

    def clear_pos():
        AnalogClockPos.hash_positions.clear()

    def __init(self):
        x = 0
        y = 0
        r = 0


@dataclass
class TrianglePos:
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

    def __init__(self):
        x = 0
        y = 0
        r = 0
        phi = 0.0

    def from_polar(self, r, phi):
        self.x = r * np.cos(phi)
        self.y = r * np.sin(phi)


daysOfTheWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
point = Coordinates()
lastHourPos = TrianglePos(0, 0, 0, 0, 0, 0)
lastMinutePos = TrianglePos(0, 0, 0, 0, 0, 0)
lastMinute = -1  # used to know when to redraw hands
lastDay = -1  # used to know when to redraw date

clockPos: AnalogClockPos = AnalogClockPos()

app = App(title="Clock", layout='grid', height=600, width=800,
          bg=SCREEN_BACK_COLOR)
app.full_screen = True
clockWidth = int(app.width / 2)
clockHeight = clockWidth # Circle
clockCanvas = Drawing(app, width=clockWidth, height=clockWidth,
                      grid=[0, 0])


def approximately_equal(f1: float, f2: float):
    return abs(f1 - f2) < APPROXIMATION_VALUE


def erase_date():
    global clockCanvas, clockWidth, clockHeight, clockPos

    x1 = 0
    y1 = int(clockPos.x + clockPos.r + (DATE_SEPARATION / 2))
    x2 = clockWidth - 1
    y2 = clockHeight - 1

    clockCanvas.rectangle(x1, y1, x2, y2, color=SCREEN_BACK_COLOR)


# display date
def draw_date(now: datetime, first_time: bool):
    global clockPos

    if not first_time:
        erase_date()

    y_pos = clockPos.y + clockPos.r + DATE_SEPARATION
    x_pos = 3 * CLOCK_PADDING
    date_str: str = ''
    str_month = str(now.month)
    str_day = str(now.day)

    if len(str_month) < 2:
        str_month = '0' + str_month

    if len(str_day) < 2:
        str_day = '0' + str_day

        date_str = str_month + "/" + str_day + \
                   "/" + str(now.year) + " " + \
                   daysOfTheWeek[now.weekday()]

    clockCanvas.text(x_pos, y_pos, date_str, color=CLOCK_HASH_COLOR,
                     size=DATE_SIZE)


# Guizero expects the bounding box if the circle, not the center
# and radius
def draw_circle(canvas: Drawing, x1: int, y1: int, r: int, drawColor: str,
                outlineOnly: bool):
    new_x1: int = x1 - r
    new_y1: int = y1 - r
    new_x2: int = x1 + r
    new_y2: int = y1 + r

    if outlineOnly:
        canvas.oval(new_x1, new_y1, new_x2, new_y2, outline_color=drawColor,
                    outline=True)
    else:
        canvas.oval(new_x1, new_y1, new_x2, new_y2, color=drawColor)


# x and y are output parameters
def get_clock_point(r: int, phi: float):
    global clockPos

    point.from_polar(r, phi)
    # The point fromPolar is calculating points based off of a
    # 0,0 origin, but ours is at clockPos.x, clockPos.y,
    # which in a 320 width screen is point 160, 160
    return point.x + clockPos.x, point.y + clockPos.y


# returns float
def get_angle_for_minute(theMinute: int):
    global CIRCLE_RADS

    minute_slice = CIRCLE_RADS / 60  # Angle measurement in each hour

    # No negative angles
    if theMinute < 15:
        theMinute += 60

    # For minutes, 15 minutes is 0, so we have to take away 15 minutes
    theMinute -= 15  # Rotate my coordinate so 0 is the new "pole"

    return theMinute * minute_slice


# Returns float to support fractional hours
# Needed because hour keeps moving slightly while minute hand moves
def get_angle_for_hour(theHour: float):
    global CIRCLE_RADS

    hour_slice = CIRCLE_RADS / 12  # Angle measurement in each minute

    # No negative hours
    if theHour < 3:
        theHour += 12

    theHour -= 3  # Rotate my coordinate so 12 is the new "pole"

    return theHour * hour_slice


def draw_inner_circle():
    global clockPos

    global clockCanvas, INNER_CIRCLE_COLOR, clockPos, CLOCK_HASH_COLOR

    draw_circle(clockCanvas, clockPos.x, clockPos.y, INNER_CIRCLE_RADIUS,
                INNER_CIRCLE_COLOR, False)
    draw_circle(clockCanvas, clockPos.x, clockPos.y, int(INNER_CIRCLE_RADIUS / 2),
                CLOCK_HASH_COLOR, True)


# Expects hour from 0 to 11, with 0 being 12 AM/PM
def draw_time_hash(theHour: int):
    global clockPos

    my_pos = AnalogClockPos.get_pos(theHour)

    if (theHour % 3) == 0:
        clockCanvas.rectangle(my_pos.x1, my_pos.y1, my_pos.x2, my_pos.y2, CLOCK_HASH_COLOR)
    else:
        clockCanvas.line(my_pos.x1, my_pos.y1, my_pos.x2, my_pos.y2, CLOCK_HASH_COLOR)


def draw_face():
    global clockPos

    # First draw filled circle to get back color of clock
    draw_circle(clockCanvas, clockPos.x, clockPos.y, clockPos.r, CLOCK_FACE_COLOR, False)

    # Now draw outline of clock in CLOCK_HASH_COLOR
    #draw_circle(clockCanvas, clockPos.x, clockPos.y, clockPos.r, CLOCK_HASH_COLOR, True)

    # Then draw lines for 12 time marks
    for myHour in range(12):
        draw_time_hash(myHour)


def erase_last_minute():
    clockCanvas.triangle(lastMinutePos.x1, lastMinutePos.y1,
                         lastMinutePos.x2, lastMinutePos.y2, lastMinutePos.x3,
                         lastMinutePos.y3, color=CLOCK_FACE_COLOR)


def erase_last_hour():
    clockCanvas.triangle(lastHourPos.x1, lastHourPos.y1,
                         lastHourPos.x2, lastHourPos.y2, lastHourPos.x3,
                         lastHourPos.y3, color=CLOCK_FACE_COLOR)


def draw_hour(theHour: int, theMinute: int, firstTime: bool):
    global lastHourPos

    print("Drawing hour: " + str(theHour))

    if not firstTime:
        erase_last_hour()

    # first determine end of the hour hand triangle
    # which is the furthest point away from center of clock.
    # Use (x3,y3)
    fractional_hour = (1.0 * theHour) + (theMinute / 60.0)
    hour_angle = get_angle_for_hour(fractional_hour)
    lastHourPos.x3, lastHourPos.y3 = get_clock_point(HOUR_HAND_LENGTH, hour_angle)

    # Now get 2 base points, each is perpendicular to hour hand
    first_phi = hour_angle - (CIRCLE_RADS / 4)
    second_phi = hour_angle + (CIRCLE_RADS / 4)
    base_r = int(HOUR_HAND_BASE / 2)

    lastHourPos.x1, lastHourPos.y1 = get_clock_point(base_r, first_phi)
    lastHourPos.x2, lastHourPos.y2 = get_clock_point(base_r, second_phi)

    # Now draw hour hand
    clockCanvas.triangle(lastHourPos.x1, lastHourPos.y1,
                         lastHourPos.x2, lastHourPos.y2, lastHourPos.x3,
                         lastHourPos.y3, color=HOUR_HAND_COLOR)


def draw_minute(theMinute: int, firstTime: bool):
    global lastMinutePos
    if not firstTime:
        erase_last_minute()

    # first determine end of the minute hand triangle
    # which is the farthest point away from center of clock.
    # Use (x3,y3)
    minute_angle = get_angle_for_minute(theMinute)
    lastMinutePos.x3, lastMinutePos.y3 = get_clock_point(MINUTE_HAND_LENGTH, minute_angle)

    # Now get 2 base points, each is perpendicular to hour hand
    first_phi = minute_angle - (CIRCLE_RADS / 4)
    second_phi = minute_angle + (CIRCLE_RADS / 4)
    base_r = int(MINUTE_HAND_BASE / 2)

    lastMinutePos.x1, lastMinutePos.y1 = get_clock_point(base_r, first_phi)
    lastMinutePos.x2, lastMinutePos.y2 = get_clock_point(base_r, second_phi)

    # Now draw hour hand
    clockCanvas.triangle(lastMinutePos.x1, lastMinutePos.y1,
                         lastMinutePos.x2, lastMinutePos.y2, lastMinutePos.x3,
                         lastMinutePos.y3, color=MINUTE_HAND_COLOR)


def draw_hands(now: datetime, firstTime: bool):
    draw_hour(now.hour, now.minute, firstTime)
    draw_minute(now.minute, firstTime)


def draw_clock(firstTime: bool = False, forceDrawHands: bool = False):
    global lastMinute, lastDay
    if firstTime:
        draw_face()

    now = datetime.now()

    print_time('Drawing clock', now)

    if firstTime or forceDrawHands or (now.minute != lastMinute):
        draw_hands(now, firstTime)

    draw_inner_circle()

    if firstTime or (now.day != lastDay):
        draw_date(now, firstTime)

    lastMinute = now.minute
    lastDay = now.day


# Used to draw lines for 1,2,4,5,7,8,10,11
def calculate_rect_pos_for_line(theHour: int):
    global clockPos

    phi = get_angle_for_hour(theHour)

    r = clockPos.r - HASH_LINE_SIZE - 1  # The first point

    x1, y1 = get_clock_point(r, phi)

    r = clockPos.r - 1  # The second point

    x2, y2 = get_clock_point(r, phi)

    return x1, y1, x2, y2


# Expects hour from 0 to 11, 0 = 12 AM/PM
def get_rect_pos(theHour: int):
    global clockPos

    rect_pos = RectPos(0, 0, 0, 0)

    if theHour == 0:  # RECTANGLE
        rect_pos.x1 = clockPos.x - (HASH_RECT_WIDTH / 2)
        rect_pos.y1 = clockPos.y - clockPos.r + 1
        rect_pos.x2 = rect_pos.x1 + HASH_RECT_WIDTH
        rect_pos.y2 = rect_pos.y1 + HASH_RECT_HEIGHT
        return rect_pos
    if theHour == 3:  # RECTANGLE sideways
        rect_pos.x1 = clockPos.x + clockPos.r - HASH_RECT_HEIGHT - 1
        rect_pos.y1 = clockPos.y - (HASH_RECT_WIDTH / 2)
        rect_pos.x2 = rect_pos.x1 + HASH_RECT_HEIGHT
        rect_pos.y2 = rect_pos.y1 + HASH_RECT_WIDTH
        return rect_pos
    if theHour == 6:  # RECTANGLE
        rect_pos.x1 = clockPos.x - (HASH_RECT_WIDTH / 2)
        rect_pos.y1 = clockPos.y + clockPos.r
        rect_pos.x2 = rect_pos.x1 + HASH_RECT_WIDTH
        rect_pos.y2 = rect_pos.y1 - HASH_RECT_HEIGHT
        return rect_pos
    if theHour == 9:  # RECTANGLE sideways
        rect_pos.x1 = clockPos.x - clockPos.r + 1
        rect_pos.y1 = clockPos.y - (HASH_RECT_WIDTH / 2)
        rect_pos.x2 = rect_pos.x1 + HASH_RECT_HEIGHT
        rect_pos.y2 = rect_pos.y1 + HASH_RECT_WIDTH
        return rect_pos
    # LINE
    rect_pos.x1, rect_pos.y1, rect_pos.x2, rect_pos.y2 = \
        calculate_rect_pos_for_line(theHour)

    return rect_pos


def calculate_clock_position():
    global clockPos, HOUR_HAND_LENGTH, MINUTE_HAND_LENGTH

    # The x origin
    clockPos.r = (clockWidth - 2 * CLOCK_PADDING) / 2
    clockPos.x = CLOCK_PADDING + clockPos.r
    clockPos.y = CLOCK_PADDING + clockPos.r

    # Now set the positions for the 12 hashes for hours
    AnalogClockPos.clear_pos()

    for myHour in range(12):
        AnalogClockPos.add_pos(get_rect_pos(myHour))

    HOUR_HAND_LENGTH = int(clockPos.r / 2)
    MINUTE_HAND_LENGTH = int(clockPos.r * 0.75)


def millis():
    now = datetime.now()
    return now.timestamp() * 1000


def fill_canvas(canvas: Drawing, drawColor: str):
    global lastMillis
    canvas.rectangle(0, 0, canvas.width, canvas.height, color=drawColor)


def print_time(msg: str, tm: datetime):
    print(msg + " - H=" + str(tm.hour) + ":" + str(tm.minute))

def handle_resize():
    global clockWidth, clockHeight, clockCanvas
    clockWidth = int(app.width / 2)
    clockHeight = clockWidth  # Circle
    clockCanvas.height = clockHeight
    clockCanvas.width = clockWidth

    calculate_clock_position()
    fill_canvas(clockCanvas, SCREEN_BACK_COLOR)
    draw_clock(True, True)



# Now setup Analog Clock Info
calculate_clock_position()
draw_clock(True, True)
clockCanvas.repeat(1000, draw_clock)
app.when_resized = handle_resize

app.display()
