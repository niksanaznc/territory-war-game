from PyQt5.QtWidgets import (
    QWidget, QPushButton, QApplication, QLCDNumber,
    QLabel, QFrame, QDialog, QSlider, QInputDialog
    )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from logic import *
import threading
import time


class MapWindow(QWidget):
    '''
    Main class of the game GUI.
    '''
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.game = Game(4)  # Make game with 4 players

        self.sig = Signals()
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

        self.sig.turnChanged.connect(turnLcd.display)
        self.sig.turnChanged.emit(self.game.turn)

        quitB = QPushButton("&Quit", self)
        quitB.clicked.connect(self.quit)
        quitB.move(1150, 720)

        self.showPlayerInfo()

        self.coords = []
        self.setWindowTitle("Territory War")
        n = self.game.map.dim
        self.makeMap(1100 // n, 600 // n, n)
        self.setWindowState(Qt.WindowFullScreen)
        self.setFixedSize(self.size())

        self.showArmies()
        self.addDiplomacyLabels()

        thread = threading.Thread(target=self.game.start, args=(0, ))
        thread.start()

    def endTurn(self):
        '''
        Method to end the current player's turn and refresh all
        the interface to show the next active player's info.
        '''
        self.game.player.end_turn.release()
        time.sleep(1)
        self.sig.turnChanged.emit(self.game.turn)
        self.player.setText(self.game.player.name)
        color = QColor(*self.game.player.color).name()
        self.player.adjustSize()
        self.player.setStyleSheet("QWidget { color: %s }" % color)
        self.sig.goldChanged.emit(self.game.player.gold)
        self.sig.incomeChanged.emit(self.game.player.income())
        maint = self.game.player.get_armies_maint()
        self.sig.maintChanged.emit(maint[0] + maint[1])
        for row in self.coords:
            for ter in row:
                ter.update()
        self.updateButtons()
        self.raisePlayerArmies(self.game.player)
        self.showOffers()

    def makeMap(self, width, height, n):
        '''
        Generates the graphical map, from the game's map. Sets events
        and connects signals for the territories.
        '''
        for i in range(n):
            self.coords.append([])
            for j in range(n):
                ter_square = TerritorySquare(self, self.game.map.map[i][j])
                self.coords[i].append(ter_square)
                square = self.coords[i][j]
                square.mouseReleaseEvent = self.showTerritoryDialog
                square.incomeChanged.emit(square.ter.get_income())
                square.marketUpgr.emit(square.ter.buildings.market_lvl)
                square.fortUpgr.emit(square.ter.buildings.fort_lvl)
                x = 110 + i * (width + 1)
                y = 60 + j * (height + 1)
                square.setGeometry(x, y, width, height)
                if square.ter.owner:
                    color = QColor(*square.ter.owner.color)
                else:
                    color = QColor(127, 127, 127)
                bgcolor = "QWidget { background-color: %s }"
                square.setStyleSheet(bgcolor % color.name())
                square.calcCenter()

    def showTerritoryDialog(self, event):
        territory_dialog = TerritoryDialog(self, event)
        territory_dialog.setWindowTitle("Territory")
        territory_dialog.setWindowModality(Qt.ApplicationModal)
        territory_dialog.setFixedSize(280, 240)
        territory_dialog.exec_()

    def showPlayerInfo(self):
        '''
        Displays player name label.
        '''
        nameLbl = QLabel('Player Name:', self)
        nameLbl.move(10, 10)
        font = QFont()
        font.setPointSize(17)
        nameLbl.setFont(font)

        self.addGoldInfo(font)
        self.addPlayerInfo(font)
        self.addIncomeInfo(font)
        self.addMaintInfo(font)

    def addGoldInfo(self, font):
        '''
        Adds gold LCDNumber and connects it with the correct signal.
        '''
        goldLbl = QLabel('Gold:', self)
        goldLbl.move(300, 10)
        goldLbl.setFont(font)
        goldLcd = QLCDNumber(4, self)
        goldLcd.move(360, 0)
        goldLcd.setFrameShape(QFrame.NoFrame)
        goldLcd.resize(65, 40)
        self.sig.goldChanged.connect(goldLcd.display)
        self.sig.goldChanged.emit(self.game.player.gold)

    def addPlayerInfo(self, font):
        '''
        Shows current player's name and adds event for changing player's name.
        '''
        self.player = QLabel(self.game.player.name, self)
        color = QColor(*self.game.player.color).name()
        self.player.setGeometry(150, 10, 40, 30)
        self.player.setFont(QFont(font.family(), 16, 200, True))
        self.player.setStyleSheet("QWidget { color: %s }" % color)
        self.player.adjustSize()
        self.player.mouseReleaseEvent = self.changePlayerName

    def addIncomeInfo(self, font):
        '''
        Adds the income LCDNumber and connects it with the correct signals.
        '''
        incomeLbl = QLabel("Income:", self)
        incomeLbl.setFont(font)
        incomeLbl.move(460, 10)
        incomeLcd = QLCDNumber(3, self)
        incomeLcd.move(530, 0)
        incomeLcd.setFrameShape(QFrame.NoFrame)
        incomeLcd.resize(60, 40)
        self.sig.incomeChanged.connect(incomeLcd.display)
        self.sig.incomeChanged.emit(self.game.player.income())

    def addMaintInfo(self, font):
        '''
        Adds maintenance QLCDNumber and connects it with the correct signals.
        '''
        maintLbl = QLabel("Total maintenance:", self)
        maintLbl.move(620, 10)
        maintLbl.setFont(font)
        maintLcd = QLCDNumber(3, self)
        maintLcd.move(840, 7)
        maintLcd.setFrameShape(QFrame.NoFrame)
        maintLcd.resize(50, 30)
        self.sig.maintChanged.connect(maintLcd.display)
        maint = self.game.player.get_armies_maint()
        self.sig.maintChanged.emit(maint[0] + maint[1])

    def addDiplomacyLabels(self):
        '''
        Displays diplomatic labels for every player.
        '''
        y = 100
        font = QFont()
        font.setPointSize(17)
        self.diploLbls = []
        for player in self.game.players:
            lbl = DiploLabel(player.name, self)
            lbl.move(1230, y)
            color = player.color
            lbl.setStyleSheet("QWidget { color: %s }" % QColor(*color).name())
            lbl.setFont(QFont(font.family(), 16, 200, True))
            self.diploLbls.append(lbl)
            y = y + 50
        diplomacy = QLabel("Diplomacy", self)
        diplomacy.move(1230, 50)
        diplomacy.setFont(QFont(font.family(), 16, 200, True))

    def updateDiploLabels(self):
        '''
        Updates diplomatic label's texts when any player's name is changed.
        '''
        for i in range(len(self.game.players)):
            self.diploLbls[i].setText(self.game.players[i].name)

    def changePlayerName(self, event):
        '''
        Method that calls input dialog to change player's name.
        '''
        input = QInputDialog(self)
        input.setLabelText("Name")
        input.setWindowTitle("Change name")
        if input.exec_() == 1:
            newName = input.textValue()
            self.game.player.name = newName
            self.player.setText(newName)
            self.updateDiploLabels()

    def showArmies(self):
        '''
        Initially adds players' armies in the GUI.
        '''
        self.armies = []
        for player in self.game.players:
            for army in player.armies:
                x = army.pos_x
                y = army.pos_y
                center = self.coords[x][y].center
                self.armies.append(ArmySquare(self, army, center))
        self.addArmyButtons()

    def raisePlayerArmies(self, player):
        '''
        Raises player's armies to the top of the map layer.
        '''
        for army in self.armies:
            if army.army.owner is player:
                army.raise_()
            if army.army.killed():
                army.close()

    def addArmyButtons(self):
        '''
        Adds buttons for upgrading of the player's units and connects these
        buttons to the responsible methods.
        '''
        infPrice = self.game.player.inf_price * 2
        self.infB = QPushButton("Upgrade infantry: {}".format(infPrice), self)
        self.infB.move(0, 100)
        self.infB.setEnabled(self.game.player.can_upgr_inf())
        self.infB.clicked.connect(self.upgrInf)
        cavPrice = self.game.player.cav_price * 2
        self.cavB = QPushButton("Upgrade cavlary: {}".format(cavPrice), self)
        self.cavB.move(0, 130)
        self.cavB.setEnabled(self.game.player.can_upgr_cav())
        self.cavB.clicked.connect(self.upgrCav)

    def upgrCav(self, event):
        '''
        Upgrades player's cavlary units.
        '''
        player = self.game.player
        player.upgr_cav()
        self.updateButtons()
        self.sig.goldChanged.emit(player.gold)

    def upgrInf(self, event):
        '''
        Upgrades player's infantry units.
        '''
        player = self.game.player
        player.upgr_inf()
        self.updateButtons()
        self.sig.goldChanged.emit(player.gold)

    def updateButtons(self):
        '''
        Updates unit upgrade buttons with the new upgrade prices.
        '''
        player = self.game.player
        self.infB.setText("Upgrade infantry: {}".format(player.inf_price * 2))
        self.cavB.setText("Upgrade cavlary: {}".format(player.cav_price * 2))
        self.cavB.setEnabled(player.can_upgr_cav())
        self.infB.setEnabled(player.can_upgr_inf())

    def showOffers(self):
        '''
        Displays dialogs with the pending offers of the current player.
        '''
        for offer in self.game.player.offers:
            offerDialog = OfferDialog(offer)
            if offerDialog.exec_() == 1:
                offer.accept()
                self.sig.goldChanged.emit(self.game.player.gold)
        self.game.player.offers = []

    def quit(self):
        self.game.turn = -1
        for player in self.game.players:
            player.end_turn.release()
        time.sleep(1)
        self.close()


class DiploLabel(QLabel):
    '''
    Class for diplomatic labels. Main reason to make it is adding
    the mouse clicked event to these labels so that they open the
    correct diplomacy windows when clicked.
    '''
    def __init__(self, text, parent):
        super().__init__(text, parent)

    def mouseReleaseEvent(self, event):
        player = None
        active = self.parent().game.player
        for x in self.parent().game.players:
            if x.name == self.text():
                player = x
        self.openDiplomacy(active, player)

    def openDiplomacy(self, active, player):
        dialog = DiploDialog(active, player)
        result = dialog.exec_()


class DiploDialog(QDialog):
    '''
    Diplomatic dialog.
    '''
    def __init__(self, active, player):
        super().__init__()
        self.active = active
        self.player = player
        self.allies = []
        self.enemies = []
        self.gold = 0
        self.setWindowTitle(self.player.name)
        self.addInfo()
        self.addActions()

    def addActions(self):
        '''
        Adds and places the labels and buttons for the diplomatic actions
        possible in the game.
        '''
        actions = QLabel("Actions", self)
        actions.move(0, 80)
        actions.setFont(self.qfont)
        self.ally = QPushButton("Ally", self)
        self.ally.move(0, 100)
        self.ally.adjustSize()
        self.ally.clicked.connect(self.allyClicked)
        self.declareWar = QPushButton("Declare War", self)
        self.declareWar.move(100, 100)
        self.declareWar.adjustSize()
        self.declareWar.clicked.connect(self.warClicked)
        self.peace = QPushButton("Make Peace", self)
        self.peace.move(100, 150)
        self.peace.adjustSize()
        self.peace.clicked.connect(self.peaceClicked)
        self.callToArms = QPushButton("Call to arms", self)
        self.callToArms.move(0, 150)
        self.callToArms.adjustSize()
        self.callToArms.clicked.connect(self.callClicked)
        self.breakAlly = QPushButton("Break Alliance", self)
        self.breakAlly.adjustSize()
        self.breakAlly.move(50, 125)
        self.breakAlly.clicked.connect(self.breakClicked)
        self.updateEnables()

    def addInfo(self):
        '''
        Adds allies and enemies labels.
        '''
        self.qfont = QFont()
        self.qfont.setPointSize(13)
        allies = QLabel("Allies", self)
        allies.setFont(self.qfont)
        enemies = QLabel("Enemies", self)
        enemies.setFont(self.qfont)
        enemies.move(0, 40)
        self.addPlayers(self.player.allies, 20, self.allies)
        self.addPlayers(self.player.enemies, 60, self.allies)

    def addPlayers(self, players, y, labels):
        '''
        Displays labels for every player in players and positions them at
        y coordinate y.
        '''
        x = 0
        for player in players:
            lbl = QLabel(player.name, self)
            lbl.move(x, y)
            lbl.setFont(self.qfont)
            color = player.color
            lbl.setStyleSheet("QWidget { color: %s }" % QColor(*color).name())
            x = x + 100
            labels.append(lbl)

    def updateEnemies(self):
        '''
        Updates enemies labels.
        '''
        x = 0
        for label in self.enemies:
            label.move(x, 60)
            x = x + 100

    def removeLabel(self, labels, name):
        '''
        Remove labels with text name from labels.
        '''
        for label in labels:
            if label.text() == name:
                for_del = label
                for_del.hide()
        if for_del:
            labels.remove(for_del)

    def warClicked(self, event):
        self.active.declare_war(self.player)
        lbl = QLabel(self.active.name, self)
        lbl.setFont(self.qfont)
        color = self.active.color
        lbl.setStyleSheet("QWidget { color: %s }" % QColor(*color).name())
        lbl.show()
        msg = " declared war on you"
        offer = Offer("message", self.player, self.active, 0, msg)
        self.player.offers.append(offer)
        self.enemies.append(lbl)
        self.updateEnemies()
        self.updateEnables()

    def peaceClicked(self, event):
        if self.execInput() == 1:
            offer = Offer("peace", self.player, self.active, self.gold)
            self.player.offers.append(offer)
            self.peace.setEnabled(False)

    def allyClicked(self, event):
        if self.execInput() == 1:
            offer = Offer("alliance", self.player, self.active, self.gold)
            self.player.offers.append(offer)
            self.ally.setEnabled(False)
            self.declareWar.setEnabled(False)

    def breakClicked(self, event):
        self.active.break_ally(self.player)
        self.removeLabel(self.allies, self.active.name)
        msg = " broke the alliance with you"
        offer = Offer("message", self.player, self.active, 0, msg)
        self.player.offers.append(offer)
        self.updateEnables()

    def callClicked(self, event):
        if self.execInput() == 1:
            offer = Offer("call to arms", self.player, self.active, self.gold)
            self.player.offers.append(offer)
            self.callToArms.setEnabled(False)

    def execInput(self):
        '''
        Executes the input dialog for adding gold in the offer.
        '''
        input = QInputDialog()
        input.setWindowTitle("Gold ammount")
        msg = "Enter negative number"
        msg = msg + " to offer and positive number to demand gold"
        input.setLabelText(msg)
        input.setIntRange(-self.active.gold, self.player.gold)
        input.setIntValue(0)
        result = input.exec_()
        self.gold = -input.intValue()
        return result

    def updateEnables(self):
        '''
        Updates the enables of all diplomatic actions
        in the diplomatic window.
        '''
        notActive = self.player is not self.active
        allyEnabled = self.player not in self.active.allies and notActive
        allyEnabled = allyEnabled and self.player not in self.active.enemies
        self.ally.setEnabled(allyEnabled)
        peaceEnabled = self.player in self.active.enemies and notActive
        self.peace.setEnabled(peaceEnabled)
        self.callToArms.setEnabled(self.active.can_call_to_arms(self.player))
        self.declareWar.setEnabled(allyEnabled)
        self.breakAlly.setEnabled(self.active in self.player.allies)


class OfferDialog(QDialog):
    '''
    Diplomatic offer dialog. Shows every time a player receives an offer.
    '''
    def __init__(self, offer):
        super().__init__()
        self.offer = offer
        self.setWindowTitle("Diplomatic message")
        self.addLabels()
        if self.offer.type == "message":
            ok = QPushButton("OK", self)
            ok.move(50, 100)
            ok.clicked.connect(self.accept)
        else:
            self.addButtons()

    def addLabels(self):
        msg = self.offer.msg
        if self.offer.gold < 0:
            txt = " and demands {} gold.".format(abs(self.offer.gold))
        elif self.offer.gold > 0:
            txt = " and offers {} gold.".format(abs(self.offer.gold))
        else:
            txt = "."
        if self.offer.type == "peace":
            msg = " offers you peace"
        elif self.offer.type == "alliance":
            msg = " offers you alliance"
        elif self.offer.type == "call to arms":
            msg = " calls you to arms in a war against"
            for player in self.offer.sender.enemies:
                msg = msg + " {}".format(player.name)
        msg = self.offer.sender.name + msg + txt
        lbl = QLabel(msg, self)
        lbl.adjustSize()

    def addButtons(self):
        accept = QPushButton("accept", self)
        accept.move(20, 100)
        accept.clicked.connect(self.accept)
        decline = QPushButton("decline", self)
        decline.move(170, 100)
        decline.clicked.connect(self.reject)


class Signals(QFrame):
    '''
    Dummie class for all the signals needed in MapWindow.
    '''
    turnChanged = pyqtSignal(int)
    goldChanged = pyqtSignal(float)
    incomeChanged = pyqtSignal(int)
    maintChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()


class TerritorySquare(QFrame):
    '''
    Class for a territory on the map.
    '''
    incomeChanged = pyqtSignal(int)
    marketUpgr = pyqtSignal(int)
    fortUpgr = pyqtSignal(int)

    def __init__(self, parent, ter):
        super().__init__(parent)
        self.ter = ter

    def calcCenter(self):
        '''
        Calculates the center coordinates of the territory.
        Needed for the placing of the armies on the territories.
        '''
        center_x = self.pos().x() + self.width() // 2
        center_y = self.pos().y() + self.height() // 2
        self.center = (center_x, center_y)

    def update(self):
        '''
        Updates the colour of the territory.
        '''
        if self.ter.owner:
            color = self.ter.owner.color
            bgcolor = "QWidget { background-color: %s }"
            self.setStyleSheet(bgcolor % QColor(*color).name())


class TerritoryDialog(QDialog):
    '''
    Dialog showed every time a territory is clicked.
    '''
    def __init__(self, map, event):
        super().__init__()
        self.mapW = map
        self.square = map.childAt(event.globalX(), event.globalY())
        self.addButtons()
        self.addLabels()
        self.addLCDNumbers()

    def addButtons(self):
        ter = self.square.ter
        player = self.mapW.game.player
        cost = ter.buildings.get_market_cost()
        self.marketUpgrB = QPushButton("Upgrade market: {}".format(cost), self)
        self.marketUpgrB.move(160, 100)
        self.marketUpgrB.clicked.connect(self.upgrMarket)
        self.marketUpgrB.setEnabled(ter.can_upgr_market())
        cost = ter.buildings.get_fort_cost()
        self.fortUpgrB = QPushButton("Upgrade fort: {}".format(cost), self)
        self.fortUpgrB.move(160, 60)
        self.fortUpgrB.setFixedWidth(self.fortUpgrB.width() + 5)
        self.fortUpgrB.clicked.connect(self.upgrFort)
        self.fortUpgrB.setEnabled(ter.can_upgr_fort())

        owner = ter.owner
        cavPrice = owner.cav_price if owner else 0
        infPrice = owner.inf_price if owner else 0
        self.hireCavB = QPushButton("Hire cavlary: {}".format(cavPrice), self)
        self.hireCavB.move(160, 140)
        self.hireCavB.clicked.connect(self.hireCav)
        cavEnable = owner is player and owner.can_hire_cav()
        infEnable = owner is player and owner.can_hire_inf()
        self.hireCavB.setEnabled(cavEnable and not ter.is_sieged())
        self.hireInfB = QPushButton("Hire infantry: {}".format(infPrice), self)
        self.hireInfB.move(10, 140)
        self.hireInfB.clicked.connect(self.hireInf)
        self.hireInfB.setEnabled(infEnable and not ter.is_sieged())

    def addLabels(self):
        self.fortTxt = QLabel("Fort level:", self)
        self.fortTxt.move(10, 60)
        self.marketTxt = QLabel("Market level:", self)
        self.marketTxt.move(10, 100)
        self.incomeTxt = QLabel("Income:", self)
        self.incomeTxt.move(10, 20)
        isSieged = self.square.ter.siege_leader
        capTime = self.square.ter.capture_time
        sieger = self.square.ter.siege_leader.name if isSieged else ""
        turns = self.square.ter.capture_time if capTime > 0 else ""
        msg = "Sieged by: {}\nCapture turns left: {}".format(sieger, turns)
        self.siegeTxt = QLabel(msg, self)
        self.siegeTxt.move(10, 180)
        txtFont = QFont()
        txtFont.setPointSize(15)

        self.fortTxt.setFont(txtFont)
        self.marketTxt.setFont(txtFont)
        self.incomeTxt.setFont(txtFont)
        self.siegeTxt.setFont(txtFont)

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
        '''
        Method to upgrade the fort of the territory.
        '''
        player = self.mapW.game.player
        ter = self.square.ter
        ter.upgr_fort()
        cost = ter.buildings.get_fort_cost()
        self.fortUpgrB.setText("Upgrade fort: {}".format(cost))
        self.updateEnables()
        self.square.fortUpgr.emit(ter.buildings.fort_lvl)
        self.mapW.sig.goldChanged.emit(player.gold)

    def upgrMarket(self, event):
        '''
        Method to upgrade the market of the territory.
        '''
        player = self.mapW.game.player
        ter = self.square.ter
        ter.upgr_market()
        cost = ter.buildings.get_market_cost()
        self.marketUpgrB.setText("Upgrade market: {}".format(cost))
        self.updateEnables()
        self.square.marketUpgr.emit(ter.buildings.market_lvl)
        self.square.incomeChanged.emit(ter.get_income())
        self.mapW.sig.goldChanged.emit(player.gold)
        self.mapW.sig.incomeChanged.emit(player.income())

    def hireCav(self, event):
        player = self.mapW.game.player
        self.hireTroops(player.hire_cav, "cav_price")

    def hireInf(self, event):
        player = self.mapW.game.player
        self.hireTroops(player.hire_inf, "inf_price")

    def hireTroops(self, hireF, troopPrice):
        '''
        Hires troops on the current territory. hireF is the function for
        hiring the troops.
        '''
        player = self.mapW.game.player
        ter = self.square.ter
        army = hireF(ter.x, ter.y)
        center_widget = self.mapW.childAt(*self.square.center)
        if isinstance(center_widget, ArmySquare):
            center_widget.army = army
        else:
            asq = ArmySquare(self.mapW, army, self.square.center)
            self.mapW.armies.append(asq)
            asq.show()
            asq.raise_()
        self.updateEnables()
        self.mapW.sig.goldChanged.emit(player.gold)
        maint = player.get_armies_maint()
        self.mapW.sig.maintChanged.emit(maint[0] + maint[1])

    def updateEnables(self):
        '''
        Updates the enables of the buttons in the territory dialog.
        '''
        player = self.mapW.game.player
        ter = self.square.ter
        sieged = ter.is_sieged()
        self.hireCavB.setEnabled(player.can_hire_cav() and not sieged)
        self.hireInfB.setEnabled(player.can_hire_inf() and not sieged)
        self.marketUpgrB.setEnabled(ter.can_upgr_market())
        self.fortUpgrB.setEnabled(ter.can_upgr_fort())
        self.mapW.updateButtons()


class ArmySquare(QFrame):
    '''
    Frame for the armies in the GUI.
    '''
    def __init__(self, parent, army, pt):
        super().__init__(parent)
        self.army = army
        color = army.owner.color
        bgcolor = "QWidget { background-color: %s }"
        self.setStyleSheet(bgcolor % QColor(*color).name())
        self.setFrameShape(QFrame.Box)
        self.a = 20
        a = self.a
        self.setGeometry(pt[0] - a / 2, pt[1] - a / 2, a, a)
        self.mouseReleaseEvent = self.moveArmy

    def moveArmy(self, event):
        '''
        Method for moving the army.
        '''
        x = event.globalX()
        y = event.globalY()
        square = self.parent().childAt(x, y)
        if square is self:
            return self.clicked()
        if isinstance(square, ArmySquare):
            square = self.parent().childAt(x + self.a, y + self.a)
        canMove = square and self.army.can_move(square.ter.x, square.ter.y)
        prevPos = self.pos()
        prevPos.setX(prevPos.x() + self.a)
        change = []
        if canMove and self.openMoveDialog(change) == 1 and change:
            self.splitArmy(change)
            if self.army.killed():
                return None
            pt = square.center
            if isinstance(self.parent().childAt(pt[0], pt[1]), ArmySquare):
                self.engage(self.parent().childAt(pt[0], pt[1]), square.ter)
                canMove = self.army.morale > 0 and not self.army.killed()
            else:
                square.ter.siege(self.army.owner)
            prevSquare = self.parent().childAt(prevPos)
            if canMove:  # the army is not killed and we can move it
                self.move(pt[0] - self.a / 2, pt[1] - self.a / 2)
                self.army.move(square.ter.x, square.ter.y)
                self.raise_()
                if change[0] + change[1] == 200:  # whole army is moved
                    prevSquare.ter.lift_siege(self.army.owner)
                    prevX = prevPos.x()
                    prevY = prevPos.y()
                    other = self.parent().childAt(prevX - self.a, prevY)
                    if isinstance(other, ArmySquare) and other.army.owner:
                        prevSquare.ter.siege(other.army.owner)
            elif change[0] + change[1] < 200:
                prevX = prevPos.x()
                prevY = prevPos.y()
                armyLeft = self.parent().childAt(prevX - self.a, prevY)
                if not isinstance(armyLeft, ArmySquare):
                    return None
                armyLeft.army.join(self.army)
                if armyLeft.army.killed():
                    self.parent().armies.remove(armyLeft)
                    armyLeft.close()
                    prevSquare.ter.lift_siege(armyLeft.army.owner)
                self.parent().armies.remove(self)
            else:  # whole army is moved and killed
                prevSquare.ter.lift_siege(self.army.owner)

    def splitArmy(self, change):
        '''
        Method to split the army in two separate armies on diffetent
        locations.
        '''
        if change[0] == 99:  # max percentage selected
            change[0] = 100
        if change[1] == 99:
            change[1] = 100
        if change[0] + change[1] < 200:
            infA = self.army.troops[0].ammount * change[0] // 100
            cavA = self.army.troops[1].ammount * change[1] // 100
            ter_square = self.parent().childAt(self.x() + self.a, self.y())
            pt = ter_square.center
            army = self.army.split((infA, cavA))
            if not army.killed():
                armyLeft = ArmySquare(self.parent(), army, pt)
                armyLeft.raise_()
                armyLeft.show()
                self.parent().armies.append(armyLeft)
            else:
                ter_square.ter.lift_siege(self.army.owner)

    def clicked(self):
        '''
        Army square is clicked -> show army dialog.
        '''
        dialog = ArmyDialog(self.army)
        dialog.setWindowTitle(self.army.owner.name)
        dialog.setFixedSize(280, 200)
        dialog.exec_()

    def openMoveDialog(self, change):
        '''
        Opens the dialog in which the player selects how many percents
        of each unit he wants to move.
        '''
        moveDialog = MoveArmyDialog(self.army)
        moveDialog.setWindowTitle("Choose army ammount")
        moveDialog.setFixedSize(280, 200)
        result = moveDialog.exec_()
        if moveDialog.infSld.value() + moveDialog.cavSld.value() > 0:
            change.append(moveDialog.infSld.value())
            change.append(moveDialog.cavSld.value())
        return result

    def engage(self, other, ter):
        self.army.fight(other.army, ter)
        if self.army.killed():
            self.close()
        if other.army.killed():
            other.close()
        maint = self.parent().game.player.get_armies_maint()
        self.parent().sig.maintChanged.emit(maint[0] + maint[1])


class ArmyDialog(QDialog):
    '''
    Dialog shown when the army square is clicked. Contains information
    about the armies stats.
    '''
    def __init__(self, army):
        super().__init__()
        self.addLabels(army.troops[0], "Infantry", 0)
        self.addLabels(army.troops[1], "Cavlary", 140)
        maint = army.get_maintenance()
        font = QFont()
        font.setPointSize(13)
        infMaint = QLabel("Maintenance: {}".format(maint[0]), self)
        cavMaint = QLabel("Maintenance: {}".format(maint[1]), self)
        infMaint.move(0, 150)
        infMaint.setFont(font)
        cavMaint.move(140, 150)
        cavMaint.setFont(font)

        msg = "Army Morale : {}/{}".format(army.morale, army.get_max_morale())
        moraleLbl = QLabel(msg, self)
        moraleLbl.move(0, 120)
        moraleLbl.setFont(font)

    def addLabels(self, unit, name, x):
        attTxt = "Attack : {}".format(unit.attack)
        defTxt = "Defence : {}".format(unit.defence)
        ammTxt = "Ammount : {}".format(unit.ammount)
        nameLbl = QLabel("     {}".format(name), self)
        attLbl = QLabel(attTxt, self)
        defLbl = QLabel(defTxt, self)
        ammLbl = QLabel(ammTxt, self)
        nameLbl.move(x, 0)
        attLbl.move(x, 30)
        defLbl.move(x, 60)
        ammLbl.move(x, 90)

        font = QFont()
        font.setPointSize(13)

        nameLbl.setFont(font)
        attLbl.setFont(font)
        defLbl.setFont(font)
        ammLbl.setFont(font)


class MoveArmyDialog(QDialog):
    '''
    Dialog opened when the player tries to move an army.
    Lets the player choose how many percents of each unit he desires
    to move.
    '''
    def __init__(self, army):
        super().__init__()
        self.addLabels()
        self.cavSld = QSlider(Qt.Horizontal, self)
        self.cavSld.move(150, 40)
        self.infSld = QSlider(Qt.Horizontal, self)
        self.infSld.move(0, 40)
        self.addNumbers()
        accept = QPushButton("Accept", self)
        accept.move(100, 150)
        accept.clicked.connect(self.accept)

    def addNumbers(self):
        cavNum = QLCDNumber(2, self)
        self.cavSld.valueChanged.connect(cavNum.display)
        self.cavSld.setValue(99)
        cavNum.resize(60, 40)
        cavNum.move(150, 60)
        infNum = QLCDNumber(2, self)
        self.infSld.valueChanged.connect(infNum.display)
        self.infSld.setValue(99)
        infNum.resize(60, 40)
        infNum.move(0, 60)

    def addLabels(self):
        font = QFont()
        font.setPointSize(15)
        infLbl = QLabel("Infantry", self)
        infLbl.setFont(font)
        infLbl.move(0, 0)
        cavLbl = QLabel("Cavlary", self)
        cavLbl.setFont(font)
        cavLbl.move(150, 0)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())
