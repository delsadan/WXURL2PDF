# --coding=utf-8
"""
基于python3.7开发
pip install beautifulsoup4
"""
import receive_url
import url2pdf
import send_mail
import time
import re
import random

if __name__ == '__main__':
    while True:
        a = receive_url.ReceiveMail()
        b = url2pdf.Html2PDF()
        receive_mail_info = a.receive_mails()

        if receive_mail_info:
            sender = receive_mail_info['sender_mail']
            subject = receive_mail_info['subject']
            url = receive_mail_info['url']
            output_name = re.sub(r'[\/:*?"<>|]', '-', subject)  # 标题重命名，去除特殊字符，避免windows保存失败
            b.html_to_pdf(url, output_name=output_name)
            s = send_mail.SendMail()
            time.sleep(1)
            s.send_mail(receiver1=sender, subject1=subject,
                        content1=url.replace('http', 'HTTP'), attachment1='./PDF_output/{}.pdf'.format(output_name))
        t = random.randint(30, 120)
        print('[*] 开始睡眠 {} s'.format(t))
        time.sleep(t)
