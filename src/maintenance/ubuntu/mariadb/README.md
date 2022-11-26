---
title: MariaDB 运维   
date: 2022-11-26
timeLine: true
sidebar: false  
icon: linux
category:  
    - 笔记  
    - 运维      
tag:   
    - linux  
    - 数据库    
    - MariaDB  
---     

## 安装与登录    
```shell-session  
$ sudo apt install mariadb-server mariadb-common mariadb-client mariadb-backup  
mariadb-common 是所有MariaDB 所需的配置文件    
mariadb-backup 是备份与恢复的工具  

$ sudo systemctl enable mariadb
$ sudo systemctl start mariadb

$ sudo mysql  # 匿名登陆，但是这样不够安全  
MariaDB [(none)]> quit
Bye
```    
## 数据管理
数据管理首先要登录sql 命令窗口：  
```sql
MariaDB [(none)]> create database test;  -- 创建数据库  
Query OK, 1 row affected (0,000 sec)

MariaDB [(none)]> show databases;  -- 列举数据库  
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| test               |
+--------------------+
5 rows in set (0,000 sec)

MariaDB [(none)]> use mysql;  -- 切换到目的数据库
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed  
MariaDB [mysql]> show tables; -- 列举当前数据空中的数据表  
```

## 用户管理  
用户管理首先要登录sql 命令窗口：    
```sql{21-22,35-36}  
-- 创建用户
MariaDB [mysql]> create user 'test'@'192.168.%' identified by 'Passw0rd';
Query OK, 0 rows affected (0,001 sec)

MariaDB [mysql]> select host,user from user;  # 列举所有用户  
+-----------+-------------+
| Host      | User        |
+-----------+-------------+
| 192.168.% | test        |
| localhost | mariadb.sys |
| localhost | mysql       |
| localhost | root        |
+-----------+-------------+
4 rows in set (0,000 sec)

MariaDB [mysql]> update user set host='%' where user='test';  -- 从MySQL 14 开始，需要使用AlterUser 或者SetPassword 管理用户了
-- ERROR 1356 (HY000): View 'mysql.user' references invalid table(s) or column(s) or function(s) or definer/invoker of view lack rights to use them
MariaDB [mysql]> rename user 'test'@'192.168.%' to 'test'@'%';  -- 可以使用rename 来修改
Query OK, 0 rows affected (0,001 sec)

MariaDB [(none)]> set password for root@localhost=password('Passw0rd');  -- 修改用户密码，以root 为例  
Query OK, 0 rows affected (0,000 sec)


-- 给用户赋予访问某个数据表的权利，可以使用* 通配符  
-- grant select, insert on data_base.data_table to 'test'@'192.168.%';
MariaDB [(none)]> grant all privileges on test.* to 'test'@'%';
Query OK, 0 rows affected (0,000 sec)


-- 赋权后需刷新生效
MariaDB [mysql]> flush privileges;
-- Query OK, 0 rows affected (0,000 sec)

$ mysql -u test -p  -- 采用新用户登录  
Enter password: 

MariaDB [(none)]> show databases;  -- test 用户只能看到有限的数据库
+--------------------+
| Database           |
+--------------------+
| information_schema |
| test               |
+--------------------+
2 rows in set (0,000 sec)
```

至于数据的增删改查操作请参考[菜鸟教程](https://www.runoob.com/mysql/mysql-tutorial.html)  


## 备份与恢复   
```shell-session  
$ mysqldump -uroot -pPassw0rd --all-databases > all.bak  # 将所有数据库内容备份成一堆sql 语句  
$ mysql -uroot -p --one-database test < all.bak  # 从所有备份中恢复某个数据表  
```


## 参考  
1. [Linux运维笔记----Mariadb数据库基本管理](https://blog.csdn.net/men_wen/article/details/52506563)  
2. [Linux运维笔记----Mariadb数据库基本管理](https://blog.cuiran.cc/522.html)  
3. [Full Backup and Restore with Mariabackup](https://mariadb.com/kb/en/full-backup-and-restore-with-mariabackup/)

-----  
2022-11-26 Aachen  