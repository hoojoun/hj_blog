from email.mime import audio
from unicodedata import category
from urllib import response
from django.test import TestCase,Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment
# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client=Client()  # 가상의 클라이언트 생성
        self.user_trump=User.objects.create_user(username='trump', password='somepassword')
        self.user_obama=User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff=True
        self.user_obama.save()
        self.category_programming=Category.objects.create(name='programming', slug='programming')
        self.category_music=Category.objects.create(name='music', slug='music')

        self.tag_python_kor=Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python=Tag.objects.create(name='python', slug='python')

        self.post_001=Post.objects.create(
            title='첫 번째 포스트',
            content='first post',
            category=self.category_programming,
            author=self.user_trump,
        )
        self.post_001.tags.add(self.tag_python)
        self.post_002=Post.objects.create(
            title='두 번째 포스트',
            content='second post',
            category=self.category_music,
            author=self.user_obama,
        )
        self.post_002.tags.add(self.tag_python)
        self.post_003=Post.objects.create(
            title='세 번째 포스트',
            content='third post',
            author=self.user_obama,
        )
        self.post_003.tags.add(self.tag_python_kor)

        self.comment_001=Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='first comment',
        )


    def category_card_test(self, soup):
        categories_card=soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

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
        # 3개의 포스트가 전부 있는 경우
        self.assertEqual(Post.objects.count(), 3)
        #1.1 클라이언트가 포스트 목록 페이지를 실행한 정보를 가져온다.
        response=self.client.get('/blog/')
        #1.2 정상적으로 페이지가 로드되는지 확인, 찾지 못하면 404 반환
        self.assertEqual(response.status_code, 200)
        #1.3 페이지 타이틀 확인
        soup=BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        #2.1 포스트 게시물이 0개인지 확인
        #self.assertEqual(Post.objects.count(),0)
        #2.2 메인 존에 "게시물이 없습니다' 라는 문구가 있는지 확인
        main_area=soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        #3.1 포스트 게시물이 데이터 베이스에 있는 환경을 위해 포스트 2개 생성 및 확인
        post_001_card=main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_python.name,post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name,post_001_card.text)

        post_002_card=main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.tag_python.name,post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name,post_002_card.text)

        post_003_card=main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_python.name,post_003_card.text)
        self.assertIn(self.tag_python_kor.name,post_003_card.text)
  
        #3.3 포스트 게시물 2개가 메인 존에 정상적으로 있는지 확인
  
        #3.4 메인 존에 "게시물이 없습니다' 라는 문구가 없는지 확인
        #self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)
        
        # 포스트가 하나도 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response=self.client.get('/blog/')
        soup=BeautifulSoup(response.content, 'html.parser')
        main_area=soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        #1.1 비어있는 데이터베이스에 포스트 생성

        #1.2 생성된 포스트가 정상적인 url에 배정되는지 확인
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1') #?
        #2.1 포스트의 상세페이지에 접근
        #response=self.client.get(post_001.get_absolute_url())
        response=self.client.get(self.post_001.get_absolute_url()+'/') #?
        self.assertEqual(response.status_code, 200)
        soup=BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        #2.3 해당 포스트의 제목이 웹 브라우저 탭 타이틀에 있는지 확인
        self.assertIn(self.post_001.title, soup.title.text)
        #2.4 포스트 제목이 포트트 영역에 있는지 확인
        main_area=soup.find('div', id='main-area')
        post_area=main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        #2.5 포스트 작성자가 포스트를 볼 수 있는지 확인
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        #2.6 포스트 내용이 포스트 영역에 있는지 확인
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        #comment area
        comments_area=soup.find('div',id="comment-area")
        comment_001_area=comments_area.find('div',id="comment-1")
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_category_page(self):
        response=self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code,200)

        soup=BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)
    
        main_area=soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response=self.client.get(self.tag_python.get_absolute_url())
        self.assertEqual(response.status_code,200)

        soup=BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)

        self.assertIn(self.tag_python.name, soup.h1.text)
    
        main_area=soup.find('div', id='main-area')
        self.assertIn(self.tag_python.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 로그인을 안한 경우
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)

        #일반 사용자가 로그인을 한 경우
        self.client.login(username='trump',password='somepassword')
        response=self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code,200)

        #관리자가 로그인을 한 경우
        self.client.login(username='obama',password='somepassword')
        response=self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code,200)

        soup=BeautifulSoup(response.content, 'html.parser')
        
        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area=soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input=main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post('/blog/create_post/',
            {
                'title':'Post form 만들기',
                'content':"post form 페이지를 만들다. ",
                'tags_str':'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post=Post.objects.last()
        self.assertEqual(last_post.title, 'Post form 만들기')
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(),4)

    def test_update_post(self):
        update_post_url=f'/blog/update_post/{self.post_003.pk}/'

        #로그인을 하지 않는 경우
        response=self.client.get(update_post_url)
        self.assertNotEqual(response.status_code,200)

        #로그인을 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author,self.user_trump)
        self.client.login(username='trump',password='somepassword')
        response=self.client.get(update_post_url)
        self.assertEqual(response.status_code,403)

        # 작성자인 경우
        self.client.login(username=self.post_003.author,password='somepassword')
        response=self.client.get(update_post_url)
        self.assertEqual(response.status_code,200)
        soup=BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area=soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input=main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부', tag_str_input.attrs['value'])

        response=self.client.post(
            update_post_url,
            {
                'title':'세번째 포스트 수정',
                'content':"수정됨 ",
                'category':self.category_music.pk,
                'tags_str':'파이썬 공부; 한글 태그, some tag',
            },
            follow=True
        )

        soup=BeautifulSoup(response.content, 'html.parser')
        main_area=soup.find('div', id='main-area')
        self.assertIn('세번째 포스트 수정', main_area.text)
        self.assertIn('수정됨', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)


