import SER

class Serial:
    def __init__(self, config, debug):
        self.config = config
        self.debug = debug
        self.buffer = ''
        
    def init(self):
        a = SER.set_speed(self.config.get('SER_SP'), self.config.get('SER_OD'))
        if(a != 1):
            raise Exception, 'ERROR, Serial.init() failed'
        self.debug.send('Serial.init() passed OK')
        return
    
    def getBuffer(self, size):
        data = ''
        if(len(self.buffer) > size):
            data = self.buffer[0:size]
            self.buffer = self.buffer[size:]
        else:
            data = self.buffer
            self.buffer = ''
        return data
    
    def receive(self, size):
        data = ''
        while(1):
            rcv = SER.read()
            if(len(rcv) > 0):
                self.buffer = self.buffer + rcv
                if(len(self.buffer) > size):
                    break
            else:
                break
        if(len(self.buffer) > 0):
            data = self.getBuffer(size)
            self.debug.send('Data received from serial port: ' + str(len(data)) + ' bytes')
        return data
    
    def send(self, data):
        SER.send(data)
        self.debug.send('Sending data to serial port: ' + str(len(data)) + ' bytes')