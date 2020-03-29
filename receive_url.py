import os
import poplib
import base64
import re
import time
from configparser import ConfigParser
from email.header import decode_header
from email.parser import Parser
from loguru import logger

# 配置日志
if not os.path.exists('log'):
    os.mkdir('log')
logger.add('./log/receive_url.log', rotation='10 MB', enqueue=True, )


# 针对邮件正文进行解码
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def decode_base64(s, charset='utf8'):
    return str(base64.decodebytes(s.encode(encoding=charset)), encoding=charset)


class ReceiveMail:

    def __init__(self):
        cfg = ConfigParser()
        cfg.read('./config/config.ini', )
        self.username = cfg.get('pop3', 'username')
        self.password = cfg.get('pop3', 'password')
        self.allow_sender = cfg.get('receive', 'allow_sender').split(';')

        self.pop3_server = cfg.get('pop3', 'pop3_server')
        self.server = poplib.POP3(self.pop3_server)
        self.server.set_debuglevel(0)
        try:
            self.server.user(self.username)
            self.server.pass_(self.password)
            logger.success('用户 {} 登入成功！'.format(self.username))
        except Exception as e:
            logger.error('登入失败，密码错误，如果是QQ邮箱，检查16位授权码！详细报错：{}'.format(e))
            return
        # logger.info('POP3服务器状态测试：{}'.format(self.server.getwelcome().decode('utf-8')))
        # self.receive_mails()

    # def __del__(self):
    #     self.server.quit()

    def read_mail(self, index):
        """
        根据邮件索引，解析邮件详细信息，做了发件人判断
        :param index: 邮件索引
        :return: 邮件发件人，邮件主题，正文的url
        """
        resp, lines, octets = self.server.retr(index)  # 根据索引读取邮件
        msg_content = b'\r\n'.join(lines).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        # print(msg)
        msg_from_raw = msg.get('From')  # 获取邮件的发送者
        msg_from = re.findall('<(.*?)>', msg_from_raw)[0]  # 提取发件人邮箱
        # 此处也对发件人进行比较，主要为了方便对邮件信息的解析读取，否则对于其他邮件的读取，报类型错误
        # 此处未做容错判断
        if msg_from in self.allow_sender:
            msg_subject = decode_str(msg.get('Subject'))  # 获取邮件主题
            # print(msg_subject)
            content = msg.get_payload(0)
            # print(msg.get_charsets()[1])
            url_base64 = str(content).split('base64')[-1]
            # print(url_base64)
            url = decode_base64(url_base64, charset=msg.get_charsets()[1])
            if 'http' in url:
                return {'sender_mail': msg_from,
                        'subject': msg_subject,
                        'url': url,
                        }

    def delete_mail(self, index):
        # 调试使用
        resp, mails, octets = self.server.list()
        print(mails)
        a = self.server.dele(index)
        print(a)

    def receive_mails(self):
        """
        主函数，通过pop3登入邮件服务器，抽取符合条件邮件，返回url，并删除此邮件
        :return:[{'sender_mail': ['lingdussr@qq.com'], 'subject': '一日一技：换个姿势「模拟登录」', 'url': 'https://mp.weixin.qq.com/s/B27WKJNlIfrqQxUpCmnFww'}, None]
        """

        resp, mails, octets = self.server.list()
        logger.info('获取的mail索引列表：{}'.format(mails))
        for i in mails:
            i_list = i.decode('utf-8').split(' ')  # ['1', '1189']
            i_index = i_list[0]  # 索引
            logger.info('尝试读取索引号为：{} 的邮件'.format(i_index))
            i_read_mail = self.read_mail(i_index)  # 读取索引的邮件信息

            if i_read_mail:  # 因为读取邮件做了发件人判断，此处遍历会有空值
                sender = i_read_mail.get('sender_mail')  # 提取发件人地址
                if sender in self.allow_sender:  # 和设置的allow_sender比对，存在即删除邮件并返回信息
                    self.server.dele(i_index)
                    self.server.quit()
                    logger.info('已删除邮件索引号：{}, 主题为：{}'.format(i_index, i_read_mail.get('subject')))
                    return i_read_mail


if __name__ == '__main__':
    while True:
        b = ReceiveMail()
        c = b.receive_mails()
        # c = b.read_mail(2)
        print(c)
        time.sleep(10)

