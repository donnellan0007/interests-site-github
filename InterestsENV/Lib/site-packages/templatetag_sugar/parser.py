from django.db.models.loading import cache
from django.template import TemplateSyntaxError

from templatetag_sugar.node import SugarNode


class Parser(object):
    def __init__(self, syntax, function):
        self.syntax = syntax
        self.function = function
    
    def __call__(self, parser, token):
        bits = token.split_contents()
        # pop the name of the tag off
        tag_name = bits.pop(0)
        pieces = {}
        error = False

        for key in self.syntax.keys():
            
            if key.name in bits:
                # Get the value for the key , this should always be the next element
                value = bits.pop(bits.index(key.name) + 1 )
                bits.pop(bits.index(key.name))
                pieces[key.name] =  self.syntax[key].parse(value)
            else:
                #if the key is required (Required subclass) and not present throw an exception
                if isinstance(key , Required):
                    raise TemplateSyntaxError()


        return SugarNode(pieces, bits, self.function)

class NamedParsable(object):
    def __init__(self, name=None):
        self.name = name
    
class Required(NamedParsable):
    pass
    
class Optional(NamedParsable):
    pass

class Variable(NamedParsable):
    def parse(self, bit):
        return bit
    
class Model(NamedParsable):
    def parse(self, parser, bits):
        bit = bits.popleft()
        app, model = bit.split(".")
        return [(self, self.name, cache.get_model(app, model))]
