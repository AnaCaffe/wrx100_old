import MOD
import SER

class Debug:
    def __init__(self, config):
        self.config = config
        self.tcpLogBuffer = ''
    
    def send(self, msg):
        message = str(MOD.secCounter()) + ' # ' + msg + '\r\n'
        max_len = int(self.config.get('TCP_MAX_LENGTH'))
        print message
        if (self.config.get('DEBUG_SER') == '1'):
            SER.send(message)
        if (self.config.get('DEBUG_TCP') == '1'):
            if((len(self.tcpLogBuffer) + len(message)) < max_len):
                self.tcpLogBuffer = self.tcpLogBuffer + message
                
    def getTcpBuffer(self):
        buffer = self.tcpLogBuffer
        self.tcpLogBuffer = ''
        return buffer