# pylint: disable=unused-argument
from {{cookiecutter.app_name}}.app import WeRoBot


robot = WeRoBot()


@robot.subscribe
@robot.identity
# pylint: disable=unused-argument
def subscribe_handler(msg):
    return '欢迎订阅该公众号😁'


@robot.unsubscribe
# pylint: disable=unused-argument
def unsubscribe_handler(msg):
    msg = '好遗憾😢，希望您还能回来 ...'
    return msg


@robot.filter('帮助')
# pylint: disable=unused-argument
def show_help(msg):
    return """
    帮助
    xxxxx
    yyyyy
    """


@robot.text
@robot.identity
# pylint: disable=unused-argument
def text_handler(msg, session):
    target = msg.target  # 开发者账号 OpenID
    source = msg.source  # 发送者账号 OpenID
    return f'{msg.content}, source: {source}, target: {target}'


@robot.image
# pylint: disable=unused-argument
def image_handler(msg):
    return msg.img


@robot.handler
# pylint: disable=unused-argument
def hello(msg):
    return f'Hello {msg}'


@robot.error_page
# pylint: disable=unused-argument
def make_error_page(url):
    return '<h1>喵喵喵 %s 不是给麻瓜访问的快走开</h1>' % url
