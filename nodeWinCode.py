import tkinter.filedialog as fd
from tkinter import *
from socket import *

class Node():
    # Описание переменных
    __entry = None
    __nodeConnectWindow = None
    __nodeWin = None
    __iP = None
    __portTCP = None
    __nodeIP = None
    __nodePortTCP = None
    __connection = []


    # Инициализация
    def __init__(self):
        self.__createConnectWindow()


    # Создание окна
    def __createConnectWindow(self):
        self.__nodeConnectWindow = Tk(className="Станция мониторинга")
        self.__nodeConnectWindow.resizable(0, 0)

        # Описание объектов окна
        nodeSettingsLabel = Label(self.__nodeConnectWindow, text="Настройки станции мониторинга:", justify=LEFT)

        nodeIPLabel = Label(self.__nodeConnectWindow, text="IP:", justify=LEFT)
        nodeIPInput = StringVar()
        nodeIPEntry = Entry(self.__nodeConnectWindow, width=30, textvariable=nodeIPInput)
        nodeIPEntry.insert(0, "127.0.0.1")

        nodePortTCPLabel = Label(self.__nodeConnectWindow, text="TCP:", justify=LEFT)
        nodePortTCPInput = StringVar()
        nodePortTCPEntry = Entry(self.__nodeConnectWindow, width=30, textvariable=nodePortTCPInput)
        nodePortTCPEntry.insert(0, "15401")

        hubSettingsLabel = Label(self.__nodeConnectWindow, text="Информация о центральной станции:", justify=LEFT)

        iPLabel = Label(self.__nodeConnectWindow, text="IP:", justify=LEFT)
        iPInput = StringVar()
        iPEntry = Entry(self.__nodeConnectWindow, width=30, textvariable=iPInput)
        iPEntry.insert(0, "127.0.0.1")
    
        portTCPLabel = Label(self.__nodeConnectWindow, text="TCP:", justify=LEFT)
        portTCPInput = StringVar()
        portTCPEntry = Entry(self.__nodeConnectWindow, width=30, textvariable=portTCPInput)
        portTCPEntry.insert(0, "14900")

        addNodeConnectionButton = Button(self.__nodeConnectWindow, text="Добавить ноду", width=15, command=lambda: self.__nodeConfiguration(iPInput.get(), portTCPInput.get(), nodeIPInput.get(), nodePortTCPInput.get()))
        
        # Расположение объектов в окне
        Frame(self.__nodeConnectWindow, width=25, height=25).grid(row=1, column=1)
        Frame(self.__nodeConnectWindow, width=25, height=25).grid(row=1, column=4)
        Frame(self.__nodeWin, width=25, height=25).grid(row=9, column=1)
        Frame(self.__nodeWin, width=25, height=25).grid(row=9, column=4)

        nodeSettingsLabel.grid(row=3, column=2, columnspan=2)

        nodeIPLabel.grid(row=4, column=2)
        nodeIPEntry.grid(row=4, column=3)

        nodePortTCPLabel.grid(row=5, column=2)
        nodePortTCPEntry.grid(row=5, column=3)

        hubSettingsLabel.grid(row=6, column=2, columnspan=2)

        iPLabel.grid(row=7, column=2)
        iPEntry.grid(row=7, column=3)

        portTCPLabel.grid(row=8, column=2)
        portTCPEntry.grid(row=8, column=3)

        addNodeConnectionButton.grid(row=9, column=2, columnspan=2)


    # Присвоение глобальных переменных
    def __nodeConfiguration(self, iP, portTCP, nodeIP, nodePortTCP):
        self.__iP = iP
        self.__portTCP = int(portTCP)
        self.__nodeIP = nodeIP
        self.__nodePortTCP = int(nodePortTCP)
        if self.__entry == None:
            self.__entry = fd.askopenfilename()
        
        # Основная функция 
        self.__commandExpect()


    # Отправка информации о дронах центральному серверу
    def __commandExpect(self):
        self.__nodeConnectWindow.after(5000, self.__commandExpect)
        try:
            # Инициализация порта для приема информации
            sockReceiver = socket()
            sockReceiver.bind((self.__nodeIP,self.__nodePortTCP))
            sockReceiver.listen(10)

            print(f">>> Ожидается команда на порт {self.__nodePortTCP}")

            conn, addr = sockReceiver.accept()
            data = conn.recv(80)

            del sockReceiver
            conn.close()
            
            if data == b"NaZavod!!!": # Указана команда для расширения функционала сервера в будущем
                print(f">>> Ожидайте ответа на порт {self.__portTCP+1}")

                # Инициализация порта для отправки данных
                sockSender = socket()
                sockSender.connect((self.__iP,self.__portTCP+1))

                print(f">>> Передача данных из файла {self.__entry}")
                
                # Обновление файла и отправка данных
                with open(self.__entry, "r") as distFile:
                    firstStr = distFile.readline()
                    firstStr = firstStr.replace("\n","")
                    lines = distFile.readlines()
                    liness = []
                    for s in lines:
                        liness.append(s.replace("\n",""))

                sockSender.send(firstStr.encode('utf-8'))

                with open(self.__entry, "w") as distFile:
                    for s in liness:
                        print(s, file=distFile)
                    print(firstStr, file=distFile)
                
                print(">>> Ответ отправлен")
            else:
                print(">>> Неверная команда")
        except FileNotFoundError:
            print(f">>> Файла '{self.__entry}' нет в директории")


    def mainloopp(self):
        self.__nodeConnectWindow.mainloop()
        self.__nodeWin.mainloop()


window = Node()
window.mainloopp()