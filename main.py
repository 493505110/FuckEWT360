import logging
import time

from selenium import webdriver
from selenium.common import JavascriptException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

USER = "账号"
PASS = "985211"


def switchNew():
    newHandle = driver.window_handles[-1]
    logging.info(f"切换到新页面: {newHandle}")
    driver.switch_to.window(newHandle)


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] %(filename)s(line:%(lineno)d) - %(levelname)s: %(message)s",
                        level=logging.INFO, datefmt="%Y/%m/%d %H:%M:%S")
    logging.info("正在启动Chrome...")
    driver = webdriver.Chrome()
    ac = ActionChains(driver)
    driver.maximize_window()
    driver.get("https://teacher.ewt360.com/")
    logging.info(driver.title)
    driver.implicitly_wait(10)  # 隐式等待十秒
    logging.info("尝试登录...")
    userT = driver.find_element(By.ID, "login__password_userName")
    userT.send_keys(USER)
    passT = driver.find_element(By.ID, "login__password_password")
    passT.send_keys(PASS)
    subBtn = driver.find_element(By.CLASS_NAME, "ant-btn-primary")
    subBtn.click()
    driver.find_element(By.LINK_TEXT, "我的假期").click()
    driver.close()
    switchNew()
    driver.find_element(By.CLASS_NAME, "ant-btn-primary").click()
    logging.info("寻找左滑按钮...")
    leftBtn = driver.find_element(By.CLASS_NAME, "left-icon")
    while True:
        try:
            ac.click(leftBtn)
            ac.perform()
        except JavascriptException:
            logging.info("页面最左")
            logging.info("获取完成度...")
            datas = (driver.find_element(By.CLASS_NAME, "swiper-item-box")
                     .find_element(By.XPATH, "./*")
                     .find_elements(By.XPATH, "./*"))
            time.sleep(1)  # 等加载
            for data in datas:
                pdata = data.find_element(By.TAG_NAME, "div")
                pdata2 = data.find_element(By.TAG_NAME, "p")
                day = pdata.text
                progress = pdata2.text
                s = progress.split("/")
                if s[0] != s[1]:
                    logging.info(f"{day}的进度为{progress}")
                    ac.click(data)
                    ac.perform()
                    time.sleep(1)
                    lessonList = (driver.find_element(By.CLASS_NAME, "ant-spin-container")
                                  .find_element(By.XPATH, "./*")
                                  .find_elements(By.XPATH, "./*"))
                    if lessonList[-1].text == "加载更多":
                        logging.info("发现更多课程,重新获取...")
                        ac.click(lessonList[-1])
                        ac.move_to_element(data)
                        ac.perform()
                        lessonList = (driver.find_element(By.CLASS_NAME, "ant-spin-container")
                                      .find_element(By.XPATH, "./*")
                                      .find_elements(By.XPATH, "./*"))[:-1]
                    else:
                        lessonList.pop()
                    for i in lessonList:
                        ac.move_to_element(i)
                        ac.perform()
                        lesson = i.find_elements(By.XPATH, "./*")
                        lessonName = lesson[0].find_element(By.XPATH, "./*").text
                        lessonStat = lesson[1].find_elements(By.XPATH, "./*")[1].text \
                            if lesson[1].text != "已完成" else "已完成"
                        logging.info(f"{lessonName} | {lessonStat}")
                        if lessonStat == "去学习":
                            ac.click(lesson[0])
                            ac.perform()
                            time.sleep(3)  # 这里必须要等，不等无法切换到新页面
                            switchNew()
                            if (("xinli.ewt360.com" in driver.current_url) or
                                    ("web.ewt360.com/spiritual-growth" in driver.current_url)):
                                time.sleep(5)
                                logging.info(f"{lessonName} | 已完成")
                                driver.close()
                                switchNew()
                            else:
                                playBtn = driver.find_element(By.CLASS_NAME, "vjs-big-play-button")
                                playBtn.click()  # 点击播放按钮
                                driver.execute_script('document.querySelector("video").playbackRate = 2')
                                driver.execute_script('document.querySelector("video").muted = true')
                                video = driver.find_element(By.TAG_NAME, "video")
                                while True:
                                    stupidList = driver.find_elements(By.CLASS_NAME, "earnest_check_mask_box")
                                    stupidList2 = driver.find_elements(By.CLASS_NAME, "action-skip")
                                    if stupidList:
                                        ac.click(stupidList[0])
                                        ac.perform()
                                        logging.info("EWT挂机检测")
                                    if stupidList2:
                                        ac.click(stupidList2[0])
                                        ac.perform()
                                        logging.info("EWT问题检测")
                                    currentTime = video.get_attribute("currentTime")  # 当前时间
                                    duration = video.get_attribute("duration")  # 视频总时长
                                    time.sleep(5)  # 每隔五秒检查一次视频看没看完
                                    if currentTime == duration:
                                        logging.info(f"{lessonName} | 已完成")
                                        driver.close()
                                        switchNew()
                                        break
            break

    driver.quit()
