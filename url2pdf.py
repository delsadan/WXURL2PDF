# --coding=utf-8
"""
Time：2020-03-25
Author：imbiubiubiu
desc：根据微信文章url，转化为pdf
微信文章保存为pdf不能加入图片，参考：https://github.com/LeLe86/vWeChatCrawl
"""

import pdfkit
import time
import os
import requests
from loguru import logger
from bs4 import BeautifulSoup
from configparser import ConfigParser

# 日志文件配置
if not os.path.exists('log'):
    os.mkdir('log')
logger.add('./log/url2pdf.log', rotation='10 MB', enqueue=True, )

# 创建pdf导出文件夹
if not os.path.exists('PDF_output'):
    os.mkdir('PDF_output')


def change_css_src(bs):
    """
    将网页源代码里link标签下，href中以//开头的前面加http:
    :param bs: soup解析后的文件
    """
    linkList = bs.findAll("link")
    for link in linkList:
        href = link.attrs["href"]
        if href.startswith("//"):
            newhref = "http:" + href
            link.attrs["href"] = newhref


def change_img_src(bs):
    """
    将网页源代码里img标签下，src中以//开头的前面加http:
    :param bs: soup解析后的文件
    """
    img_list = bs.findAll('img')
    for img in img_list:
        if 'src' in str(img):
            src = img.attrs['src']
            if src.startswith('//'):
                new_src = 'http:' + src
                img.attrs["src"] = new_src


def change_content(bs):
    jscontent = bs.find(id="js_content")
    if jscontent:
        jscontent.attrs["style"] = ""
    else:
        print("-----可能文章被删了-----")


class Html2PDF:

    def __init__(self):
        cfg = ConfigParser()
        cfg.read('./config/config.ini')

        # 读取wkhtmltopdf的路径，主要用于Windows
        self.path_wk = cfg['url2pdf']['wkhtmltopdf_path']
        self.config = pdfkit.configuration(wkhtmltopdf=self.path_wk)
        logger.info('当前设置的wkhtmltopdf路径为：{}'.format(self.path_wk))

    def html_to_pdf(self, url1, output_name=time.strftime('%Y%m%d_%H%M%S')):
        """
        对微信文章的网页代码进行处理后，交由pdfkit转成pdf
        :return: 保存成功为True
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/70.0.3538.110 Safari/537.36'}
        try:
            r = requests.get(url1, headers=headers)
            r = r.text.replace('data-src', 'src')  # 将html里面涉及图片链接的data-src暴力替换成src
            # soup = BeautifulSoup(r, 'lxml')
            soup = BeautifulSoup(r, 'html.parser')
            change_css_src(soup)
            change_img_src(soup)
            change_content(soup)
            logger.success('微信文章html处理完成!')
        except Exception as e:
            logger.error('微信文章html处理失败！原因：{}'.format(e))
            return False

        options = {
            # 'page-size': 'Letter',
            # 'margin-top': '0.75in',
            # 'margin-right': '0.75in',
            # 'margin-bottom': '0.75in',
            # 'margin-left': '0.75in',
            # 'encoding': "UTF-8",
            'disable-javascript': None,  # 禁用js，否则，一直卡着，没法保存pdf
            'load-error-handling': 'skip'}
        output_path = './PDF_output/{}.pdf'.format(output_name)
        try:
            if pdfkit.from_string(str(soup), output_path, options=options, configuration=self.config, ):
                logger.success('{} 文章已成功转成PDF！'.format(output_name))
                return True
        except Exception as e:
            logger.error('{} 转成PDF失败，原因：{}'.format(output_name, e))
            return False


if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s/3BNun_QfD9vB6YTgWLasBg'
    a = Html2PDF()
    a.html_to_pdf(url, )
