import sys

from django.conf import settings

settings.configure(
    DEBUG=True,
    SECRET_KEY='thisisthesecretkey',  # of course, should not be used in production environment
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleWare',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
)

from django.http import HttpResponse


# A view:
# In a real django project we would put this in a views.py file inside one of our apps
def index(request):
    return HttpResponse('Hello World')


from django.conf.urls import url

# Django maps matching urls to views:
# In a real django project we would put this in a urls.py file inside one of our apps
urlpatterns = (
    url(r'^$', index),  # the root
)

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
