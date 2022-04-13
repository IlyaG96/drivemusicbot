def fun():
    print("this is fun")
    def _fun():
        print("this is _fun")
    return _fun



fun()()
