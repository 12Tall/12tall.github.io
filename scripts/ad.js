hexo.extend.filter.register('theme_inject', function(injects) {
  //名字路径等都可以随意修改，为了方便下文都以这里的定义为主
  injects.bodyEnd.raw('google-ad-js', '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9670282672953561" crossorigin="anonymous"></script>', {}, {cache: true});
});