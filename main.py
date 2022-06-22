import requests,json,time

class Spider:

    def __init__(self):
        self.userName = '350623199003231014'
        self.passwd = "KF123456"
        self.login()
        self.overview()

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

    def overview(self):
        '''
        需要获取课程id
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/study/userPracticeScheme/overview'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        res = requests.post(url,headers=headers)
        userFosterSchemeTermCourseVOList = res.json()['data']['processList'][0]['userFosterSchemeTermCourseVOList']
        for userFosterSchemeTermCourseVO in userFosterSchemeTermCourseVOList:
            # print(userFosterSchemeTermCourseVO)
            if userFosterSchemeTermCourseVO['courseName'] == '法理学原理与实务':

                # 获取到课程id
                courseResourceId = userFosterSchemeTermCourseVO['courseResourceId']
                print(f"课程名称： {userFosterSchemeTermCourseVO['courseName']}")
                self.charterSectionList(courseResourceId)
            # break

    def charterSectionList(self,courseResourceId):
        '''
        针对没门课程进行一些参数获取，方便对课程中测试题，视频和ppt进行操作
        :param courseResourceId:
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/charterSection/charterSectionList'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "courseResourceId": courseResourceId
        }
        res = requests.post(url,headers=headers,data=json.dumps(data))
        # 获取到大章节
        charterSectionList = res.json()['data']['charterSectionList']
        for charterSection in charterSectionList:
            # 获取pdf文档信息
            try:
                sectionList = charterSection['sectionList']
                if sectionList == []:
                    materialList = charterSection['materialList']
                    for material in materialList:
                        fileList = material['fileList']
                        for file in fileList:
                            # 断定pdf文档是否已经读过
                            read = file['read']
                            if read:
                                print(f"文档 === >>> {file['name']} 已经被学习过了")
                            else:
                                # pdf文档没有被堵过则获取id
                                id = file['id']
                                self.getFileInfo(id)
                for section in sectionList:
                    materialList = section['materialList']
                    for material in materialList:
                        fileList = material['fileList']
                        for file in fileList:
                            # 断定pdf文档是否已经读过
                            read = file['read']
                            if read:
                                print(f"文档 ===>>> {file['name']} 已经被学习过了")
                            else:
                                # pdf文档没有被堵过则获取id
                                id = file['id']
                                self.getFileInfo(id)
            except Exception as e:
                print(e)

            # 获取测试题信息
            try:
                taskList = charterSection['taskList']
                for task in taskList:
                    if '线下任务' in task['taskName']:
                        continue
                    else:
                        # 测试题id
                        print(f"测试题 ===>>> {task['taskName']}")
                        examUserId = task['examUserId']
                        self.question(examUserId)
            except Exception as e:
                print(e)
        self.info(courseResourceId)


    def info(self,courseResourceId):
        url = 'https://yk.myunedu.com/yunkai/student/score/info'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "courseResourceId": courseResourceId
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))
        videoStudyInfoList = res.json()['data']['videoStudyInfoList']
        for videoStudyInfo in videoStudyInfoList:
            if videoStudyInfo['studyProgress'] == 100:
                print(f"视频 ===>>> {videoStudyInfo['videoName']} 已经被学习完了")
            else:
                id = videoStudyInfo['id']
                lastStudyTime = videoStudyInfo['lastStudyTime']
                self.getVideoInfo(id,lastStudyTime)
            #
            # # 获取视频信息
            # try:
            #     videoList = charterSection['videoList']
            #     for video in videoList:
            #         if video['duration'] == video['lastStudyTime']:
            #             print(f"视频{video['title']}已经被学习完了")
            #         else:
            #             id = video['id']
            #             lastStudyTime = video['lastStudyTime'] - 1
            #             self.getVideoInfo(id,lastStudyTime)
            # except Exception as e:
            #     print(e)

    def getVideoInfo(self,id,lastStudyTime):
        '''
        打开视频
        :param id:
        :param lastStudyTime:
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/charterSection/getVideoInfo'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "id": id
        }
        res = requests.post(url,headers=headers,data=json.dumps(data))
        print(f"正在学习: {res.json()['data']['title']}...")
        # 获取休息视频信息的id
        charterSectionId = res.json()['data']['charterSectionId']
        # 获取视频总长度
        duration = res.json()['data']['duration']

        while lastStudyTime == duration:
            time.sleep(10)
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
                "localCreateTime": int(time.time()*1000),
                "studyTime": 10,
                "uploadType": 1,
                "videoId": id,
                "videoType": 1
            }
            self.addVideoTime(addVideoTime_data)
            print(f"视频进度: {int(lastStudyTime/duration*100)}%")

    def addVideoProgress(self,data):
        url = 'https://yk.myunedu.com/yunkai/admin/userstudyrecord/addVideoProgress'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        res = requests.post(url,headers=headers,data=json.dumps(data))

    def addVideoTime(self,data):
        url = 'https://yk.myunedu.com/yunkai/admin/userstudyrecord/addVideoTime'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))

    def getFileInfo(self,id):
        '''
        打开pdf文档，设定文档已读，发起请求，自动已读
        :param id: pdf视频的id
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/charterSection/getFileInfo'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "id": id
        }
        res = requests.post(url,headers=headers,data=json.dumps(data))
        print(f"文档 ===>>> {res.json()['data']['name']} 正在学习")

        red_url = 'https://yk.myunedu.com/yunkai/web/study/readFile'
        data = {
            "fileId": id,
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))

    def question(self,examUserId):
        '''
        测试题进行答案处理
        :param examUserId:
        :return:
        '''
        url = 'https://yk.myunedu.com/yunkai/web/examPaper/question'
        headers = {
            "authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://yk.myunedu.com/yunkaiExamPC/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        }
        data = {
            "examUserId": examUserId,
            "status": None,
            "questionType": None,
            "subjectId": "2"
        }
        res = requests.post(url,headers=headers,data=json.dumps(data))
        # print(res.json())
        subList = res.json()['data']['subList']
        for sub in subList:
            # print(sub)
            if "选题" in sub['groupName']:
                answerItemList = sub['answerItemList']
                answer_item = {}
                for answerItem in answerItemList:
                    answer_item[answerItem['answerKey']] = answerItem['answerText']
                item = {
                    "answer": sub['answer'],
                    "groupId": sub['groupId'],
                    "groupName": sub['groupName'],
                    "topic": sub['topic'],
                    "answerItem": answer_item
                }
                print(item)
            elif sub['groupName'] == "填空题":
                item = {
                    "groupId": sub['groupId'],
                    "groupName": sub['groupName'],
                    "rightAnswer": sub['rightAnswer'],
                    "topic": sub['topic']
                }
                print(item)

if __name__ == '__main__':
    # Spider()
    import platform
    print(platform.system())
