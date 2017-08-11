# DoorDash Scheduling Bot
# Written by Evan Greavu July 9th 2016
# Version 1.2

import pyautogui
import time
from PIL import Image
from datetime import date
import logging
from twilio.rest import TwilioRestClient

# meta
version = 1.2
TEST_MODE = True

# Images to be scanned to determine state of the program
apps = Image.open("apps.PNG")
dasher = Image.open("dasher.PNG")
dashTitle = Image.open("dashTitle.PNG")
scheduleTitle = Image.open("scheduleTitle.PNG")
menu = Image.open("menu.PNG")
scheduleButton = Image.open("schedule.PNG")
scheduleSelected = Image.open("scheduleSelected.PNG")
logOut = Image.open("logOut.PNG")
kierland = Image.open("kierland.PNG")
ohNo = Image.open("ohNo.PNG")
timeSlotError = Image.open("timeSlotError.PNG")
timeCreateCancel = Image.open("timeCreateCancel.PNG")
emptiness = Image.open("emptiness.PNG")
emulatorOpen = Image.open("open.PNG")
emulatorClosed = Image.open("closed.PNG")

# Scheduling
SCHEDULE_TIME = 7 # Time of day the schedule is released (7 AM)
SCHEDULE_WINDOW = 10 # Minutes before and after the time to attempt scheduling
DEBUG_DAY = 0 # If 0, ignored. Otherwise try for the chosen day (1 = current)
TARGET_DAY = 7 # 7 represents 6 days ahead.

# Schedule in numerical coordinate format. 24 hour time. (startHour, startMinute, endHour, endMinute)
SCHEDULE = {'sunday' : (11, 0, 15, 30), 'monday' : (16, 30, 21, 0),
            'tuesday': (0, 0, 0, 0), 'wednesday' : (16, 30, 21, 0),
            'thursday': (11, 0, 15, 30), 'friday' : (11, 0, 15, 30),
            'saturday': (0, 0, 0, 0)}

# Android Emulator Interaction
TOPLEFT = (757, 112)
HOME = (987, 840)
APPS = (987, 780)

# Scheduling Screen Interaction
DAY_1 = (834, 321)
DAY_2 = (882, 322)
DAY_3 = (933, 323)
DAY_4 = (991, 324)
DAY_5 = (1032, 325)
DAY_6 = (1087, 326)
DAY_7 = (1142, 327)
TIME_SLOT = (900, 475)
TIME_SLOT2 = (900, 547)
TIME_SLOT3 = (900, 610)

# Clock Interaction
TIME_12 = (984, 493)
TIME_1 = (1027, 508)
TIME_2 = (1053, 535)
TIME_3 = (1067, 569)
TIME_4 = (1057, 614)
TIME_5 = (1025, 640)
TIME_6 = (985, 652)
TIME_7 = (947, 646)
TIME_8 = (915, 612)
TIME_9 = (907, 571)
TIME_10 = (922, 535)
TIME_11 = (942, 502)
TIME_OK = (1077, 701)
TIME_CANCEL = (1001, 700)
TIME_AM = (1069, 410)
TIME_PM = (1072, 437)
TIME_TOP = (989, 445)
TIME_BOTTOM = (973, 523)
TIME_CREATE = (1110, 616)

# Logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='run.log', level=logging.DEBUG)

# SMS
twilio = TwilioRestClient("AC7fb5fc61b1c0b21814d794319a219501", "ee2b1a7b9146d7ee143ee3afa455aa4d")
smsTo = "(480) 433-3368"
smsFrom = "(480) 360-5470"
smsIntro = "DoorDash Scheduling Bot Notification "

def sms(msg):
    formatted = smsIntro + time.strftime("%I:%M %p") + ":\n" + msg
    twilio.messages.create(from_=smsFrom, to=smsTo, body=formatted)

# Locate an image on the screen
def locate(img):
    return pyautogui.locateCenterOnScreen(img)

# Locate an image on the screen, 3 attempts to timeout and return nothing. Return the center coordinates if found.
def waitForLocate(img, imgAlt=None, timeout=3):
    i = 0
    while i < timeout:
        posA = locate(img)
        if (posA != None):
            print("waitForLocate() success1.")
            return posA
        else:
            if imgAlt != None:
                posB = locate(imgAlt)
                if posB != None:
                    print ("waitForLocate() success2.")
                    return posB
        time.sleep(0.1)
        i += 1
    logging.warning("waitForLocate() timeout.")
    print("Error: waitForLocate() timeout.")
    return None

# Click a position on the screen.
def click(pos):
    pyautogui.click(pos)
    time.sleep(0.5)

# Take a screenshot and save it into the screenshots folder. Info can be given to be added onto the name.
def screenshot(info=None):
    myTime = time.strftime("%H-%M-%S_%m-%d")
    name = "screencaps/screencap_" + myTime
    if info is not None: name += "_" + info
    image = pyautogui.screenshot()
    image.save(name+".PNG", "PNG")
    print ("Screenshot saved as " + name + ".PNG")
    image.close()

# Determine the state of the program.
def analyze():
    # 1 = Android Home Screen
    # 2 = Apps Screen
    # 3 = Menu Screen
    # 4 = Driver Dash Screen
    # 5 = Schedule Screen
    # 6 = Time Schedule Screen

    # These states have been deemed unneccessary for the current stage of development.

    if locate(scheduleTitle) is not None:
        return 5
    elif locate(dashTitle) is not None:
        return 4
    elif locate(timeCreateCancel) is not None:
        return 6
    elif locate(apps) is not None:
        return 1
    elif locate(dasher) is not None:
        return 2
    elif locate(logOut) is not None:
        return 3
    else:
        print ("State not found.")
        logging.warning("State not found.")
        click(waitForLocate(emulatorOpen,emulatorClosed))
        return None

# On the Android emulator, navigate to the Dasher app.
def goToDasherApp():
    state = analyze()
    if state == 1:
        click(APPS)
        click(waitForLocate(dasher))
    elif state == 4 or state == 5 or state == 3:
        print ("Already in Dasher app!")
    else:
        click(HOME)
        time.sleep(2)
        click(APPS)
        print ("Error: Unexpected state in goToDasherApp(): " + str(state))

# On the Android emulator, in the Dasher app, navigate to the scheduling page.
def goToScheduleScreen():
    state = analyze()
    if state == 4:
        click(waitForLocate(menu))
        click(waitForLocate(scheduleButton))
    elif state == 5:
        return True
    else:
        print ("Error: Unexpected state in goToScheduleScreen(): " + str(state))

# Click the given arbitrary weekday in the scheduling page, 1 to 7 from left to right.
def goToDay(day):
    if day == 1:
        click(DAY_1)
    elif day == 2:
        click(DAY_2)
    elif day == 3:
        click(DAY_3)
    elif day == 4:
        click(DAY_4)
    elif day == 5:
        click(DAY_5)
    elif day == 6:
        click(DAY_6)
    elif day == 7:
        click(DAY_7)
    time.sleep(1.5)

# Returns the current hour in 24h.
def getHour():
    return int(time.strftime("%H"))

# Returns the current minute.
def getMinute():
    return int(time.strftime("%M"))

# Determine the current time situation: close to the scheduling time, at the time, or not even close.
def getTimeState():
    # 0 - Nothing
    # 9 - Almost time
    # 1 - Time
    hour, minute = getHour(), getMinute()
    if hour == SCHEDULE_TIME - 1 and minute >= 60 - SCHEDULE_WINDOW:
        print ("It is almost time!")
        logging.info("It is almost time!")
        return 9
    if hour == SCHEDULE_TIME and minute <= SCHEDULE_WINDOW:
        print ("It is time!")
        logging.info("It is time!")
        return 1
    else:
        return 0

# Given an hour in 12h format, click the correct position on the clock.
def clockHour(hour):
    if hour == 12:
        click(TIME_12)
    elif hour == 1:
        click(TIME_1)
    elif hour == 2:
        click(TIME_2)
    elif hour == 3:
        click(TIME_3)
    elif hour == 4:
        click(TIME_4)
    elif hour == 5:
        click(TIME_5)
    elif hour == 6:
        click(TIME_6)
    elif hour == 7:
        click(TIME_7)
    elif hour == 8:
        click(TIME_8)
    elif hour == 9:
        click(TIME_9)
    elif hour == 10:
        click(TIME_10)
    elif hour == 11:
        click(TIME_11)
    else:
        print ("Error: Unexpected hour in clockHour(): " + hour)

# Click either AM or PM on the clock.
def clockHalf(pm):
    if pm:
        click(TIME_PM)
    else:
        click(TIME_AM)

# Take a minute and turn it into a position on the clock, like the hours would work (30 turns into 6).
def adaptMinute(minute):
    if minute >= 30:
        return 6
    elif minute < 30:
        return 12
    else:
        print ("Error: Unexpected minute in adaptMinute(): " + str(minute))
        return 12

# Take a 24h hour and find its correct hour in 12h format (17 turns into 5).
def adaptHour(hour):
    if hour > 12:
        return hour - 12
    else:
        return hour

# Navigate to the scheduling screen and the correct day (6 days in advance).
def prepare():
    click(waitForLocate(emulatorOpen, emulatorClosed))
    state = analyze()
    if state != 5:
        goToDasherApp()
        goToScheduleScreen()
    if DEBUG_DAY != 0:
        goToDay(DEBUG_DAY)
    else:
        goToDay(TARGET_DAY)
    print ("Ready to schedule.")

# Schedule dashes using the start time and end time buttons and the clock.
# sched is a coordinate time (startHour, startMinute, endHour, endMinute).
# Returns true to indicate an attempt to schedule.
def schedule(sched):
    # Prepare variables.
    startHour, startMinute = sched[0], sched[1]
    endHour, endMinute = sched[2], sched[3]
    startPm = False
    if startHour > 11:
        startPm = True
    endPm = False
    if endHour > 11:
        endPm = True
    # Execute.
    click(TIME_TOP)
    startHour = adaptHour(startHour)
    endHour = adaptHour(endHour)
    clockHour(startHour)
    clockHour(adaptMinute(startMinute))
    clockHalf(startPm)
    click(TIME_OK)
    click(TIME_BOTTOM)
    clockHour(endHour)
    clockHour(adaptMinute(endMinute))
    clockHalf(endPm)
    click(TIME_OK)
    click(TIME_CREATE)
    time.sleep(0.5)
    print ("CHECK..")
    screenshot("SuccessCheck")
    success = checkForSuccess()
    if success:
        print ("Success!")
        sms("Scheduling successful!")
    else:
        print ("Couldn't schedule!")
        sms("Scheduling unsuccessful.")
    return True

# Check the scheduling screen for the "time slot is not available" message, indicating a failed scheduling.
def checkForSuccess():
    check = locate(timeSlotError)
    if check is not None:
        return False
    else:
        return True

# Click on an arbitrary day and back to refresh the scheduling day.
def refreshDay(day):
    if day != 1:
        goToDay(1)
    else:
        goToDay(2)
    goToDay(day)

# Get the current day (isoweekday format).
def dayOfMorning():
    # 1 - Monday
    # 7 - Sunday
    return date.today().isoweekday()

# Turn a day number into a string (isoweekday format).
def stringDay(day):
    if day == 1:
        return 'monday'
    elif day == 2:
        return 'tuesday'
    elif day == 3:
        return 'wednesday'
    elif day == 4:
        return 'thursday'
    elif day == 5:
        return 'friday'
    elif day == 6:
        return 'saturday'
    elif day == 7:
        return 'sunday'

# Check if there is work to be scheduled on the target day.
def haveWorkOn(day):
    sched = SCHEDULE[day]
    if sched[0] == 0 and sched[1] == 0 and sched[2] == 0 and sched[3] == 0:
        return False
    else:
        return True

# Return the day 6 days in advance.
def getDay6():
    current = dayOfMorning()
    targ = current + 6
    if targ > 7:
        targ -= 7
    if DEBUG_DAY != 0:
        return DEBUG_DAY
    return targ

# At this stage of development, only 1 attempt will happen to schedule.
scheduleAttempted = False
sms("Initiated.")

# Loop to wait for the time and execute the test schedule.
while True:
    if TEST_MODE:
        time.sleep(2)
        prepare()
        time.sleep(2)
        goToDay(1)
        time.sleep(1)
        goToDay(2)
        time.sleep(1)
        goToDay(7)
        time.sleep(1)
        goToDay(6)
        time.sleep(1)
        print ("Test complete!")
        TEST_MODE = False
        time.sleep(3)
    timestate = getTimeState()
    if timestate == 9:
        prepare()
    if timestate == 1:
        # Within the window and time to schedule.
        if analyze() != 5:
            prepare()
        screenshot("WaitingForSchedule")
        if DEBUG_DAY != 0:
            refreshDay(DEBUG_DAY)
        else:
            refreshDay(TARGET_DAY)
        # Check if ready to schedule.
        ready = locate(emptiness)
        if ready is None:
            # Time slot buttons are up.
            screenshot("ScheduleUp")
            print ("Schedule is up!")
            if not scheduleAttempted:
                day = stringDay(getDay6())
                if haveWorkOn(day):
                    print("It's time to schedule for " + day)
                    click(TIME_SLOT3)
                    state = analyze()
                    if state != 6:
                        screenshot("Timeslot1Fail")
                        print ("Had to try for time slot 2!")
                        click(TIME_SLOT2)
                    screenshot("AfterTimeslotClicks")
                    sched = SCHEDULE[day]
                    print("Schedule for " + day + ": " + str(sched))
                    if not scheduleAttempted:
                        scheduleAttempted = schedule(sched)
                        print ("scheduleAttempted: " + str(scheduleAttempted))
                    else:
                        print ("Scheduling already attempted.")
                else:
                    print ("No schedule for this day.")
                    scheduleAttempted = True
            else:
                print ("Complete.")
                break
        else:
            print ("Schedule is not up.")
