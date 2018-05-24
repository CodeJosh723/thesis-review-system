from django.shortcuts import redirect


def is_student(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_teacher:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_teacher(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_teacher:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
