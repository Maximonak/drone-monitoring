import tkinter.filedialog as fd
from tkinter import *
from time import *
from socket import *
import numpy as np

class Hub():
    # Описание переменных
    __dronesNum = None
    __nodesNum = None
    __canvas = None
    __canvasSize = None
    __infoLabel = None
    __fileNameInput = None
    __entry = None
    dCoordsPre = []
    __connections = []
    __distances = []
    __coords = []
    _coordssPre = []
    _xyzCoordsPre = []
    _yCoordsPre = []
    _xCoordsPre = []
    _zCoordsPre = []
    _pathLines = []
    __droneSpeeds = []


    # Инициализация
    def __init__(self):
        self.__createWindow()


    # Создание окна
    def __createWindow(self):
        self.__hubWin = Tk(className="Центральная станция")
        self.__hubWin.resizable(0, 0)

        # Описание объектов окна
        self.__infoLabel = Label(self.__hubWin, height=10, anchor=NW, justify=LEFT)

        trackButton = Button(self.__hubWin, text="Начать слежение", width=15, command=self.__dronesTracking)

        inputButton = Button(self.__hubWin, text="Конфигурационный файл", width=25, command=self.__configurate)

        # Расположение объектов в окне
        Frame(self.__hubWin, width=25, height=25).grid(row=1, column=1)
        Frame(self.__hubWin, width=25, height=25).grid(row=1, column=4)

        inputButton.grid(row=2, column=2, columnspan=2, sticky=NSEW)
        self.__infoLabel.grid(row=3, column=2, columnspan=2, sticky=NSEW)
        trackButton.grid(row=4, column=2, sticky=W)


    # Создание окна слежения
    def __createTrackingWindow(self):
        self.__trackingWin = Tk()
        self.__canvasSize = [600,450]
        self.__trackingWin.resizable(0, 0)
        self.__canvas = Canvas(self.__trackingWin, width=self.__canvasSize[0]+10, height=self.__canvasSize[1], bg="white")
        self.__trackInfo = Label(self.__trackingWin, width=40, height=25, anchor=NW, justify=LEFT)

        self.__trackInfo.grid(row=1, column=1)
        self.__canvas.grid(row=1, column=2)


    # Открытие файла и запись данных в переменные
    def __configurate(self):
        try:
            if self.__entry == None:
                self.__entry = fd.askopenfilename()

            self.__connections = []
            with open(self.__entry, 'r') as confFile: 
                self.__nodesNum ,self.__dronesNum = map(int, confFile.readline().split())
                nodesInfoStr = confFile.readlines()
        
            self.__infoLabelConfigure(self.__nodesNum, self.__dronesNum, nodesInfoStr)

            for i in nodesInfoStr:
                self.__connections.append([i.split()[0], int(i.split()[1]), int(i.split()[2]), int(i.split()[3])])

        except FileNotFoundError:
            print(f">>>файла '{self.__entry}' нет в директории")
            self.__hubWin.destroy()
            self.__createWindow()


    # Вывод данных о станциях мониторинга
    def __infoLabelConfigure(self, nodesNum=None, dronesNum=None, nodesInf=[]):
        info = f"Кол-во станций мониторинга: {nodesNum}\n"\
               f"Кол-во дронов: {dronesNum}\n"\
                "Доступные станции мониторинга:\n"
        for s in nodesInf:
            info += "    " + s
        self.__infoLabel.configure(text=info)


    # Запуск процесса отслеживания дронов
    def __dronesTracking(self):

        self.__createTrackingWindow()

        info = open("savedInfo.txt", "w")

        self.__trackingСycle(info)


    # Цикл вычисления и отрисовки точек дронов
    def __trackingСycle(self, info):
        x = round(time())
        self.__trackingWin.after(10000, lambda info=info: self.__trackingСycle(info))
        print(F">>> время: {x}")

        self.__configurate()

        self.__TCPExchange()

        self.__coordsFinding(self.__distances, self.__connections)

        self.__trackVisualize(self.__connections, self.__coords)

        self.__saveInformation(info, self.__coords, self.__droneSpeeds)


    # Принятие и запись информации от серверов
    def __TCPExchange(self):
        self.__distances = []
        distancess = []

        try:
            for i in range(len(self.__connections)):
                print(f">>> {i+1} элемент опрошен")
                
                self.__sockSender = socket()
                self.__sockSender.connect((self.__connections[i][0],self.__connections[i][1]))
                self.__sockSender.send(b"NaZavod!!!") # Указана команда для расширения функционала сервера в будущем
                self.__sockSender.close()

                print(f">>> ожидается ответ на порт 14901")

                sockReceiver = socket()
                sockReceiver.bind(("127.0.0.1",14901))
                sockReceiver.listen(1)
                self.__conn, addr = sockReceiver.accept()
                data = self.__conn.recv(40)
                data = data.decode('utf-8')

                self.__conn.close()
                del sockReceiver

                print(f">>> ответ {i} элемента: {data}")
  
                distancess.append(data.split())
            self.__distances.append(distancess)
        except ConnectionRefusedError:
            print(">>> нет активных СМ")  
            self.__trackingWin.destroy()  


    # Нахождение координат дрона
    def __coordsFinding(self, distances, connections):
        self.__coords = []
        pointss = []
        distancess = []
        
        for iNode in range(self.__nodesNum):
            pointss.append([self.__connections[iNode][2], self.__connections[iNode][3], 0])
        for iDist in range(self.__dronesNum):
            dist = []
            distances3 = []
            for iNode in range(self.__nodesNum):
                dist = float(self.__distances[0][iNode][iDist])
                distances3.append(dist)
            distancess.append(distances3)
        
        for i in range(self.__dronesNum):
            droneCoords = self.__trilaterate(pointss, distancess[i])
            self.__coords.append(droneCoords)

        print(f">>> координаты дронов: {self.__coords}")


    # Вывод в окно координаты дронов и серверов
    def __trackVisualize(self, nCoords, dCoords):
        coordsCenter = [10, self.__canvasSize[1]-10]
        self.__canvas.delete(ALL)
        self.__trackInfo.configure(text="")
        
        tInfo = ""

        self.__canvas.create_line(coordsCenter, coordsCenter[0]+190, coordsCenter[1]-190, fill='Blue', width=2, arrow=LAST, arrowshape="5 15 5")
        self.__canvas.create_line(coordsCenter, coordsCenter[0]+380, coordsCenter[1], fill='Red', width=2, arrow=LAST, arrowshape="5 15 5")
        self.__canvas.create_line(coordsCenter, coordsCenter[0], 10, fill='Green', width=2, arrow=LAST, arrowshape="5 15 5")

        # Цена деления для каждой оси
        yDV = 18
        xzDV = 36

        for i in range(11):
            self.__canvas.create_text(coordsCenter[0] + i * xzDV, coordsCenter[1], anchor=NW, text=f"{i}", font="Arial 6")
            self.__canvas.create_line(coordsCenter[0] + i * xzDV, coordsCenter[1], coordsCenter[0] + i * xzDV, coordsCenter[1] - 5, fill='Red')

        for i in range(10):
            self.__canvas.create_text(coordsCenter[0]-2, coordsCenter[1] - (i+1) * xzDV, anchor=NE, text=f"{i+1}", font="Arial 6")
            self.__canvas.create_line(coordsCenter[0] + 3, coordsCenter[1] - (i+1) * xzDV, coordsCenter[0] - 2, coordsCenter[1] - (i+1) * xzDV, fill='Green')

        for i in range(10):
            self.__canvas.create_text(coordsCenter[0] + (i+1) * yDV, coordsCenter[1] - (i+1) * yDV, anchor=SE, text=f"{i+1}", font="Arial 6")
            self.__canvas.create_line(coordsCenter[0] + (i+1) * yDV, coordsCenter[1] - (i+1) * yDV, coordsCenter[0] + (i+1) * yDV, coordsCenter[1] - (i+1) * yDV, fill='Blue')

        # Отрисовка точек серверов
        for coords in nCoords:
            coords.pop(0)
            coords.pop(0)

            yCoord = [coordsCenter[0] + coords[1] * yDV, coordsCenter[1] - coords[1] * yDV]
            xCoord = [coordsCenter[0] + coords[0] * xzDV, coordsCenter[1]]
            xyCoord = [coordsCenter[0] + coords[1] * yDV + coords[0] * xzDV , coordsCenter[1] - coords[1] * yDV]

            self.__canvas.create_oval(xyCoord[0]-5, xyCoord[1]-5, xyCoord[0]+5, xyCoord[1]+5, fill="Black")

            self.__canvas.create_line(coordsCenter[0] + coords[0] * xzDV,coordsCenter[1] ,coordsCenter[0] + coords[0] * xzDV + coords[1] * yDV,  coordsCenter[1] - coords[1] * yDV, fill="Blue")
            self.__canvas.create_line(coordsCenter[0] + coords[1] * yDV, coordsCenter[1] - coords[1] * yDV ,coordsCenter[0] + coords[0] * xzDV + coords[1] * yDV,  coordsCenter[1] - coords[1] * yDV, fill="Red")

        coordss = []
        xyzCoords = []
        yCoords = []
        xCoords = []
        zCoords = []

        # Нахождение координат точек дронов в системе окна
        for coords in dCoords:
            yCoord = [coordsCenter[0] + coords[1] * yDV, coordsCenter[1] - coords[1] * yDV]
            xCoord = [coordsCenter[0] + coords[0] * xzDV, coordsCenter[1]]
            zCoord = [coordsCenter[0], coordsCenter[1] - coords[2] * xzDV]
            xyzCoord = [coordsCenter[0] + coords[1] * yDV + coords[0] * xzDV, coordsCenter[1] - coords[1] * yDV - coords[2] * xzDV]

            coordss.append(coords)
            xyzCoords.append(xyzCoord)
            yCoords.append(yCoord)
            xCoords.append(xCoord)
            zCoords.append(zCoord)

        # Сравнение координат точек дронов и нахождение скорости
        if self.dCoordsPre !=[]:
            self.__droneSpeeds = []
            for i in range(self.__dronesNum):
                if dCoords[i] != self.dCoordsPre[i]:
                    self._pathLines.append([xyzCoords[i][0], xyzCoords[i][1] ,coordsCenter[0] + self.dCoordsPre[i][1] * yDV + self.dCoordsPre[i][0] * xzDV, coordsCenter[1] - self.dCoordsPre[i][1] * yDV - self.dCoordsPre[i][2] * xzDV])
                    self.__droneSpeeds.append(((dCoords[i][0] - self.dCoordsPre[i][0])**2 + (dCoords[i][1] - self.dCoordsPre[i][1])**2 + (dCoords[i][2] - self.dCoordsPre[i][2])**2)**0.5 / 10 * 1000)
                else:
                    self.__droneSpeeds.append(0)
        else:
            for _ in range(self.__dronesNum):
                self.__droneSpeeds.append(0)

        for coords in dCoords:
            tInfo += f"{dCoords.index(coords)+1} точка: {coords}\n"
            tInfo += f"    Скорость: {self.__droneSpeeds[dCoords.index(coords)]} м/с\n"
            
        self.__trackInfo.configure(text=tInfo)

        # Отрисовка траектории дронов
        for lines in self._pathLines:
            self.__canvas.create_line(lines, fill="Black")

        self.dCoordsPre = dCoords

        # Отрисовка дронов и вспомогательных линий
        for i in range(self.__dronesNum):
            self.__canvas.create_oval(xyzCoords[i][0]-3, xyzCoords[i][1]-3, xyzCoords[i][0]+3, xyzCoords[i][1]+3, fill="Green")
            self.__canvas.create_text(xyzCoords[i][0]+3, xyzCoords[i][1]-3, anchor=SW, text=f"{self.__droneSpeeds[i]} м/с")

            self.__canvas.create_line(coordsCenter[0] + coordss[i][0] * xzDV,coordsCenter[1] ,coordsCenter[0] + coordss[i][0] * xzDV + coordss[i][1] * yDV,  coordsCenter[1] - coordss[i][1] * yDV, fill="Blue")
            self.__canvas.create_line(coordsCenter[0] + coordss[i][0] * xzDV + coordss[i][1] * yDV,  coordsCenter[1] - coordss[i][1] * yDV, xyzCoords[i][0], xyzCoords[i][1], fill="Green")
            self.__canvas.create_line(coordsCenter[0] + coordss[i][1] * yDV, coordsCenter[1] - coordss[i][1] * yDV ,coordsCenter[0] + coordss[i][0] * xzDV + coordss[i][1] * yDV,  coordsCenter[1] - coordss[i][1] * yDV, fill="Red")
        

    # Сохранение информации в файл
    def __saveInformation(self, info, coords, speeds):
        info = open("savedInfo.txt", "a")
        print(f"{strftime('%Y-%m-%d-%H.%M.%S')}", file=info)
        for i in range(self.__dronesNum):
            print(f"{i+1} точка:\n  Координаты: {coords[i]}\n  Скорость: {speeds[i]} м/с\n", file=info)


    # Трилатерация
    def __trilaterate(self, points, distances):
        p1,p2,p3 = points
        r1,r2,r3 = distances

        def norm(v):
            vv = []
            for i in v:
                vv.append(i**2)
            return (np.sum(vv))**0.5
        def dot(v1,v2):
            return np.dot(v1,v2)
        def cross(v1,v2):
            return np.cross(v1,v2)

        temp1 = []
        for i, j in zip(p2, p1):
            temp1.append(i-j)

        ex = (temp1) / norm(temp1)

        temp2 = []
        for i, j in zip(p3, p1):
            temp2.append(i-j)

        i = dot(ex, temp2)
        a = (temp2) - ex*i
        ey = a / norm(a)
        ez = cross(ex, ey)
        d = norm(temp1)
        j = dot(ey, temp2)
        x = (r1**2 - r2**2 + d**2) / (2*d)
        y = (r1**2 - r3**2 + i**2 + j**2) / (2*j) - (i/j) * x
        b = r1**2 - x**2 - y**2

        z = b**0.5

        a = p1 + ex*x + ey*y
        p4a = a - ez*z

        coords = list(p4a)
        roundCoords = []
        for element in coords:
            roundCoords.append(round(element, 3))

        return roundCoords


    def mainloopp(self):
        self.__hubWin.mainloop()
        self.__trackingWin.mainloop()

        self.__conn.close()
        self.__sockSender.close()


window = Hub()
window.mainloopp()