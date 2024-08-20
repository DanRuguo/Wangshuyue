import os
import requests
import time
import zipfile
from io import BytesIO

max_campus_num = 99
max_college_num = 30

def post_with_retry(session, url, headers, data, retries=5, delay=3):
    for i in range(retries):
        try:
            response = session.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            print(f"POST 请求连接错误: {e}, 尝试重试第 {i + 1} 次...")
            time.sleep(delay)
        except requests.exceptions.HTTPError as e:
            print(f"POST 请求返回错误: {e}, 状态码: {response.status_code}")
            break
    return None


def download_with_retry(session, url, headers, retries=5, delay=2):
    for i in range(retries):
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                return response
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            print(f"下载连接错误: {e}, 尝试重试第 {i + 1} 次...")
            time.sleep(delay)
        except requests.exceptions.HTTPError as e:
            print(f"GET 请求返回错误: {e}, 状态码: {response.status_code}")
            break
    return None


def generate_sno(failed_campus_num=None, failed_college_num=None, failed_class_num=None):
    start_campus_num = 1 if failed_campus_num is None else failed_campus_num
    start_college_num = 1 if failed_college_num is None else failed_college_num
    start_class_num = 1 if failed_class_num is None else failed_class_num
    for campus_num in range(start_campus_num, max_campus_num + 1):  # 校区从01到20
        campus_str = f"{campus_num:02d}"
        for college_num in range(start_college_num, max_college_num + 1):  # 学院从01到24
            college_str = f"{college_num:02d}"
            for class_num in range(start_class_num, 100):  # 班级从01到99
                class_str = f"{class_num:02d}"
                for last_two_digits in range(1, 100):  # 尾号从01到99
                    sno_suffix = f"{last_two_digits:02d}"
                    yield f"2021{campus_str}{college_str}{class_str}{sno_suffix}"


def download_files_and_extract_photos():
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'connection': 'keep-alive',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'ASP.NET_SessionId=xpgfc112vl2l12fixtnm4ant; hallticket=257C87648308474391B46DAA8669C8F1',
        'origin': 'http://yktfwdt.sdust.edu.cn',
        'pragma': 'no-cache',
        'referer': 'http://yktfwdt.sdust.edu.cn/Page/Page',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    session = requests.Session()
    photos_dir = "photos"
    os.makedirs(photos_dir, exist_ok=True)

    failed_campus_num = None
    failed_college_num = None
    failed_class_num = None
    while True:
        found_file = False
        for sno in generate_sno(failed_campus_num, failed_college_num, failed_class_num):
            photo_path = os.path.join(photos_dir, f"{sno}.jpg")

            # 检查照片是否已存在
            if os.path.exists(photo_path):
                print(f"学号：{sno} 的照片已存在，跳过下载。")
                continue

            data = {'sno': sno, 'ename': '', 'json': 'true'}

            response = post_with_retry(session, 'http://yktfwdt.sdust.edu.cn/Photo/OutPic', headers, data)
            if response is None:
                print(f"POST 请求失败，学号：{sno}，重试次数耗尽")
                continue

            if response.status_code == 200 and 'ok_' in response.text:
                print(f"请求成功，学号：{sno}，响应内容：", response.text)

                result = response.text.strip('"')
                download_url = f"http://yktfwdt.sdust.edu.cn/File/D/{result.split('_')[1]}.zip"
                print("下载链接：", download_url)

                # time.sleep(0.1)

                download_response = download_with_retry(session, download_url, headers)

                if download_response and download_response.status_code == 200:
                    with zipfile.ZipFile(BytesIO(download_response.content)) as zip_file:
                        zip_file.extractall(photos_dir)
                    print(f"文件已解压到文件夹：{photos_dir}")
                    found_file = True
                else:
                    print(f"下载压缩包失败，学号：{sno}，重试次数耗尽")

            else:
                print(f"请求失败，学号：{sno}，状态码：", response.status_code)

                if sno[-2:] == "01":
                    if int(sno[6:8]) >= max_college_num:
                        print(f"校区 {sno[4:6]} 遍历完成，尝试下一个校区：{int(sno[4:6]) + 1:02d}")
                        failed_campus_num = int(sno[4:6]) + 1
                        failed_college_num = 1
                        failed_class_num = 1
                    else:
                        print(f"班级 {sno[8:10]} 遍历失败，尝试下一个学院：{int(sno[6:8]) + 1:02d}")
                        failed_college_num = int(sno[6:8]) + 1
                        failed_class_num = 1
                    break

                if sno[-2:] != "01":
                    failed_class_num = int(sno[8:10]) + 1
                    print(f"学号尾号不是01，班级 {sno[8:10]} 遍历失败，尝试下一个班级：{failed_class_num:02d}")
                    failed_college_num = int(sno[6:8])  # 保持学院号不变
                    break

            if found_file:
                failed_college_num = None
                failed_class_num = None

        if failed_campus_num and failed_campus_num > max_campus_num:
            print("所有校区遍历完成，未找到更多文件，结束。")
            break

    print("所有文件已下载并解压到文件夹：photos")


if __name__ == "__main__":
    download_files_and_extract_photos()
