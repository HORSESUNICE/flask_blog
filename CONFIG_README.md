- 阿里云centos7部署
  - 在云服务器上安装python3.6和mysql5.7 参考链接:http://blog.csdn.net/hobohero/article/details/54381475 https://dev.mysql.com/doc/refman/5.7/en/binary-installation.html
  - https://github.com/HORSESUNICE/flask_blog fork后clone
  - virtualenv venv
  - source venv/bin/activate
  - pip install -r requirements.txt

  1.uwsgi
  - pip install uwsgi
  - uwsgi config.ini
    [uwsgi]

    # uwsgi 启动时所使用的地址与端口
    socket = 127.0.0.1:8001

    # 指向网站目录
    chdir = /home/xxx/flask_blog

    # python 启动程序文件
    wsgi-file = manage.py

    # python 程序内用以启动的 application 变量名
    callable = app

    # 处理器数
    processes = 4

    # 线程数
    threads = 2

    #状态检测地址
    stats = 127.0.0.1:9191

  2.ngnix
  - yum install nginx
  - cd /etc/nginx/conf.d
  - vim default.conf
  server {
          listen  80;
          server_name www.xxx.com;

          location / {
                include      uwsgi_params;
                uwsgi_pass   127.0.0.1:8001;
                uwsgi_param UWSGI_PYHOME /home/xxx/flask_blog/venv;
                uwsgi_param UWSGI_CHDIR  /home/xxx/flask_blog;
                uwsgi_param UWSGI_SCRIPT manage:app;
          }
        }

  3.Supervisor
  - yum install supervisor
  - cd /etc/supervisord.d/
  - vim flask_blog.conf
  [program:flask_blog]
  command=/home/mayangbin/flask_blog/venv/bin/uwsgi /home/mayangbin/flask_blog/config.ini

  directory=/home/mayangbin/flask_blog
  user=root

  autostart=true
  autorestart=true

  stdout_logfile=/home/mayangbin/flask_blog/logs/uwsgi_supervisor.log

  4.启动网站
  supervisord -c /etc/supervisord.conf
  sudo service nginx restart