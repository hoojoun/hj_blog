# hj_blog
### 사이트 주소
https://www.entergramming.com/

### 기능
- 게시판 기능
- 각종 자료 및 Github 링크
- Youtube의 원하는 동영상 실행

### 실행
```bash
$ git clone https://github.com/hoojoun/hj_blog.git
$ cd hj_blog
$ sudo apt install docker.io
$ sudo systemctl start docker
$ sudo systemctl enable docker
$ sudo apt install docker-compose
$ sudo docker-compose up -d --build
$ sudo docker-compose exec web python manage.py makemigrations blog
$ sudo docker-compose exec web python manage.py migrate
```
### 추가할 기능
- 편의성 및 디자인 개선 (css 위주)
- 클라우드 기능 추가
- 모바일 화면 개선
