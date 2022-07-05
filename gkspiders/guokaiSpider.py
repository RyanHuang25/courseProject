# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: guokaiSpider.py
@Time: 2022/6/27 22:46
@Email: leo.r.huang@microcore.tech
@Desc: 
'''

import requests,pytesseract,execjs,time,redis,json
from PIL import Image
from lxml import etree
import time

pika = redis.Redis(host='47.108.199.19',port=8379,db=4,password='spider666.')

class GuokaiSpider:

    def __init__(self):
        self.userName = '2251001404593'
        self.pwd = 'Ouchn@2021'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        # goto,SunQueryParamsString,validateCode = self.startRequest()
        # oauth2Url = self.loginPost(goto,SunQueryParamsString,validateCode)
        # codeUrl = self.oauth2(oauth2Url)
        # indexUrl = self.indexCode(codeUrl)
        # pika.lpush('guokai_cookie',json.dumps(self.cookie))
        self.cookie = json.loads(pika.lrange('guokai_cookie',0,1)[0])
        self.videoInfo = {}
        self.learningPC()

    def startRequest(self):
        goto, SunQueryParamsString = self.loginPage()
        validateCode = self.validateCode()
        if len(validateCode) == 4:
            pass
        else:
            print('验证码读取错误...')
            time.sleep(2)
            goto, SunQueryParamsString = self.startRequest()
        return goto, SunQueryParamsString, validateCode

    def loginPage(self):
        '''
        请求登录主页，获取到网站的cookie信息
        :return: goto,SunQueryParamsString
        '''
        indexLoginUrl = 'https://iam.pt.ouchn.cn/am/UI/Login?realm=%2F&service=initService&goto=https%3A%2F%2Fiam.pt.ouchn.cn%2Fam%2Foauth2%2Fauthorize%3Fservice%3DinitService%26response_type%3Dcode%26client_id%3D345fcbaf076a4f8a%26scope%3Dall%26redirect_uri%3Dhttps%253A%252F%252Fmenhu.pt.ouchn.cn%252Fouchnapp%252Fwap%252Flogin%252Findex%26decision%3DAllow'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        }
        res = requests.get(indexLoginUrl,headers=headers,allow_redirects=False,timeout=30)
        self.cookie = requests.utils.dict_from_cookiejar(res.cookies)
        print(self.cookie)
        tree = etree.HTML(res.text)
        goto = tree.xpath("//input[@name='goto']/@value")[0]
        SunQueryParamsString = tree.xpath("//input[@name='SunQueryParamsString']/@value")[0]
        return goto, SunQueryParamsString

    def validateCode(self):
        '''
        获取验证码
        :return:
        '''
        url = 'https://iam.pt.ouchn.cn/am/validate.code'
        headers = {
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://iam.pt.ouchn.cn/am/UI/Login?realm=/&service=initService&goto=https://iam.pt.ouchn.cn/am/oauth2/authorize?service=initService&response_type=code&client_id=345fcbaf076a4f8a&scope=all&redirect_uri=https%3A%2F%2Fmenhu.pt.ouchn.cn%2Fouchnapp%2Fwap%2Flogin%2Findex&decision=Allow",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        res = requests.get(url,headers=headers,cookies=self.cookie,timeout=30)
        with open('./code.jpg','wb') as fp:
            fp.write(res.content)
        text = pytesseract.image_to_string(Image.open('./code.jpg'),lang='eng')
        text = text.replace('\r','').replace('\n','').replace('\t','').replace(' ','')
        print(f"读取验证码： {text}")
        return text

    def loginPost(self,goto,SunQueryParamsString,validateCode):
        '''
        发送登录请求，按钮点击接口
        :return:
        '''
        url = 'https://iam.pt.ouchn.cn/am/UI/Login'
        data = {
            "IDToken1": self.strEnc(self.userName),
            "IDToken2": self.strEnc(self.pwd),
            "IDToken3": validateCode,
            "goto": goto,
            "gotoOnFail": "",
            "SunQueryParamsString": SunQueryParamsString,
            "encoded": "true",
            "gx_charset": "UTF-8"
        }
        print(f"正在登录：{data}")
        res = requests.post(url,headers=self.headers,cookies=self.cookie,data=data,allow_redirects=False,timeout=30)
        cookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key,value in cookies.items():
            self.cookie[key] = value
        print(f"cookies已经更新 ===>>> {self.cookie}")
        Location = res.headers['Location']
        print(f"重定向url: {Location}")
        return Location

    def strEnc(self,text):
        '''
        调用登录的加密算法
        :return:
        '''
        keyword = 'OqxQ1Iea4njSROH/N06Tuw=='
        node = execjs.get()
        ctx = node.compile(open('./des.js',encoding='utf8').read())
        pwd = ctx.eval(f'strEnc("{text}","{keyword}")')
        print(f'加密：{text} ===>>> {pwd}')
        return pwd

    def oauth2(self,url):
        '''
        重定向请求
        :return:
        '''
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "https://iam.pt.ouchn.cn/am/UI/Login?realm=%2F&service=initService&goto=https%3A%2F%2Fiam.pt.ouchn.cn%2Fam%2Foauth2%2Fauthorize%3Fservice%3DinitService%26response_type%3Dcode%26client_id%3D345fcbaf076a4f8a%26scope%3Dall%26redirect_uri%3Dhttps%253A%252F%252Fmenhu.pt.ouchn.cn%252Fouchnapp%252Fwap%252Flogin%252Findex%26decision%3DAllow"
        }
        res = requests.get(url,headers=headers,cookies=self.cookie,allow_redirects=False,timeout=30)
        Location = res.headers['Location']
        return Location

    def indexCode(self,url):
        '''
        重定向请求，获取重定向连接和更新cookie
        :param url:
        :return:
        '''
        res = requests.get(url,headers=self.headers,allow_redirects=False,timeout=30)
        cookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in cookies.items():
            self.cookie[key] = value
        print(f"cookies已经更新 ===>>> {self.cookie}")
        Location = res.headers['Location']
        print(f"重定向url: {Location}")
        return Location

    def learningPC(self):
        '''
        获取到个人课程的所有课程，提取出课程的url
        :return:
        '''
        url = 'https://menhu.pt.ouchn.cn/ouchnapp/wap/course/learning-pc'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Referer": "https://menhu.pt.ouchn.cn/site/ouchnPc/index"
        }
        cookies = {
            "UUkey": self.cookie['UUkey'],
            "eai-sess": self.cookie['eai-sess']
        }
        res = requests.get(url,headers=headers,cookies=cookies,timeout=30)
        courseList = res.json()['d']['list']
        for course in courseList:
            print(course)
            courseUrl = course['url']
            self.modules(courseUrl)
            break

    def content(self,courseUrl):
        '''
        获取课程的章节前的准备信息，获取cookie和refererUrl
        :param courseUrl:
        :return:
        '''
        # 向课程发起请求，第一次重定向
        oneHeaders = {
            "authority": "lms.ouchn.cn",
            "method": "GET",
            "path": courseUrl[24:],
            "scheme": "https",
            "Referer": "https://menhu.pt.ouchn.cn/",
            "Host": "lms.ouchn.cn",
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        res = requests.get(courseUrl,headers=oneHeaders,allow_redirects=False,timeout=30)
        oneLocation = res.headers['Location']
        print(f'重定向url: {oneLocation}')
        cookies = requests.utils.dict_from_cookiejar(res.cookies)
        print(f'获取到cookies： {cookies}')
        # 根据第一次重定向的结果，进行cookie更新并第二次请求发送
        twoHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Referer": "https://menhu.pt.ouchn.cn/",
            "Host": "lms-identity.ouchn.cn"
        }
        res = requests.get(oneLocation,headers=twoHeaders,cookies=cookies,timeout=30,allow_redirects=False)
        twoLocation = res.headers['Location']
        print(f'重定向url: {twoLocation}')
        twoCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key,value in twoCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        # 根据第二次重定向的结果，进行cookie更新并第三次请求发送
        threeHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "lms-identity.ouchn.cn",
        }
        res = requests.get(twoLocation, headers=threeHeaders, cookies=cookies, timeout=30, allow_redirects=False)
        threeLocation = res.headers['Location']
        print(f'重定向url: {threeLocation}')
        threeCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in threeCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        # 根据第三次重定向的结果，进行cookie更新并第四次请求发送
        fourHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "iam.pt.ouchn.cn",
        }
        res = requests.get(threeLocation, headers=fourHeaders, cookies=self.cookie, timeout=30, allow_redirects=False)
        fourLocation = res.headers['Location']
        print(f'重定向url: {fourLocation}')
        # 根据第四次请求重定向结果，进行第五次请求发送
        fiveHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "lms-identity.ouchn.cn"
        }
        res = requests.get(fourLocation,headers=fiveHeaders,cookies=cookies,timeout=30,allow_redirects=False)
        fiveCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in fiveCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        fiveLocation = res.headers['Location']
        print(f'重定向url: {fiveLocation}')
        sixHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "lms.ouchn.cn"
        }
        res = requests.get(fiveLocation,headers=sixHeaders,cookies=cookies,timeout=30,allow_redirects=False)
        sixCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in sixCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        sixLocation = res.headers['Location']
        print(f'重定向url: {sixLocation}')
        sevenHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "lms.ouchn.cn"
        }
        res = requests.get(sixLocation,headers=sevenHeaders,cookies=cookies,timeout=30,allow_redirects=False)
        sevenCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in sevenCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        sevenLocation = res.headers['Location']
        print(f'重定向url: {sevenLocation}')
        eightHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Host": "lms.ouchn.cn"
        }
        res = requests.get(sevenLocation,headers=eightHeaders,cookies=cookies,timeout=30,allow_redirects=False)
        eightCookies = requests.utils.dict_from_cookiejar(res.cookies)
        for key, value in eightCookies.items():
            cookies[key] = value
        print(f'更新cookies： {cookies}')
        return sevenLocation,cookies

    def modules(self,courseUrl):
        '''
        或许课程的所有章节，根据章节的id，可以获取到每个章节下面要学习的东西
        :param courseUrl:
        :return:
        '''
        courseId = courseUrl[-19:-8]
        ngUrl,couseCookies = self.content(courseUrl)
        url = f'https://lms.ouchn.cn/api/courses/{courseId}/modules'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Referer": ngUrl,
            "Host": "lms.ouchn.cn"
        }
        res = requests.get(url,headers=headers,cookies=couseCookies,allow_redirects=False,timeout=30)
        # 获取到已经学习的视频和测试题id集合
        self.myCompleteness(courseId,couseCookies,ngUrl)
        modules = res.json()['modules']
        for module in modules:
            print(module)
            id = module['id']
            self.allActivities(courseId,id,couseCookies)

    def myCompleteness(self,courseId,couseCookies,ngUrl):
        '''
        获取已经完成学习的视频和测试题
        :param courseId:
        :return:
        '''
        url = f'https://lms.ouchn.cn/api/course/{courseId}/my-completeness'
        headers = {
            "authority": "lms.ouchn.cn",
            "method": "GET",
            "path": f"/api/course/{courseId}/my-completeness",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "referer": ngUrl,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        res = requests.get(url,headers=headers,cookies=couseCookies,allow_redirects=False,timeout=30)
        self.exam_activity_complete = res.json()['completed_result']['completed']['exam_activity']
        self.learning_activity_complete = res.json()['completed_result']['completed']['learning_activity']

    def allActivities(self,courseId,id,couseCookies):
        '''
        处理对应章节的测试，学习视频等，获取处理这些对应的参数
        :param courseId:
        :param id:
        :param couseCookies:
        :return:
        '''
        url = f'https://lms.ouchn.cn/api/course/{courseId}/all-activities?module_ids=[{id}]&activity_types=learning_activities,exams,classrooms,live_records,rollcalls&no-loading-animation=true'
        headers = {
            "authority": "lms.ouchn.cn",
            "method": "GET",
            "path": f"/api/course/{courseId}/all-activities?module_ids=[{id}]&activity_types=learning_activities,exams,classrooms,live_records,rollcalls&no-loading-animation=true",
            "scheme": "https"
        }
        res = requests.get(url,headers=headers,cookies=couseCookies,timeout=30)
        # 学习
        learning_activities = res.json()['learning_activities']
        for learning_activity in learning_activities:
            if learning_activity['type'] == "page":
                # 学习文本
                pageId = learning_activity['id']
                if pageId in self.learning_activity_complete:
                    print(f"{learning_activity['title']} ===>>> 已经被学习过了")
                    continue
                self.activitiesRead(pageId,courseId,couseCookies)
            elif learning_activity['type'] == "online_video":
                # 视频
                videoId = learning_activity['id']
                if videoId in self.learning_activity_complete:
                    print(f"{learning_activity['title']} ===>>> 已经被学习过了")
                    continue
                print(f"{learning_activity['title']} ===>>> 正在学习视频：{videoId}")
                self.activitiesReadVideo(videoId,courseId,couseCookies)
        # 测试
        exams = res.json()['exams']
        for exam in exams:
            pass

    def activitiesRead(self,pageId,courseId,couseCookies):
        '''
        学习文本
        :param courseId:
        :param couseCookies:
        :return:
        '''
        url = f'https://lms.ouchn.cn/api/course/activities-read/{pageId}'
        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://lms.ouchn.cn/course/{courseId}/learning-activity/full-screen",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        res = requests.post(url,headers=headers,data=json.dumps({}),cookies=couseCookies,allow_redirects=False,timeout=30)
        print(f"文本：{res.json()['id']} ===>>> {res.json()['last_visited_at']} 正在学习")

    def activitiesGetDurtion(self,videoId,couseCookies):
        '''
        获取视频的总长度
        :param videoId:
        :param couseCookies:
        :return:
        '''
        url = f'https://lms.ouchn.cn/api/activities/{videoId}'
        headers = {
            "authority": "lms.ouchn.cn",
            "method": "GET",
            "path": f"/api/activities/{videoId}",
            "scheme": "https",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        res = requests.get(url,headers=headers,cookies=couseCookies,allow_redirects=False,timeout=30)
        duration = res.json()['uploads'][0]['videos'][0]['duration']
        duration = int(duration) + 1
        return duration

    def activitiesReadVideo(self,videoId,courseId,couseCookies):
        '''
        学习视频，对视频连接发起请求
        :return:
        '''
        url = f'https://lms.ouchn.cn/api/course/activities-read/{videoId}'
        headers = {
            "authority": 'lms.ouchn.cn',
            "method": "POST",
            "path": f"/api/course/activities-read/{videoId}",
            "scheme": "https",
            "referer": f"https://lms.ouchn.cn/course/{courseId}/learning-activity/full-screen",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        res = requests.post(url,headers=headers,data=json.dumps({}),cookies=couseCookies,allow_redirects=False,timeout=30)
        # print(f"视频：{res.json()['activity_id']} ===>>> {res.json()['last_visited_at']} 正在学习")
        try:
            end = res.json()['data']['end']
        except:
            end = 0
        self.onLineVideo(videoId,courseId,couseCookies,end)

    def onLineVideo(self,videoId,courseId,couseCookies,end):
        '''
        模拟观看视频
        :return:
        '''
        durtion = self.activitiesGetDurtion(videoId,couseCookies)
        print(f'视频总长度: {durtion},已经观看： {end}')
        while durtion>end:
            # time.sleep(10)
            start = end
            end += 60
            if end > durtion:
                end = durtion
            url = f'https://lms.ouchn.cn/api/course/activities-read/{videoId}'
            headers = {
                "authority": "lms.ouchn.cn",
                "method": "POST",
                "path": f"/api/course/activities-read/{videoId}",
                "scheme": "https",
                "Content-Type": "application/json",
                "referer": f"https://lms.ouchn.cn/course/{courseId}/learning-activity/full-screen",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            }
            data = {
                "end": end,
                "start": start
            }
            print(data)
            # self.onlineVideoRequest(end, start, couseCookies)
            print(url)
            res = requests.post(url,headers=headers,data=json.dumps(data),allow_redirects=False,timeout=30,cookies=couseCookies)
            print(res.json())
            # print(f"视频进度：{str(res.json()['data']['end']/durtion)[:5]}/%")
            print(f"视频进度：{str(end / durtion * 100)[:5]}%")

    def onlineVideoRequest(self,end,start,couseCookies):
        url = 'https://lms.ouchn.cn/statistics/api/online-videos'
        headers = {
            "authority": "lms.ouchn.cn",
            "method": "POST",
            "path": "/statistics/api/online-videos",
            "scheme": "https",
            "referer": f"https://lms.ouchn.cn/course/40000000809/learning-activity/full-screen",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        data = {
            "user_id":"40000654410",
            "org_id":"40000000001",
            "course_id":"40000000809",
            "module_id":"40000037163",
            "activity_id":"40000299118",
            "upload_id":"1552752",
            "reply_id": "",
            "comment_id": "",
            "forum_type":"",
            "action_type":"play",
            "is_teacher": False,
            "is_student":True,
            "ts": int(time.time()*1000),
            "user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "meeting_type":"online_video",
            "start_at":start,
            "end_at": end,
            "duration":"60",
            "master_course_id":"12195",
            "org_name":"四川开放大学",
            "org_code":"510",
            "user_no":"2251001404593",
            "user_name":"范晓军",
            "course_code":"202203-01206510",
            "course_name":"汽车机械基础",
            "dep_id":"40000000066",
            "dep_name":"四川省级机关电大高新教学点",
            "dep_code":"5100205"
        }
        res = requests.post(url,headers=headers,data=json.dumps(data),cookies=couseCookies,allow_redirects=False,timeout=30)



if __name__ == '__main__':
    GuokaiSpider()
