DownThesisFromSEG
====
1、功能
------
使用DownloadThesisFromSeg(searchItem,usr,psd)函数，将[SEG](http://library.seg.org)搜索到的pdf文献批量下载下来，文件名按照“【年份】标题”的形式。

2、用法
-------
DownloadThesisFromSeg(searchItem,usr,psd)<br>
输入参数:<br>

* searchItem: 你要搜索的关键字
* usr:SEG的用户名

* psd:SEG的密码

3、更新
------
2016-05-01  添加formatFileName(filename)函数，修复因为标题中含有不合法字符而新建文件失败的问题。
2016-05-01  在代码中重新设置系统默认编码，修复运行时按照ASCII码解析字符导致报错的问题