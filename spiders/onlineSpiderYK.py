# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: onlineSpiderYK.py
@Time: 2022/6/24 11:37
@Email: leo.r.huang@microcore.tech
@Desc: 
'''


import requests,json,time,redis

pika = redis.Redis(host='47.108.199.19',port=8379,password='spider666.',db=4)

class YCSpider:

    def __init__(self):
        self.passwd = 'KF123456'
        while True:
            print('='*100)
            self.account = pika.rpop('yc_account')
            self.userName = json.loads(self.account)['account']
            self.login()

    def login(self):
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
        res = requests.post(url,headers=headers,data=json.dumps(data))
        # print(res.json())
        self.token = res.json()['data']['token']
        self.headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        self.overview()

    def overview(self):
        '''
        需要获取课程id
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/study/userPracticeScheme/overview'
        try:
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
                else:
                    print(f"课程：{userFosterSchemeTermCourseVO['courseName']} === {courseResourceEndTime} 已经到期了")
            userFosterSchemeTermCourseVOListNotStart = res.json()['data']['processList'][1]['userFosterSchemeTermCourseVOList']
            for userFosterSchemeTermCourseVO in userFosterSchemeTermCourseVOListNotStart:
                print('*' * 100)
                # 获取到课程id
                courseResourceId = userFosterSchemeTermCourseVO['courseResourceId']
                print(f"课程名称： {userFosterSchemeTermCourseVO['courseName']}")
                courseResourceBeginTime = userFosterSchemeTermCourseVO['courseResourceBeginTime']
                courseResourceBeginTime_str = time.mktime(time.strptime(courseResourceBeginTime, "%Y-%m-%d %H:%M:%S"))
                if courseResourceBeginTime_str < time.time():
                    self.info(courseResourceId)
            pika.lpush('yc_account_file',json.dumps(self.account))
        except:
            self.overview()

    def info(self, courseResourceId):
        url = 'https://yk.myunedu.com/yunkai/student/score/info'
        data = {
            "courseResourceId": courseResourceId
        }
        try:
            res = requests.post(url, headers=self.headers, data=json.dumps(data))
            videoStudyInfoList = res.json()['data']['videoStudyInfoList']
            self.notReadList = []
            for videoStudyInfo in videoStudyInfoList:
                if videoStudyInfo['studyProgress'] == 0:
                    self.notReadList.append(videoStudyInfo['id'])
                if videoStudyInfo['studyProgress'] == 100:
                    print(f"视频 ===>>> {videoStudyInfo['videoName']} 已经被学习完了")
                else:
                    id = videoStudyInfo['id']
                    lastStudyTime = videoStudyInfo['lastStudyTime']
                    if lastStudyTime:
                        lastStudyTime = lastStudyTime
                    else:
                        lastStudyTime = 0
                    self.getVideoInfo(id, lastStudyTime)
            self.task_list(courseResourceId)
        except:
            self.info(courseResourceId)

    def task_list(self,courseResourceId):
        url = 'https://yk.myunedu.com/yunkai/web/student/task/list'
        data = {
            "courseResourceId": courseResourceId
        }
        res = requests.post(url, headers=self.headers, data=json.dumps(data))
        recordList = res.json()['data']['recordList']
        for record in recordList:
            if '线上作业' in record['taskName']:
                if record['score']:
                    print(f"测试 {record['charterName']} 已经完成，分数：{record['score']}")
                else:
                    task_data = {
                        "id": record['examId'],
                        "subjectId": record['subjectId'],
                        "taskId": record['taskId']
                    }
                    print(f'正在答题：{record["charterName"]}...')
                    try:
                        self.start(task_data)
                    except Exception as e:
                        print(e)

    def start(self,task_data):
        url = 'https://yk.myunedu.com/yunkai/web/examPaper/start'
        res = requests.post(url, headers=self.headers, data=json.dumps(task_data),timeout=30)
        testUserId = res.json()['data']['testUserId']
        questionAnswers = []
        groups = res.json()['data']['groups']
        for group in groups:
            topic = group['topic']
            if topic == '单选题':
                questionType = 1
            elif topic == '多选题':
                questionType = 2
            elif topic == "判断题":
                questionType = 4
            elif topic == "填空题":
                questionType = 13
            questions = group['questions']
            for question in questions:
                answer = question['answer']
                answer_list = []
                if questionType == 1:
                    answer_list.append(answer)
                elif questionType == 2:
                    for i in answer:
                        answer_list.append(i)
                elif questionType == 4:
                    answer_list.append(answer)
                elif questionType == 13:
                    answers = answer.split(' ')
                    for an in answers:
                        answer_list.append(an[2:])

                update_data = {
                    "answer": answer_list,
                    "questionId": question['id'],
                    "questionType": questionType,
                    "sequence": question['sequence'],
                    "taskId": task_data['taskId'],
                    "userAnswerId": question['userAnswerId']
                }
                self.update(update_data)
                questionAnswer = {
                    "answer": answer_list,
                    "questionId": question['id'],
                    "questionType": questionType,
                    "sequence": question['sequence'],
                    "userAnswerId": question['userAnswerId']
                }
                questionAnswers.append(questionAnswer)
        submit_data = {
            "questionAnswers": questionAnswers,
            "taskId": task_data['taskId'],
            "testUserId": testUserId,
            "version": 0
        }
        self.submit(submit_data)

    def update(self,update_data):
        try:
            url = 'https://yk.myunedu.com/yunkai/web/examPaper/update'
            res = requests.post(url,headers=self.headers,data=json.dumps(update_data))
        except:
            self.update(update_data)

    def submit(self,submit_data):
        try:
            url = 'https://yk.myunedu.com/yunkai/web/examPaper/submit'
            res = requests.post(url,headers=self.headers,data=json.dumps(submit_data))
        except Exception:
            self.submit(submit_data)

    def getVideoInfo(self, id, lastStudyTime):
        '''
        打开视频
        :param id:
        :param lastStudyTime:
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/charterSection/getVideoInfo'
        data = {
            "id": id
        }
        try:
            res = requests.post(url, headers=self.headers, data=json.dumps(data))
            print(f"正在学习: {res.json()['data']['title']}...")
            # 获取休息视频信息的id
            charterSectionId = res.json()['data']['charterSectionId']
            # 获取视频总长度
            duration = res.json()['data']['duration']

            while lastStudyTime != duration:
                time.sleep(2)
                lastStudyTime += 10
                if lastStudyTime > duration:
                    lastStudyTime = duration
                addVideoProgress_data = {
                    "charterSectionId": charterSectionId,
                    "lastStudyTime": lastStudyTime,
                    "videoId": id
                }
                self.addVideoProgress(addVideoProgress_data)
                addVideoTime_data = {
                    "appType": 3,
                    "charterSectionId": charterSectionId,
                    "lastStudyTime": lastStudyTime,
                    "localCreateTime": int(time.time() * 1000),
                    "studyTime": 10,
                    "uploadType": 1,
                    "videoId": id,
                    "videoType": 1
                }
                self.addVideoTime(addVideoTime_data)
                print(f"视频进度: {str(lastStudyTime / duration * 100)[:5]}%")
        except:
            self.getVideoInfo(id, lastStudyTime)

    def addVideoProgress(self, data):
        try:
            url = 'https://yk.myunedu.com/yunkai/admin/userstudyrecord/addVideoProgress'
            res = requests.post(url, headers=self.headers, data=json.dumps(data))
        except:
            self.addVideoProgress(data)

    def addVideoTime(self, data):
        try:
            url = 'https://yk.myunedu.com/yunkai/admin/userstudyrecord/addVideoTime'
            res = requests.post(url, headers=self.headers, data=json.dumps(data))
        except Exception:
            self.addVideoTime(data)

YCSpider()

