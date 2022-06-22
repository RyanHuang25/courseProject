# -*- coding: utf8 -*-
'''
@Author: huangrenwu
@File: readPDF.py
@Time: 2022/6/17 02:06
@Email: leo.r.huang@microcore.tech
'''

import time,platform
from selenium import webdriver

class SeleniumSpider:

    def __init__(self):
        if platform.system() == "Darwin":
            chrome_path = '/Users/huangrenwu/Project/course_spiders/chromedriver'
        else:
            chrome_path = 'D:/Project/course_spiders/chromedriver.exe'
        self.bro = webdriver.Chrome(executable_path=chrome_path)
        self.title_count = 0
        self.course_count = 0
        self.startRequest()

    def startRequest(self):
        '''
        打开对应网站
        :return:
        '''
        self.bro.get('https://yk.myunedu.com/#/login')
        time.sleep(5)
        # try:
        self.login()

    def login(self):
        # 输入账号密码
        self.bro.find_element_by_id('ddd').send_keys('350521198201106019')
        self.bro.find_element_by_id('bbb').send_keys('KF123456')
        # 点击button登陆按钮
        self.bro.find_element_by_xpath("//div[@class='btn-wrap']/button").click()
        self.course_list()

    def course_list(self):
        '''
        点击对应的课程
        :return:
        '''
        time.sleep(10)
        course_entrys = self.bro.find_elements_by_xpath("//div[@class='studyCourse-content-button1 base-btn1']")
        course_entrys[self.course_count].click()
        self.title_list()


    def title_list(self):
        time.sleep(5)
        try:
            title_list = self.bro.find_elements_by_xpath("//div[@class='courseChapter-titleContent-title']")
        except:
            self.title_list()
        try:
            print(title_list[self.title_count].text)
            title_list[self.title_count].click()
            time.sleep(0.5)
            if self.bro.find_elements_by_class_name('videoName') == []:
                self.title_count += 1
                self.title_list()
            elif self.bro.find_element_by_class_name("videoFile-read flex-cont flex-centerbox opacity1").text == '已读':
                print('################## 文档已经学习过了 ######################')
                self.title_count += 1
                self.title_list()
            else:
                self.pdfread()
        except:
            self.bro.find_element_by_xpath("//div[@class='navigation-button-text']").click()
            self.course_count += 1
            try:
                self.course_list()
            except:
                time.sleep(10)
                self.course_list()


    def pdfread(self):
        pdfs = self.bro.find_elements_by_xpath("//span[@class='videoFile-title-filename']")
        if pdfs == []:
            self.title_count += 1
            self.title_list()
        else:
            pdfs[0].click()
            try:
                self.backup()
            except:
                time.sleep(10)
                self.backup()


    def backup(self):
        time.sleep(10)
        self.bro.find_element_by_xpath('//div[@class="navigation-button-text"]').click()
        time.sleep(5)
        self.title_count += 1
        self.title_list()


SeleniumSpider()