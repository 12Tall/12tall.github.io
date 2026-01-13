window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],  // 行内数学分隔符  
        displayMath: [['$$', '$$'], ['\\[', '\\]']], // 显示数学分隔符  
        processEscapes: true,  // 启用转义处理  

        packages: {'[+]': ['ams']}
    },
    svg: {
        fontCache: 'global'
    },

    startup: {
        pageReady: () => {
            console.log('Running MathJax');
            return MathJax.startup.defaultPageReady();
        }
    },
};
// (function () {
//     var script = document.createElement('script');
//     script.src = 'https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg.js';
//     script.defer = true;
//     document.head.appendChild(script);
// })();