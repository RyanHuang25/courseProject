# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: findScore.py
@Time: 2022/6/25 16:28
@Email: leo.r.huang@microcore.tech
@Desc: 
'''
import requests,time,json,redis

pika = redis.Redis(host='47.108.199.19',port=8379,password='spider666.',db=4)

class FindScore:

    def __init__(self):
        self.passwd = 'KF123456'
        self.userList = pika.lrange('yc_account_score',0,-1)
        for userName in self.userList:
            print("="*100)
            self.userName = json.loads(userName)['account']
            self.startRequest()

    def startRequest(self):
        url = 'https://yk.myunedu.com/yunkai/sys/identification/login'
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "userName": self.userName,
            "passwd": self.passwd,
            "orgId": 260,
            "rentId": 179,
            "loginType": 2
        }
        print(f"正在登陆账号：{self.userName}")
        try:
            res = requests.post(url, headers=headers, data=json.dumps(data))
            # print(res.json())
            try:
                self.token = res.json()['data']['token']
            except:
                print(res.json())
                return
            self.headers = {
                "authorization": self.token,
                "Content-Type": "application/json;charset=UTF-8",
                "Referer": "https://yk.myunedu.com/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
            }
            self.overview()
        except:
            self.startRequest()

    def overview(self):
        '''
        需要获取课程id
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/study/userPracticeScheme/overview'
        res = requests.post(url,headers=self.headers)
        userFosterSchemeTermCourseVOList = res.json()['data']['processList'][0]['userFosterSchemeTermCourseVOList']
        for userFosterSchemeTermCourseVO in userFosterSchemeTermCourseVOList:
            # print(userFosterSchemeTermCourseVO)
            # if userFosterSchemeTermCourseVO['courseName'] == '法理学原理与实务':
            print('*'*100)
            # 获取到课程id
            courseResourceId = userFosterSchemeTermCourseVO['courseResourceId']
            print(f"课程名称： {userFosterSchemeTermCourseVO['courseName']}")
            courseResourceEndTime = userFosterSchemeTermCourseVO['courseResourceEndTime']
            courseResourceEndTime_str = time.mktime(time.strptime(courseResourceEndTime,"%Y-%m-%d %H:%M:%S"))
            if courseResourceEndTime_str > time.time():
                self.info(courseResourceId)
                # self.info(courseResourceId)
            else:
                print(f"课程：{userFosterSchemeTermCourseVO['courseName']} === {courseResourceEndTime} 已经到期了")

    def info(self, courseResourceId):
        url = 'https://yk.myunedu.com/yunkai/student/score/info'
        data = {
            "courseResourceId": courseResourceId
        }
        try:
            res = requests.post(url, headers=self.headers, data=json.dumps(data),timeout=10)
            try:
                taskStudyTotalScore5 = res.json()['data']['taskStudyTotalScore5']
            except:
                taskStudyTotalScore5 = 0
            item = {
                "形考成绩": res.json()['data']['courseScore'],
                "直播成绩": res.json()['data']['liveStudyTotalScore'],
                "视频成绩": res.json()['data']['videoStudyTotalScore'],
                "测试成绩": taskStudyTotalScore5
            }
            print(item)
        except:
            self.info(courseResourceId)
FindScore()