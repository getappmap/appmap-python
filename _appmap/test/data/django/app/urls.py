import django.http
from django.urls import include, path, re_path


def view(_request):
    return django.http.HttpResponse("testing")


def user_view(_request, username):
    return django.http.HttpResponse(f"user {username}")


def post_view(_request, post_id):
    return django.http.HttpResponse(f"post {post_id}")


def post_unnamed_view(_request, arg):
    return django.http.HttpResponse(f"post with unnamed, {arg}")


def user_post_view(_request, username, post_id):
    return django.http.HttpResponse(f"post {username} {post_id}")


def echo_view(request):
    return django.http.HttpResponse(request.body)


def exception_view(_request):
    raise RuntimeError("An error")


def user_included_view(_request, username):
    return django.http.HttpResponse(f"user {username}, included")


def acl_edit(_request, pk):
    return django.http.HttpResponse(f"acl_edit {pk}")


# replicate a problematic bit of misago's routing
admincp_patterns = [
    re_path(
        "^",
        include(
            [
                re_path(
                    r"^permissions/",
                    include(
                        (
                            [re_path(r"^edit/(?P<pk>\d+)$", acl_edit, name="edit")],
                            "permissions",
                        ),
                        namespace="permissions",
                    ),
                )
            ]
        ),
    )
]

urlpatterns = [
    path("test", view),
    path("", view),
    re_path("^user/(?P<username>[^/]+)$", user_view),
    path("post/<int:post_id>", post_view),
    path("post/<username>/<int:post_id>/summary", user_post_view),
    re_path(r"^post/unnamed/(\d+)$", post_unnamed_view),
    path("echo", echo_view),
    path("exception", exception_view),
    re_path(r"^post/included/", include([path("<username>", user_view)])),
    re_path(r"^admincp/", include((admincp_patterns, "admin"), namespace="admin")),
]
