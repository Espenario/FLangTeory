class ref:
    def __init__(self, obj):
        self.obj = obj
    def get(self):
        return self.obj
    def set(self, obj): 
        self.obj = obj

a = ref('2')
c = ref('3')
b = [a,c]
d = ref(b[0].get() + b[1].get())
print(d.get())
c.set('5')
print(d.get())