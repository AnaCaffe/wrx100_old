class Config:
    def __init__(self):
        self.config = {}
        
    def get(self, k):
        return self.config[k]
    
    def set(self, k, v):
        self.config[k] = v
        
    def read(self):
        try:
            fh = open("settings.ini", "r")
            try:
                lines = fh.readlines()
                for l in lines:
                    kv = l.strip().split('::')
                    self.config[kv[0]] = kv[1]
            finally:
                fh.close()
        except IOError:
            print "Configuration file not found."

    def write(self):
        try:
            fh = open("settings.ini", "w")
            try:
                lines = []
                for k in self.config.keys():
                    lines.append(k + '::' + self.config[k] + '\n')
                fh.writelines(lines)
            finally:
                fh.close()
        except IOError:
            print "Configuration file not found."
        
    def dump(self):
        for k in self.config.keys():
            print k + "::" + self.config[k]
        