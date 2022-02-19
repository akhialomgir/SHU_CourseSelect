import re
import logging
from time import sleep
from bs4 import BeautifulSoup


class Worker():
    def __init__(self, config) -> None:
        import requests

        logging.basicConfig(filename=config.split('.')[0]+'.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S')

        self.active = True
        self.courseNum = -1
        self.sess = requests.session()
        self.config = config
        self.__inputConfig()
        self.__run()

    def __json2dict(self, file) -> dict:
        import json
        with open(file) as f:
            return json.load(f)

    def __inputConfig(self) -> None:
        self.master = self.__json2dict(self.config)['master']
        self.term = self.__json2dict(self.config)['term']
        self.params = self.__json2dict(self.config)['params']
        self.param = {'username': '', 'password': '', }
        self.servant = self.__json2dict(self.config)['servant']
        self.query = self.__json2dict(self.config)['query']
        if self.servant['username'] != '':
            print('Enquiry account exists')
            logging.info('Enquiry account exists')
        else:
            print('Enquiry account does not exist, use course selection account')
            logging.info(
                'Enquiry account does not exist, use course selection account')
            self.servant = self.master

        self.status = {}
        for i in range(0, len(self.params['cids'])):
            self.status[self.params['cids'][i]+'_'+self.params['tnos'][i]] = ''

    def __getCookie(self, account) -> None:
        login = self.sess.post('https://oauth.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2MzU4NDcxMTAxOTc4NDk1ODYsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0=',
                               data=account)
        if login.status_code == 200:
            print(account['username'] + ' login successfully')
            logging.info(account['username'] + ' login successfully')
        selectTerm = self.sess.post('http://xk.autoisp.shu.edu.cn/Home/TermSelect',
                                    data=self.term)
        if selectTerm.status_code == 200:
            print('Term ' + self.term['termId'] + ' is selected successfully')
            logging.info(
                'Term ' + self.term['termId'] + ' is selected successfully')

    def __iter(self) -> bool:
        length = len(self.params['cids'])
        if length == 0:
            self.active = False
            return False
        else:
            self.courseNum = (self.courseNum+1) % length

        self.param['cids'] = self.params['cids'][self.courseNum]
        self.param['tnos'] = self.params['tnos'][self.courseNum]
        self.query['CID'] = self.param['cids']
        self.query['TeachNo'] = self.param['tnos']
        return True

    def __search(self) -> list:  # TODO to be more stable
        search = self.sess.post(
            'http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/QueryCourseCheck',
            data=self.query)
        soup = BeautifulSoup(search.text, 'lxml')
        table = soup.find(id='tblcoursecheck').text
        table = re.sub('\n', ' ', table).split()
        print(''.join(str(i)+' ' for i in table[13:]))
        return table

    def __select(self) -> None:
        self.__getCookie(self.master)
        self.sess.post('http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/CourseSelectionSave',
                       data=self.param)

        self.__check()

    def __check(self) -> None:
        courseTable = self.sess.get(
            'http://xk.autoisp.shu.edu.cn/StudentQuery/QueryCourseTable')
        soup = BeautifulSoup(courseTable.text, 'lxml')
        table = soup.find('table', attrs={'class': 'tblnoborder'}).text
        table = re.sub('\x20', '_', table)
        table = re.sub('\n_*', '\x20', table).split()[12:-1]
        for item in table:
            if re.match('[A-Z0-9]{8}', item):
                for cid, tno in zip(self.params['cids'], self.params['tnos']):
                    if item == cid:
                        self.params['cids'].remove(cid)
                        self.params['tnos'].remove(tno)
                        print('<'+cid+'_'+tno+'>', 'selected')
                        self.status[cid+'_'+tno] = 'selected'
                        logging.info('<'+cid+'_'+tno + '>' + ' ' +
                                     self.status[cid+'_'+tno])

    def __run(self) -> None:
        while (self.active == True):
            try:
                if self.courseNum == -1:
                    self.__getCookie(self.master)
                    self.__check()
                    self.__getCookie(self.servant)
                if not self.__iter():
                    break
                table = self.__search()
                if table[-2] == '人数已满':
                    print('Capacity:', table[-5], 'Current:', table[-4])
                else:
                    print('Capacity:', table[-4], 'Current:', table[-3])
                    self.__select()

                print(self.status)
                sleep(1)
            except Exception as Error:
                print(Error)


if __name__ == '__main__':
    cs = Worker('config.json')
