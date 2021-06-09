#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


import os
import sys
import django
from channels.routing import get_default_application

# 让 asgi 能够查找的应用所在的目录路径
app_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(os.path.join(app_path, "zanhu"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()
application = get_default_application()
