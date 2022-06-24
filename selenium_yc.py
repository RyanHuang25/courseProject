# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: selenium_yc.py
@Time: 2022/6/17 15:42
@Email: leo.r.huang@microcore.tech
@Desc: 
'''

import time,platform
from selenium import webdriver

class YCSelenium:
    def __init__(self):
        self.user_list = ['350521198201106019', '350221198009210039', '350625198709111522',
                          '350204198112137013', '350823198806162629']
        self.userName = '350521198201106019'
        self.passwd = 'KF123456'
        self.startRequest()

    def startRequest(self):
        '''
        打开对应网站
        :return:
        '''
        if platform.system() == "Darwin":
            chrome_path = '/Users/huangrenwu/Project/course_spiders/chromedriver'
        else:
            chrome_path = 'D:/Project/course_spiders/chromedriver.exe'
        self.course_count = 0
        self.bro = webdriver.Chrome(executable_path=chrome_path)
        self.bro.get('https://yk.myunedu.com/#/login')
        time.sleep(5)
        self.login()

    def login(self):
        '''
        登陆账号和密码，并点击button按钮
        :return:
        '''
        # 输入账号密码
        self.bro.find_element_by_id('ddd').send_keys(self.userName)
        self.bro.find_element_by_id('bbb').send_keys(self.passwd)
        # 点击button登陆按钮
        self.bro.find_element_by_xpath("//div[@class='btn-wrap']/button").click()
        # self.course_list()

class SeleniumSpider:

    def __init__(self):
        self.user_list = ['350823198806162629']
        self.passwd = 'KF123456'
        for user in self.user_list:
            print('=' * 100)
            self.userName = user
            self.startRequest()

    def startRequest(self):
        '''
        打开对应网站
        :return:
        '''
        if platform.system() == "Darwin":
            chrome_path = '/Users/huangrenwu/Project/course_spiders/chromedriver'
        else:
            chrome_path = 'D:/Project/course_spiders/chromedriver.exe'
        self.course_count = 0
        self.bro = webdriver.Chrome(executable_path=chrome_path)
        self.bro.get('https://yk.myunedu.com/#/login')
        time.sleep(5)
        self.login()

    def login(self):
        # 输入账号密码
        self.bro.find_element_by_id('ddd').send_keys(self.userName)
        self.bro.find_element_by_id('bbb').send_keys(self.passwd)
        # 点击button登陆按钮
        self.bro.find_element_by_xpath("//div[@class='btn-wrap']/button").click()
        print(f'正在登陆账号：{self.userName}')
        self.course_list()

    def course_list(self):
        '''
        点击对应的课程
        :return:
        '''
        time.sleep(10)
        courseName = self.bro.find_elements_by_xpath("//div[@class='studyCourse-content-info-courseName fl']")
        # print(courseName[self.course_count].text)
        course_entrys = self.bro.find_elements_by_xpath("//div[@class='studyCourse-content-button1 base-btn1']")
        if self.course_count >= len(course_entrys):
            print('所有课程遍历完了')
            time.sleep(10)
            # self.bro.quit()
            return
        course_entrys[self.course_count].click()
        print(f"*"*100)
        self.title_count = 0
        self.title_list()

    def title_list(self):
        time.sleep(5)
        try:
            title_list = self.bro.find_elements_by_xpath("//div[@class='courseChapter-titleContent-title']")
            if self.title_count >= len(title_list):
                print('章节已经学习完成了...')
                self.course_count += 1
                self.bro.find_element_by_xpath("//div[@class='main-tab-item-select active-tab']").click()
                time.sleep(10)
                self.bro.refresh()
                # self.bro.find_element_by_xpath("//div[@class='navigation-button-text']").click()
                self.course_list()
            else:
                print(f"正在处理章节： {title_list[self.title_count].text}")
                title_list[self.title_count].click()
                time.sleep(0.5)
                # fileStatus = self.bro.find_elements_by_xpath("//div[@class='videoFile-read flex-cont flex-centerbox opacity1']")
                if self.bro.find_elements_by_class_name('videoName') == []:
                    print(f"章节 {title_list[self.title_count].text} 没有文档")
                    self.title_count += 1
                    self.title_list()
                # elif fileStatus != []:
                #     print(f'文件已经学习过了')
                #     self.title_count += 1
                #     self.title_list()
                else:
                    self.pdf_count = 0
                    self.pdfread()
        except:
            self.title_list()

    def pdfread(self):
        pdfs = self.bro.find_elements_by_xpath("//span[@class='videoFile-title-filename']")
        if pdfs == []:
            self.title_count += 1
            self.title_list()
        else:
            if self.pdf_count >= len(pdfs):
                self.title_count += 1
                self.title_list()
            else:
                print(f"正在学习： {pdfs[self.pdf_count].text}")
                pdfs[self.pdf_count].click()
                try:
                    self.backup()
                except:
                    time.sleep(10)
                    self.backup()

    def backup(self):
        time.sleep(10)
        self.bro.find_element_by_xpath('//div[@class="navigation-button-text"]').click()
        time.sleep(5)
        self.pdf_count += 1
        self.pdfread()

if __name__ == '__main__':
    SeleniumSpider()
