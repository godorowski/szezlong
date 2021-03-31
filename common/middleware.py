import threading

GLOBAL_REQUEST = threading.local()


def global_request_middleware(get_response):
    """
    Keep request global
    """

    def process_request(request):
        GLOBAL_REQUEST.request = request
        response = get_response(request)
        return response

    return process_request


def get_request():
    try:
        return GLOBAL_REQUEST.request
    except AttributeError:
        return None

