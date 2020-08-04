# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class pyAmizone:
    def __get_tokens(self, session):
        '''
        Obtains vertification tokens from
        webpage and cookies respectively
        Returns dict {rvt, crvt}
        '''
        index_url = 'https://student.amizone.net'  # HomePage URL
        index_response = session.get(index_url)
        soup = BeautifulSoup(index_response.text, 'html.parser')
        rvt = soup.find('form', id='loginform').find('input').get('value')
        crvt = session.cookies.get('__RequestVerificationToken')
        return {'rvt': rvt, 'crvt': crvt}

    def __get_request_headers(self):
        '''
        Returns basic header properties required
        to make requests
        Returns dict
        '''
        headers = {'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.9',
                   'Connection': 'keep-alive',
                   'DNT': '1',
                   'Host': 'student.amizone.net',
                   'Referer': 'https://student.amizone.net/Home',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/84.0.4147.105 Safari/537.36',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'X-Requested-With': 'XMLHttpRequest'}
        return headers

    def __validate_date(self, date):
        date_format = '%Y-%m-%d'
        try:
            datetime.strptime(date, date_format)
            return True
        except:
            return False

    def __init__(self, username, password):
        '''
        Verifies username and password credentials
        Raises exception in case of invalid credentials
        '''
        session = requests.Session()
        self.tokens = self.__get_tokens(session)
        login_url = 'https://student.amizone.net/Login/Login'
        payload = {'__RequestVerificationToken': self.tokens.get('rvt'),
                   '_UserName': username,
                   '_Password': password}
        headers = {'Host': 'student.amizone.net',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/80.0.3987.100 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/webp,/;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Content-Length': '170',
                   'Origin': 'https://student.amizone.net',
                   'Connection': 'keep-alive',
                   'Referer': 'https://student.amizone.net/login/',
                   'Cookie': '__RequestVerificationToken=' +
                   self.tokens.get('crvt'),
                   'Upgrade-Insecure-Requests': '1'}

        login_resp = session.post(login_url, data=payload, headers=headers)

        if login_resp.url != 'https://student.amizone.net/Home':
            raise Exception('Invalid Credentials')

        aspxauth = session.cookies.get('.ASPXAUTH')
        asp_sessionid = session.cookies.get('ASP.NET_SessionId')
        rvt = session.cookies.get('__RequestVerificationToken')
        self.cookie_header = (f'__RequestVerificationToken={rvt}; '
                              f'ASP.NET_SessionId={asp_sessionid}; '
                              f'.ASPXAUTH={aspxauth}')
        
        home_soup = BeautifulSoup(login_resp.content, 'html.parser')
        info = home_soup.find('span', class_='user-info')
        print('Logged In!')
        print('Name:', info.contents[0].strip())
        print('Enrolment Number:', info.small.get_text())

    def get_courses(self, semester=None):
        headers = self.__get_request_headers()
        headers.update({'Cookie': self.cookie_header})

        if semester is None:
            url = 'https://student.amizone.net/Academics/MyCourses'
            payload = {'X-Requested-With': 'XMLHttpRequest'}
            page = requests.get(url, data=payload, headers=headers)
        else:
            url = 'https://student.amizone.net/Academics/MyCourses/CourseListSemWise'
            payload = {'sem': semester}
            page = requests.post(url, data=payload, headers=headers)

        courses_soup = BeautifulSoup(page.text, 'html.parser')
        courses_table = courses_soup.find('table')

        courses = list()
        for row in courses_table.findAll('tr')[1:]:
            courses.append({'Course Code': row.find(attrs={'data-title': 'Course Code'}).text,
                            'Course Name': row.find(attrs={'data-title': 'Course Name'}).text,
                            'Course Type': row.find(attrs={'data-title': 'Type'}).text,
                            'Attendance': row.find(attrs={'data-title': 'Attendance'}).text.strip()
                            })
        return courses

    def get_schedule_today(self):
        headers = self.__get_request_headers()
        headers.update({'Cookie': self.cookie_header})

        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        payload = {'start': date,
                   'end': date}

        day = requests.get('https://student.amizone.net/Calendar/home/GetDiaryEvents', 
                           data=payload, headers=headers)
        response = day.json()
        
        keys_remove = ['id','color','sType','className','AttndColor','allDay']
        [entry.pop(key) for key in keys_remove for entry in response]
        
        return response
    
    def get_schedule(self, start, end):
        if self.__validate_date(start) is False:
            raise Exception('Start Date Invalid Format')
        if self.__validate_date(end) is False:
            raise Exception('End Date Invalid Format')
        
        headers = self.__get_request_headers()
        headers.update({'Cookie': self.cookie_header})
        payload = {'start': start,
                   'end': end}

        schedule = requests.get('https://student.amizone.net/Calendar/home/GetDiaryEvents',
                                data=payload, headers=headers)
        response = schedule.json()

        keys_remove = ['id','color','sType','className','AttndColor','allDay']
        [entry.pop(key) for key in keys_remove for entry in response]
        
        return response

    def get_faculty_list(self):
        headers = self.__get_request_headers()
        headers.update({'Cookie': self.cookie_header})

        faculty_url = 'https://student.amizone.net/FacultyFeeback/FacultyFeedback'
        payload = {'X-Requested-With': 'XMLHttpRequest'}
        response = requests.get(faculty_url, params=payload, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        faculty_list = soup.find('ul', attrs={'class': 'timeline'})
        
        faculties = list()
        for faculty in faculty_list.findAll('li'):
            subject = faculty.find('div', attrs={'class': 'subject'})
            if subject is not None:
                temp = dict()
                temp['Subject'] = subject.text.strip()
                faculty_picture = faculty.find('img')
                temp['Picture'] = faculty_picture.get('src')
                faculty_name = faculty.find('h4', 
                                            attrs={'class': 'faculty-name'})
                temp['Name'] = faculty_name.text
                faculties.append(temp)
        
        return faculties
        
    def get_attendance(self):
        headers = self.__get_request_headers()
        headers.update({'Cookie': self.cookie_header})
        
        home_url = 'https://student.amizone.net/Home/_Home'
        payload = {'X-Requested-With': 'XMLHttpRequest'}
        response = requests.get(home_url, params=payload, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        att_list = soup.find('ul', attrs={'id': 'tasks'})
        attendance = list()
        for item in att_list.findAll('li', 
                                     attrs={'class': 'item-green clearfix'}):
            att = dict()
            course_code = item.find('span', attrs={'class': 'sub-code'})
            att['Course Code'] = course_code.get_text().strip()
            course_name = item.find('span', attrs={'class': 'lbl'})
            att['Course Name'] = course_name.get_text().split('\t')[1]
            count = item.find('div', attrs={'class': 'pull-right class-count'})
            att['Class Count'] = count.text.strip()
            percent = item.find('span', attrs={'class': 'percent'})
            att['Percentage'] = percent.text.strip()
            attendance.append(att)
        
        return attendance
