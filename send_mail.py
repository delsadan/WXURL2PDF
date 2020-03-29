# --coding=utf-8
import yagmail
import os
from loguru import logger
from configparser import ConfigParser

# 日志文件配置
if not os.path.exists('log'):
    os.mkdir('log')
logger.add('./log/send_mail.log', rotation='10 MB', enqueue=True, )


class SendMail:
    def __init__(self):
        cfg = ConfigParser()
        cfg.read('./config/config.ini')
        self.username = cfg['smtp']['username']
        self.password = cfg['smtp']['password']
        self.host = cfg['smtp']['host']

    def send_mail(self, receiver1, subject1, content1=None, attachment1=None):
        try:
            yag = yagmail.SMTP(user=self.username, password=self.password, host=self.host, port=465)
            yag.send(to=receiver1, subject=subject1, contents=content1, attachments=attachment1, )
            logger.success('邮件已成功发送给：{}, 主题为：{}, 内容为：{}, 附件为：{}'.format(receiver1, subject1, content1, attachment1))
        except Exception as e:
            logger.error('主题为：{} 的邮件发送失败，详情：{}'.format(subject1, e))
            return


if __name__ == '__main__':
    receiver = 'ooooo@qq.com'
    attachment = u'./PDF_output/{}.pdf'.format('民航局最新通知！国际航班重大调整')
    subject = '测试邮件'
    content = '你好，这是一封测试邮件！'
    s = SendMail()
    s.send_mail(receiver, subject, content, attachment1=attachment)
