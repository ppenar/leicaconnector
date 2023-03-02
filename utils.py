from struct import *
import struct

class TMacFrame:
    """Klasa reprezentuje ramkę danych pomiarowych dla sondy TMac. 

    :param code: kod opisuje typ ramki danych. Zawsze 211
    :type code: int(4B)
    :param d1: pierwsza parametr danych ramki
    :type code: int(4B)
    :param d2: drugi parametr danych ramki
    :type d2: int(4B)
    :param d3: trzeci parametr danych ramki
    :type d3: int(4B)


    """
    def __init__(self,_code,_x,_y,_z,_a,_b,_c,_d) -> None:
        self.code =_code
        self.x =_x
        self.y =_y
        self.z =_z
        self.a =_a
        self.b =_b
        self.c =_c
        self.d =_d
    def __str__(self) -> str:
        """Tworzy tekstową reprezentacje obiektu

        :return: reprezentacja obiektu
        :rtype: str
        """
        return "TMac Frame:({code},{x},{y},{z},{a},{b},{c},{d})".format(code=self.code,x=self.x,y=self.y,z=self.z,a=self.a,b=self.b,c=self.c,d=self.d)
    
    def toBytes(self):
        """Metoda zwraca ciąg bajtów (8 bajty*4 pola=32 bajtów) reprezentujący ramkę

        :return: Ciąg bajtów
        :rtype: tables of bytes
        """
        return struct.pack("llllllll",self.code,self.x,self.y,self.z,self.a,self.b,self.c,self.d)
        
    def toCommandStr(self):
        return 'code{0}'.format(self.code)






class LeicaFrame:
    """Klasa reprezentuje ramkę danych, wymienianą pomiędzy serwerem a urządzeniem pomiarowym Leica. 

    :param code: kod opisuje typ ramki danych oraz determinuje interpretacje danych zawartych w ramce. 
    1x - kody konfiguracyjne, 2x -kody danych pomiarowych. Błędnie odczytana ramka ma wartość -1 w każdym polu
    :type code: ulong int(4B)
    :param d1: pierwsza parametr danych ramki
    :type code: ulong int(4B)
    :param d2: drugi parametr danych ramki
    :type d2: ulong int(4B)
    :param d3: trzeci parametr danych ramki
    :type d3: ulong int(4B)


    """
    def __init__(self,_code,_d1,_d2,_d3) -> None:
        self.code =_code
        self.data1 =_d1
        self.data2 =_d2
        self.data3 =_d3
    def __str__(self) -> str:
        """Tworzy tekstową reprezentacje obiektu

        :return: reprezentacja obiektu
        :rtype: str
        """
        return "Frame: code {c}, data: ({d1},{d2},{d3})".format(c=self.code,d1=self.data1,d2=self.data2,d3=self.data3)
    
    def toBytes(self):
        """Metoda zwraca ciąg bajtów (4 bajty*4 pola=16 bajtów) reprezentujący ramkę

        :return: Ciąg bajtów
        :rtype: tables of bytes
        """
        return struct.pack("llll",self.code,self.data1,self.data2,self.data3)

    def toCommandStr(self):
        return 'code{0}'.format(self.code)

def bytesToLeicaFrame(msg):
    """Konwersja ciągu bajtów na obiekt klasy LeicaFrame. Jeśli konwersja jest niepoprawna, każde pole 
    ramki ma wartość -1

    :param msg: ciąg bajtów
    :type msg: bytes
    :return: object of LeicaFrame
    :rtype: LeicaFrame
    """
    try:
        dataTuple= struct.unpack("llll",msg)
        frame = LeicaFrame(dataTuple[0],dataTuple[1],dataTuple[2],dataTuple[3])
        return frame
    except:
        frame = LeicaFrame(-1,-1,-1,-1)
        return frame

def getAckFrame():
    return LeicaFrame(200,1,1,1)


def getErrorFrame():
    return LeicaFrame(201,1,1,1)

def getGeneralErrorFrameByCode(code: str):
    return LeicaFrame(int(code),0,0,0)
def getAckOrErrorCommandFrame(cond:bool, frame: LeicaFrame):
    if cond==True:
        return LeicaFrame(frame.code+100,0,0,0)
    else:
        return LeicaFrame(frame.code+200,0,0,0)

