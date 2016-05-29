from PyQt5.QtWidgets import (QWidget, QGridLayout, 
    QPushButton, QApplication, QLCDNumber, QLabel, QFrame, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from twg import Player, Game, Territory


class MapWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.game = Game(4, 0)

        self.tf = TurnFrame()
        endTurnButton = QPushButton("&EndTurn", self)
        endTurnButton.clicked.connect(self.endTurn)
        endTurnButton.move(1260, 720)
        turnLcd = QLCDNumber(3, self)
        turnLcd.move(90, 715)
        turnLcd.setSegmentStyle(QLCDNumber.Filled)
        turnLcd.resize(60, 40)
        turnTxt = QLabel("Turn:", self)
        turnFont = QFont()
        turnFont.setPointSize(20)
        turnTxt.setFont(turnFont)
        turnTxt.move(20, 720)
        
        self.tf.turnChanged.connect(turnLcd.display)
        self.tf.turnChanged.emit(self.game.turn)

        self.showPlayerInfo()

        self.coords = []
        self.setWindowTitle("Territory War")
        n = self.game.map.dim
        self.makeMap(1100 // n, 600 // n, n)
        self.setWindowState(Qt.WindowFullScreen)
        self.setFixedSize(self.size())

    def endTurn(self):
        self.tf.turnChanged.emit(self.game.turn)

    def makeMap(self, width, height, n):
        for i in range(n):
            self.coords.append([])
            for j in range(n):
                self.coords[i].append(TerritorySqare(self, self.game.map.map[i][j]))
                square = self.coords[i][j]
                square.mouseReleaseEvent = self.showTerritoryDialog
                square.incomeChanged.emit(square.ter.get_income())
                square.marketUpgr.emit(square.ter.buildings.market_lvl)
                square.fortUpgr.emit(square.ter.buildings.fort_lvl)
                square.setGeometry(110 + i * (width + 1), 60 + j * (height + 1), width, height)
                color = QColor(*square.ter.owner.color) if square.ter.owner else QColor(127, 127, 127)
                square.setStyleSheet("QWidget { background-color: %s }" % color.name())

    def showTerritoryDialog(self, event):
        territory_dialog = TerritoryDialog(self, event)

        territory_dialog.setWindowTitle("Territory Name Here")
        territory_dialog.setWindowModality(Qt.ApplicationModal)
        territory_dialog.setFixedSize(280, 200)
        territory_dialog.exec_()

    def showPlayerInfo(self):
        nameLbl = QLabel('Player Name:', self)
        nameLbl.move(10, 10)
        nameFont = QFont()
        nameFont.setPointSize(15)
        nameLbl.setFont(nameFont)

        player = QLabel('Niko',self)
        player.setGeometry(130, 10, 40, 30)
        player.setFont(QFont(nameFont.family(), 16, 200, True))
        player.setStyleSheet("QWidget { color: %s }" % QColor(0, 255, 0).name())
        player.adjustSize()


class TurnFrame(QFrame):
    turnChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()


class TerritorySqare(QFrame):
    incomeChanged = pyqtSignal(int)
    marketUpgr = pyqtSignal(int)
    fortUpgr = pyqtSignal(int)

    def __init__(self, parent, ter):
        super().__init__(parent)
        self.ter = ter


class TerritoryDialog(QDialog):
    def __init__(self, map, event):
        super().__init__()
        self.square = map.childAt(event.globalX(), event.globalY())
        self.addButtons()
        self.addLabels()
        self.addLCDNumbers()

    def addButtons(self):
        b1 = QPushButton("ok", self)
        b1.move(65, 170)
        self.marketUpgrB = QPushButton("Upgrade market: {}".format(self.square.ter.buildings.get_market_cost()), self)
        self.marketUpgrB.move(160, 100)
        self.marketUpgrB.clicked.connect(self.upgrMarket)
        self.marketUpgrB.setEnabled(self.square.ter.can_upgr_market())
        self.fortUpgrB = QPushButton("Upgrade fort: {}".format(self.square.ter.buildings.get_fort_cost()), self)
        self.fortUpgrB.move(160, 60)
        self.fortUpgrB.resize(self.fortUpgrB.width() + 5, self.fortUpgrB.height())
        self.fortUpgrB.clicked.connect(self.upgrFort)
        self.fortUpgrB.setEnabled(self.square.ter.can_upgr_fort())

    def addLabels(self):
        self.fortTxt = QLabel("Fort level:", self)
        self.fortTxt.move(10, 60)
        self.marketTxt = QLabel("Market level:", self)
        self.marketTxt.move(10, 100)
        self.incomeTxt = QLabel("Income:", self)
        self.incomeTxt.move(10, 20)
        txtFont = QFont()
        txtFont.setPointSize(15)

        self.fortTxt.setFont(txtFont)
        self.marketTxt.setFont(txtFont)
        self.incomeTxt.setFont(txtFont)

    def addLCDNumbers(self):
        fortLCD = QLCDNumber(1, self)
        fortLCD.setFrameShape(QFrame.NoFrame)
        fortLCD.move(125, 50)
        fortLCD.resize(40, 40)
        fortLCD.display(self.square.ter.buildings.fort_lvl)
        incomeLCD = QLCDNumber(2, self)
        incomeLCD.setFrameShape(QFrame.NoFrame)
        incomeLCD.move(117, 10)
        incomeLCD.resize(40, 40)
        incomeLCD.display(self.square.ter.get_income())
        marketLCD = QLCDNumber(1, self)
        marketLCD.setFrameShape(QFrame.NoFrame)
        marketLCD.move(125, 90)
        marketLCD.resize(40, 40)
        marketLCD.display(self.square.ter.buildings.market_lvl)

        self.square.incomeChanged.connect(incomeLCD.display)
        self.square.fortUpgr.connect(fortLCD.display)
        self.square.marketUpgr.connect(marketLCD.display)

    def upgrFort(self, event):
        self.square.ter.upgr_fort()
        self.fortUpgrB.setText("Upgrade fort: {}".format(self.square.ter.buildings.get_fort_cost()))
        self.fortUpgrB.setEnabled(self.square.ter.can_upgr_fort())
        self.marketUpgrB.setEnabled(self.square.ter.can_upgr_market())
        self.square.fortUpgr.emit(self.square.ter.buildings.fort_lvl)
        

    def upgrMarket(self, event):
        self.square.ter.upgr_market()
        self.marketUpgrB.setText("Upgrade market: {}".format(self.square.ter.buildings.get_market_cost()))
        self.marketUpgrB.setEnabled(self.square.ter.can_upgr_market())
        self.fortUpgrB.setEnabled(self.square.ter.can_upgr_fort())
        self.square.marketUpgr.emit(self.square.ter.buildings.market_lvl)
        self.square.incomeChanged.emit(self.square.ter.get_income())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())