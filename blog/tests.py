from urllib import response
from django.test import TestCase,Client
from bs4 import BeautifulSoup
from .models import Post
# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client=Client()  # 가상의 클라이언트 생성

    def navbar_test(self, soup):
        navbar=soup.nav
        #self.assertIn('blog', navbar.text)
        self.assertIn('Django', navbar.text)

        logo_btn=navbar.find('a', text='Django')
        self.assertEqual(logo_btn.attrs['href'],'/')

        home_btn=navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'],'/')

        blog_btn=navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'],'/blog/')

        about_me_btn=navbar.find('a', text='about_me')
        self.assertEqual(about_me_btn.attrs['href'],'/about_me/')



    def test_post_list(self):
        #1.1 클라이언트가 포스트 목록 페이지를 실행한 정보를 가져온다.
        response=self.client.get('/blog/')
        #1.2 정상적으로 페이지가 로드되는지 확인, 찾지 못하면 404 반환
        self.assertEqual(response.status_code, 200)
        #1.3 페이지 타이틀 확인
        soup=BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text,'Blog')

        self.navbar_test(soup)

        #2.1 포스트 게시물이 0개인지 확인
        self.assertEqual(Post.objects.count(),0)
        #2.2 메인 존에 "게시물이 없습니다' 라는 문구가 있는지 확인
        main_area=soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)
        #3.1 포스트 게시물이 데이터 베이스에 있는 환경을 위해 포스트 2개 생성 및 확인
        post_001=Post.objects.create(
            title='첫 번째 포스트',
            content='first post',
        )
        post_002=Post.objects.create(
            title='두 번째 포스트',
            content='second post',
        )
        #3.2 페이지 새로고침을 위한 1.1~1.3 반복
        response=self.client.get('/blog/')
        soup=BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        #3.3 포스트 게시물 2개가 메인 존에 정상적으로 있는지 확인
        main_area=soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        #3.4 메인 존에 "게시물이 없습니다' 라는 문구가 없는지 확인
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        #1.1 비어있는 데이터베이스에 포스트 생성
        post_001=Post.objects.create(
            title='첫 번째 포스트',
            content='first post',
        )
        #1.2 생성된 포스트가 정상적인 url에 배정되는지 확인
        self.assertEqual(post_001.get_absolute_url(), '/blog/1') #?
        #2.1 포스트의 상세페이지에 접근
        #response=self.client.get(post_001.get_absolute_url())
        response=self.client.get(post_001.get_absolute_url()+'/') #?
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)

        #2.3 해당 포스트의 제목이 웹 브라우저 탭 타이틀에 있는지 확인
        self.assertIn(post_001.title, soup.title.text)
        #2.4 포스트 제목이 포트트 영역에 있는지 확인
        main_area=soup.find('div', id='main-area')
        post_area=main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        #2.5 포스트 작성자가 포스트를 볼 수 있는지 확인
        #작성불가
        #2.6 포스트 내용이 포스트 영역에 있는지 확인
        self.assertIn(post_001.content, post_area.text)

        