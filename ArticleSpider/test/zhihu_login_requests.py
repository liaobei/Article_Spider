import requests
import http.cookiejar as cookielib
import re
import time
import os
from PIL import Image

agent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3236.0 Safari/537.36"

headers = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com/",
    "User-Agent":agent
}
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False

def get_xsrf():
    response = requests.get("https://www.zhihu.com/",headers=headers)
    # print(response.text)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text.replace("\n",""))
    if match_obj:
        return match_obj.group(1)
    else:
        return ""

def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha




#
# def get_index():
#     response = session.get("https://www.zhihu.com", headers=headers)
#     with open("index_page.html",'wb') as f:
#         f.write(response.text.encode("utf8"))
#     print("ok")

def zhihu_login(acount,password):
    #知乎登录
    _xsrf=get_xsrf()
    headers["X-Xsrftoken"] = _xsrf
    headers["X-Requested-With"] = "XMLHttpRequest"
    if re.match("1\d{10}",acount):
        print("phone login")
        post_url  = "https://www.zhihu.com/login/phone_num"
        post_data ={
            "_xsrf":_xsrf,
            "phone_num":acount,
            "password":password,
            "capatcha":get_captcha()
        }
        login_page = session.post(post_url,data=post_data,headers=headers)
        login_code = login_page.json()
        # if login_code['r'] == 1:
        #     # 不输入验证码登录失败
        #     # 使用需要输入验证码的方式登录
        #     post_data["captcha"] = get_captcha()
        #     response = session.post(post_url, data=post_data, headers=headers)
        #     login_code = response.json()
        #     print(login_code['msg'])
        session.cookies.save()


# get_index()
if isLogin():
        print('您已经登录')
else:
        zhihu_login("17770030411", "19950319")