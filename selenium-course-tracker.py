from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def getStatus(url, courseID):
    driver.get(url)
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "{}.0.courseOpenSections.courseOpenSectionsNumerator".format(courseID)))
        )
    except TimeoutException:
        print("Loading took too much time!")
        driver.quit()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    status = soup.find(id='{}.0.courseOpenSections.courseOpenSectionsNumerator'.format(courseID)).get_text()

    return status

def getCourseID(url):
    driver.get(url)
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "courseInfo"))
        )
    except TimeoutException:
        print("Loading took too much time!")
        driver.quit()

    soup = BeautifulSoup(driver.page_source, 'lxml')

    courseID = soup.find("span", {"id": "courseId"}).get_text()
    print("Course: {}".format(courseID))
    return courseID

def textSender(status, count):
    gmail_user = os.getenv("USER")
    gmail_password = os.getenv("PASS")

    sms_gateway = os.getenv("GATEWAY")
    # sms = 'ENROLL\nStatus: {}\nCount: {}'.format(status, count)
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = sms_gateway
    msg['Subject'] = ""
    body = ""
    if (status != 0):
        body = "Sections open: {}\n".format(status)
    else:
        body = "Still working\n"

    msg.attach(MIMEText(body, 'plain')) # Attach body

    sms = msg.as_string()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, sms_gateway, sms)
        server.quit()

        print('-----------------------Text sent!-----------------------')
    except:
        print('Something went wrong...')

if __name__ == "__main__":
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')

    index = input("Enter course index: ")
    url = 'https://sis.rutgers.edu/soc/#keyword?keyword={}&semester=92020&campus=NB&level=U'.format(index)

    courseID = getCourseID(url)

    count = 0
    status = '0'
    while (status == '0'):
        status = getStatus(url, courseID)
        count += 1
        print('Sections open: {} at {}'.format(status, count))
        if count % 360 == 0: # send reminder every hour
            textSender(status, count)
        time.sleep(10)

    if (status != '0'):
        textSender(status, count)

    driver.close()