

class Utils:

    @staticmethod
    def parselist(_list):
        _modules = _list.replace(" ","")
        _modules = _modules.replace("[","") 
        _modules = _modules.replace("]","")
        return _modules.split(",")



