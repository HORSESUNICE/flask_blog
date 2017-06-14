# 项目介绍
这是我用flask框架制作的个人博客的源码存储库。
This repository contains the source code for a personal blog created by flask.
参考资料:Flask Web开发
References: [Flask Web Development](https://github.com/miguelgrinberg/flasky)

## tag所完成的内容以及遇到的问题
*   homepage:
    > 将bootstrap的example改写为Jinja模版,用到了bootstrap的navbar和footer,自己在css中增加了背景图片.
    > 设置背景图片后第一次访问网站图片响应比较慢,可能是图片较大的原因(2.2M)

*   form:
    > 在模版中增加了表单,并且将post请求利用url_for重定向,虽然用session记录了表单内容但没有实际使用
    > 注意对于含有动态可变部分的路由,不要忘记将可变部分作为参数传给view,否则不能正确访问URL
