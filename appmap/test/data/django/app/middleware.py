def hello_world(get_response):
    def _hello_world(request):
        print("Hello world!")
        return get_response(request)

    return _hello_world
