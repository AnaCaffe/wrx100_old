version = 'wrx100.0.5'

import MOD
import sys

import config
CONFIG = config.Config()
CONFIG.read()

import debug
DEBUG = debug.Debug(CONFIG)

import utils
UTILS = utils.Utils(CONFIG, DEBUG)

import serial
SERIAL = serial.Serial(CONFIG, DEBUG)

import gsm
GSM = gsm.GSM(CONFIG, DEBUG, SERIAL)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
C_SCFG1 = 'AT#SCFG=1,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',90,60,2\r'   # AT КОМАНДА НАСТРОЙКИ СОКЕТА №1,"2" - data sending timeout; after this period data are sent also if they’re less than max packet size.
C_SCFGEXT1 = 'AT#SCFGEXT=1,1,0,0,0,0\r'  # COKET1, SRING + DATA SIZE, receive in TEXT, keepalive off, autoreceive off, send in TEXT

C_SCFG2 = 'AT#SCFG=2,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',120,60,2\r'   # AT КОМАНДА НАСТРОЙКИ СОКЕТА №2 - Сокет для определения точного времени 15 сек на попытку подключенния
C_SCFGEXT2 = 'AT#SCFGEXT=2,1,0,0,0,0\r'  # COKET2, SRING + DATA SIZE+DATA, receive in TEXT, keepalive off, autoreceive off, send in TEXT

#C_SCFG3 = 'AT#SCFG=3,1,' + CONFIG.get('TCP_MAX_LENGTH') + ',250,100,2\r'  # AT КОМАНДА НАСТРОЙКИ СОКЕТА №3 - Сокет для ведения лога на удаленном TCP севрере
#C_SCFGEXT3 = 'AT#SCFGEXT=3,1,0,0,0,0\r'  # COKET2, SRING + DATA SIZE, receive in TEXT, keepalive off, autoreceive off, send in TEXT
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

AUTH_REQUEST = '\x02\xAA\xAA\x86\x81\xFF\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\xB0\xB0\xB0\x80\xB0\xB0\xB0\x88\x80\xFD\x88\x82\x9F\x8D\x80\xFE\xE2\x84\x99\x9D\x03'

def initWatchdog():
    MOD.watchdogEnable(int(CONFIG.get('WATCHDOG_PERIOD')))
    
def resetWatchdog():
    MOD.watchdogReset()
    
def ping(trys):
    servers = CONFIG.get('PING_IPS').split(',')
    for i in range(trys):
        for server in servers:
            DEBUG.send('Send ping to ' + server)
            res = GSM.ping(server)
            if(res == 0):
                return (0)
            resetWatchdog()
    return (-1)

try:
    REG_REPLY = UTILS.getServerReply(CONFIG.get('ID_SERVER'))               # РАСЧЕТ ОТВЕТА РЕГИСТРАЦИИ НА СЕРВЕРЕ НА ОСНОВЕ СВОЕГО ID_SERVER
    REG_LOG_REPLY = UTILS.getServerReply(CONFIG.get('ID_LOG_SERVER'))
    
    DEBUG.send(' SCRIPT STARTED. Version: ' + version + '\r\nCopyright 2012.' \
                'Teleofis Wireless Communications\r\n==============' \
                '==================================')

    initWatchdog()
    SERIAL.init()                       # ИНИЦИАЛИЗАЦИЯ ПОСЛЕДОВАТЕЛЬНОГО ПОРТА
    GSM.initModem()                     # НАСТРОЙКА ПАРАМЕТРОВ GSM МОДЕМА
    GSM.initStartMode()                 # НАСТРОЙКА РЕЖИМА ЗАПУСКА СКРИПТОВ
    GSM.initSim()                       # ПРОВЕРКА РАБОТОСПОСОБНОСТИ SIM КАРТЫ
    GSM.initCreg()                      # ПРОВЕРКА РЕГИСТРАЦИИ В СЕТИ
    GSM.initCsq()                       # ПОЛУЧЕНИЕ УРОВНЯ СИГНАЛА В АНТЕННЕ
    GSM.initSocket(C_SCFG1, C_SCFGEXT1) # ИНИЦИАЛИЗАЦИЯ Socket 1
    GSM.initSocket(C_SCFG2, C_SCFGEXT2) # ИНИЦИАЛИЗАЦИЯ Socket 2
    GSM.initContext()                   # НАСТРОЙКА ПАРАМЕТРОВ PDP КОНТЕКСТА
    
    #
    # Status flags
    #
    DATA_AUTH = 0
    LOG_AUTH = 0
    DATA_SOCKET = 0
    LOG_SOCKET = 0
    
    #
    # Timers
    #
    TCP_LOG_TIMER = 0

    while(1):
        # check context
        context = GSM.checkContext()
        if(context != '1'):
            DEBUG.send('Activation GPRS context')
            GSM.activateContext()
        
        # check socket 1
        socket = GSM.checkSocket('1')
        if(socket not in ['1', '2', '3']):   # Socket closed
            DEBUG.send('Trying to open a socket #1 (data)')
            DATA_SOCKET = 0
            DATA_AUTH = 0
            try:
                GSM.connect('1', CONFIG.get('DEST_IP'), CONFIG.get('DEST_PORT'), 3)
                DATA_SOCKET = 1
            except Exception, e:
                DEBUG.send(e)
                ping_trys = int(CONFIG.get('PING_TRYS'))
                res = ping(ping_trys)
                if(res < 0):
                    raise Exception, 'ERROR. Ping failed'
                continue
        
        # data channel authorization
        if((CONFIG.get('REG_SERVER') == '1') and (DATA_SOCKET == 1) and (DATA_AUTH == 0)):
            DEBUG.send('Start authorization on socket #1 (data)')
            data = ''
            try:
                data = GSM.receiveMDM()
            except Exception, e:
                DEBUG.send(e)
            if((len(data) > 0)): # and (data.find(AUTH_REQUEST) != -1)):
                GSM.sendMDM(REG_REPLY)
            else:
                DEBUG.send('Authorization failed')
                continue
            DATA_AUTH = 1
            DEBUG.send('Authorization complete')
        
        if(CONFIG.get('DEBUG_TCP') == '1'):
            socket = GSM.checkSocket('2')
            if(socket not in ['1', '2', '3']):   # Socket closed
                DEBUG.send('Trying to open a socket #2 (log)')
                LOG_SOCKET = 0
                LOG_AUTH = 0
                try:
                    GSM.connect('2', CONFIG.get('LOG_IP'), CONFIG.get('LOG_PORT'), 3)
                    LOG_SOCKET = 1
                except Exception, e:
                    DEBUG.send(e)
        
        # log channel authorization
        if((CONFIG.get('REG_LOG_SERVER') == '1') and (LOG_SOCKET == 1) and (LOG_AUTH == 0)):
            DEBUG.send('Start authorization on socket #2 (log)')
            data = ''
            try:
                data = GSM.receive('2')
            except Exception, e:
                DEBUG.send(e)
            if((len(data) > 0)): # and (data.find(AUTH_REQUEST) != -1)):
                GSM.send(REG_LOG_REPLY, '2')
            else:
                DEBUG.send('Authorization failed')
            LOG_AUTH = 1
            DEBUG.send('Authorization complete')
        
        # send TCP debug info
        if((CONFIG.get('DEBUG_TCP') == '1') and (MOD.secCounter() > TCP_LOG_TIMER) and (LOG_SOCKET == 1)):
            buffer = DEBUG.getTcpBuffer()
            GSM.send(buffer, '2')
            TCP_LOG_TIMER = MOD.secCounter() + int(CONFIG.get('DEBUG_TCP_PERIOD'))
        
        # serial to tcp
        data = SERIAL.receive(int(CONFIG.get('TCP_MAX_LENGTH')))
        if(len(data) > 0):
            GSM.sendMDM(data)
        
        # tcp to serial
        data = ''
        try:
            data = GSM.receiveMDM()
        except Exception, e:
            DEBUG.send(e)
        if(len(data) > 0):
            SERIAL.send(data)
            
        resetWatchdog()
    
except Exception, e:
    DEBUG.send('Exception!')
    DEBUG.send(e)
    GSM.reboot()
        

        
