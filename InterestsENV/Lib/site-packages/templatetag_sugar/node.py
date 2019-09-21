from django.template import Node


class SugarNode(Node):
    def __init__(self, pieces, bits, function):
        self.pieces = pieces
        self.function = function
        self.bits = bits
    
    def render(self, context):
        args = self.bits 
        kwargs = {}
        for key in self.pieces.keys():
            kwargs[key] = self.pieces[key] 

        return self.function(context, *args, **kwargs)
