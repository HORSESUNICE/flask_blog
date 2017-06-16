# 项目介绍 :octocat:
[![](https://img.shields.io/badge/python-3.6-green.svg)](https://www.python.org/downloads/release/python-360/)
- 这是我用flask框架制作的个人博客的源码存储库。
- This repository contains the source code for a personal blog created by flask.
- 参考资料:Flask Web开发
- References: [Flask Web Development](https://github.com/miguelgrinberg/flasky)

## tag所完成的内容以及遇到的问题
- homepage:
  - **将bootstrap的example改写为Jinja模版,用到了bootstrap的navbar和footer,自己在css中增加了背景图片**
  - [ ] 问题1:设置背景图片后第一次访问网站图片响应比较慢,可能是图片较大的原因(2.2M)
  - 解决方案:暂时还没有处理

- form:
  - **在模版中增加了表单,并且将post请求利用url_for重定向,虽然用session记录了表单内容但没有实际使用**

  - 注意事项1:对于含有动态可变部分的路由,不要忘记将可变部分作为参数传给view,否则不能正确访问URL

- database:
  - **利用SQLAlchemy提供的ORM来构建访问朋友提供的公共账号,使用的数据库是mysql,利用session记录访问对象如果试图访问其他friend页面返回403,为shell命令增加数据库实例和模型的上下文,增加了数据库迁移的配置,添加自动更新数据库及写入内容的deploy函数**

  - 注意事项1:首先要在本地mysql中创建flask_blog的数据库,并且在app.config中修改自己相应的数据库管理员账号和密码
  - 注意事项2:relationship中增加lazy参数配置禁止自动查询
  - 注意事项3:维护数据库迁移前需要python blog.py db init创建迁移仓库,python blog.py db migrate -m "initial migration"创建初始迁移脚本
  - 注意事项4:deploy中用到的account记得要定义在deploy之前

  - [x] 问题1:UserWarning: SQLALCHEMY_DATABASE_URI not set.
  - 解决方案:config URI要在拓展SQLAlchemy之前
  - [x] 问题2:FSADeprecationWarning
  - 解决方案:增加一行配置app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  - [x] 问题3:Incorrect string value
  - 解决方案:更改数据库默认字符设置 alter database flask_blog CHARACTER SET utf8;
  - [ ] 问题4:session中试图存入数据库查询得到的Friend对象,使用时发现session不能正确存储这样的对象
  - 解决方案:暂未解决
  - [x] 问题5:db upgrade前先要在shell中create_all()
  - 解决方案:可能是命令输错了,正确创建迁移脚本后可以正确使用python blog.py deploy默认配置
  - [ ] 问题6:如果把迁移函数account放在另一个py文件中会导致shell命令失败
  - 解决方案:尚未解决,应该是再次commit重复数据导致的问题,直接添加相同数据会报错,需要从数据库查询出数据修改后再次commit才能成功,但对于不同类型数据的修改提交没有很好的一致的方案所以还没有解决

- email:
  - **增加发送邮件功能**

  - [x] 问题1:attribute refresh operation cannot proceed
  - 解决方案:可能是在当前线程重新加入程序上下文导致session失效,改为新线程发送邮件解决
  - [ ] 问题2:发送邮件时间过久(5s)
  - 解决方案:暂未解决,使用新线程比原来10s快一些但网页刷新仍然显示有明显延迟

- structure:
  - **重新组织程序结构**

  - [x] 问题1:No module named 'email.Utils'; 'email' is not a package
  - 解决方案:个人的py文件最好不要和python module相同
  - [ ] 问题2:对于import的使用规则不太理解,app.__init__直接from config import config而不是from ..config
  - 解决方案:暂未解决
  - [x] 问题3:'function' object has no attribute 'route'
  - 解决方案:蓝本使用别名,不要与蓝本中的视图函数重名
  - [x] 问题4:werkzeug.routing.BuildError: Could not build url for endpoint 'friends'
  - 解决方案:base模版中的url_for也要做相应修改
