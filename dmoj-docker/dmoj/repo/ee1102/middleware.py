import re

from django.http import Http404

# Pages that would let a student see other students' scores or rankings.
BLOCKED = re.compile(r'^/(users|api|stats|organizations?|ta)(/|$)|^/contest/[^/]+/stats')
OTHER_USER = re.compile(r'^/(?:user|submissions/user)/(?P<name>[^/]+)')


class RestrictStudentPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if not user.is_staff:
            path = request.path
            if BLOCKED.match(path):
                raise Http404()
            match = OTHER_USER.match(path)
            if match and (not user.is_authenticated or match.group('name') != user.username):
                raise Http404()
        return self.get_response(request)
