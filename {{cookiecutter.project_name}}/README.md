## 部署

### 创建 Python 虚拟环境

    $ pyenv virtualenv 3.6.5 {{cookiecutter.project_name}}
    $ pyenv activate {{cookiecutter.project_name}}

### 安装项目依赖包

    $ make pip

### 启动服务

    $ make run-dev

## 统计报表

本项目只用了两个数据库，这两个数据库都可以通过 `web link` 以 `csv`
文件下载到本地。

- 下载 `user`
  + `http://xxx/api/dump/user?openid=<your-openid>`

注：

- 上面 `link` 中的 `openid` 是公众号为自己分配的
- 只有将 `openid` 加入项目配置后才有权限下载，不必担心其他人下载你的数据
