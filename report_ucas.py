import requests
from bs4 import BeautifulSoup
import configparser
import datetime
import json

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,\
        image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36\
         (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36',
}

def load_info():
    config=configparser.ConfigParser()
    config.read('user_info.ini')
    user_info =config.items('baseconf')
    return dict(user_info)

class Report(object):
    def __init__(self,username_,passwd_):
        self.username=username_
        self.passwd=passwd_

        self.session=requests.session()
        self.session.headers.update(headers)
        
        self.base_url = "https://sep.ucas.ac.cn"
        self.login_url = "http://sep.ucas.ac.cn/slogin" #POST
        self.ehall_url = 'http://sep.ucas.ac.cn/portal/site/416/2095'  #GET
        self.post_url = "https://ehall.ucas.ac.cn/site/apps/launch"
    def __login(self):
        login_data_={
            "userName":self.username,
            "pwd":self.passwd,
            "sb":"sb"
        }
        res1=self.session.post(self.login_url,data=login_data_,headers=headers)
        soup1=BeautifulSoup(res1.text,"html.parser")
        #return res1,soup1
    
    def __get_redirect_url(self):
        headers_=headers
        sepuser_=self.session.cookies.get("sepuser")
        jsessionid_=self.session.cookies.get("JSESSIONID")
        headers_["Cookie"]="sepuser={0}; JSESSIONID={1}".format(sepuser_,jsessionid_)
        
        res2=self.session.get(self.ehall_url,headers=headers_)
        soup2=BeautifulSoup(res2.text,"html.parser")

        return soup2.find_all('a')[-2]['href']

    def __visit_ehall(self):
        redirect_url=self.__get_redirect_url()
        headers_=headers
        sepuser_ = self.session.cookies.get("sepuser")
        jsessionid_ = self.session.cookies.get("JSESSIONID")
        headers_["Cookie"] = "sepuser={0}; JSESSIONID={1}".format(sepuser_, jsessionid_)

        self.session.get(redirect_url,headers=headers_,verify=False)
        #soup3=BeautifulSoup(res3)

    def __post_data(self):
        info_dict=load_info()
        headers_=headers
        sepuser_=self.session.cookies.get("sepuser")
        vjuid_=self.session.cookies.get("vjuid")
        vjvd_=self.session.cookies.get("vjvd")
        vt_=self.session.cookies.get("vt")
        headers_["Cookie"] = 'sepuser="{0}"; vjuid={1}; vjvd={2}; vt={3}'.format(sepuser_,vjuid_,vjvd_,vt_)
        headers["Referer"] = 'https://ehall.ucas.ac.cn/v2/matter/start?id=740'

        post_data=dict()
    
        application_time = datetime.datetime.now().date().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-15]+"16:00:00.000Z"
        leaving_back_time=datetime.datetime.now().isoformat()[:-7]+"+08:00"
        data={
            "app_id":"740",
            "node_id":"",
            "form_data":
            {"1533":
                {
                    "User_18":"",
                    "User_19":"",
                    "User_20":"",
                    "User_27":"",
                    "User_56":"",
                    "User_82":"",
                    "Input_21":"",
                    "Input_22":"",
                    "Input_23":"",
                    "Input_24":"",
                    "Input_61":"",
                    "Radio_31":{"value":"1","name":"是yes"},
                    "Radio_32":{"value":"2","name":"否no"},
                    "Radio_71":{"name":"是yes","value":"1"},
                    "Radio_81":{"value":"2","name":"否no"},
                    "Calendar_28":application_time,
                    "Calendar_29":application_time,
                    "Calendar_30":leaving_back_time,
                    "Calendar_57":leaving_back_time,
                    "SelectV2_62":[{"value":3,"name":"3"}],
                    "ShowHide_58":"","ShowHide_64":"",
                    "ShowHide_72":"","Validate_77":"",
                    "DataSource_63":"",
                    "DataSource_66":"",
                    "DataSource_67":"",
                    "RepeatTable_33":
                    [{"Input_69":"",
                    "Input_41":"",
                    "Input_42":"",
                    "Calendar_43":None,
                    "Calendar_44":None,
                    "Input_45":""}]}},
                    "userview":1}
        data["form_data"]["1533"]["User_18"]=info_dict["name"]
        data["form_data"]["1533"]["User_19"]=info_dict["student_no"]
        data["form_data"]["1533"]["User_20"]=info_dict["gender"]
        data["form_data"]["1533"]["User_27"]=info_dict["phone"]
        data["form_data"]["1533"]["User_56"]=info_dict["name"]
        data["form_data"]["1533"]["User_82"]=info_dict["class"]
        data["form_data"]["1533"]["Input_22"]=info_dict["department"]
        data["form_data"]["1533"]["Input_23"]=info_dict["major"]
        data["form_data"]["1533"]["Input_61"]=info_dict["education"]

        post_data["data"]=json.dumps(data,ensure_ascii=False)
        post_data["agent_uid"]=""
        post_data["starter_depart_id"]=68879
        post_data["test_uid"]=0

        re=self.session.post(self.post_url,data=post_data,headers=headers_,verify=False)
        soup=BeautifulSoup(re.text)
        return re,soup

    def run(self):
        self.__login()
        self.__visit_ehall()
        self.__post_data()

if __name__=='__main__':
    user_info=load_info()
    username=user_info["username"]
    passwd=user_info["passwd"]
    report = Report(username, passwd)
    report.run()
