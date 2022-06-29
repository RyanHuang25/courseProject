# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: guokaiSpider.py
@Time: 2022/6/27 22:46
@Email: leo.r.huang@microcore.tech
@Desc: 
'''
import requests,pytesseract,execjs,time
from PIL import Image
from lxml import etree

class GuokaiSpider:

    def __init__(self):
        self.userName = '2251001404593'
        self.pwd = 'Ouchn@2021'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        goto,SunQueryParamsString,validateCode = self.startRequest()
        oauth2Url = self.loginPost(goto,SunQueryParamsString,validateCode)
        self.oauth2(oauth2Url)

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
        res = requests.get(indexLoginUrl,headers=headers,allow_redirects=False)
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
        res = requests.get(url,headers=headers,cookies=self.cookie)
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
        res = requests.post(url,headers=self.headers,cookies=self.cookie,data=data,allow_redirects=False)
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
        res = requests.get(url,headers=headers,cookies=self.cookie,allow_redirects=False)
        Location = res.headers['Location']
        return Location


if __name__ == '__main__':
    GuokaiSpider()
