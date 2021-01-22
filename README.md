# sql-tools

#### windows 下面编译流程

​	检查本地pip版本  `pip -V` 

​	升级pip版本到最新 `python -m pip install --upgrade pip` 

​	安装python编译工具 PyInstaller	`pip install PyInstaller`

​	在资源管理器下面点击项目代码中 build_sql_update-3.6.bat 文件开始编译,或者在命令行模式下输入` pyinstaller -F -n=sql_update sql_update_3_6.py`手动编译

​	项目生成目录dist ,文件夹中生成sql_update.bat,sql_update.exe

#### windows 下使用

​	资源管理器中编辑sql_update.bat文件,配置相关数据库信息后,点击使用

#### linux 编译流程

​	检查本地pip版本  `pip -V` 

​	升级pip版本到最新 `pip install --upgrade setuptools && python3 -m pip install --upgrade pip` 

​	安装 mysqlclient  解决找不到 MySQLdb模块报错的问题 `pip install mysqlclient`

​	如果安装时提示`OSError: mysql_config not found`错误,安装 mysql-devel `sudo yum install python3-devel mysql-devel`  ,安装完毕重新安装mysqlclient

​	安装 PyInstaller	`pip install PyInstaller`

​	在项目目录下面执行命令开始编译: `pyinstaller -F sql_update_3_6.py `

​	项目生成dist文件夹,生成sql_update_3_6可执行文件

#### linux环境下使用

​	在dist 目录下执行 ` ./sql_update_3_6 --sql_dir=./sql_release --host= --user= --passwd= --dbname= --port= --charset=`

​	相关参数后根据本地数据库参数填写

​	或者使用该目录下脚本 ,编译脚本内的相关配置为本地数据库配置后,在dist目录中输入 `./sql_update_3_6.sh`







​	

