from logic.twg_army import Army, Cavlary, Infantry


class Player:
    STARTING_GOLD = 30

    def __init__(self, name, color):
        self.name = name
        self.territories = []
        self.armies = []
        self.offers = []
        self.enemies = set()
        self.allies = set()
        self.gold = self.STARTING_GOLD
        self.color = color
        self.active = False
        self.end_turn = False
        self.inf_stats = (1, 5, 1000, 5)  # AD#M
        self.cav_stats = (2, 2, 1000, 5)
        self.inf_price = 4
        self.cav_price = 7

    def play_turn(self):
        self.active = True
        while not self.end_turn:
            pass
        self.active = False

    def get_income(self):
        self.gold = self.gold + self.income()

    def get_armies_maint(self):
        '''
        Returns total army maintenance in a tuple containing
        maintenance of all infantry and cavlary.
        '''
        inf = 0
        cav = 0
        for army in self.armies:
            maint = army.get_maintenance()
            inf = round(inf + maint[0], 2)
            cav = round(cav + maint[1], 2)
        return (inf, cav)

    def pay_maintenance(self):
        maint = self.get_armies_maint()
        self.gold = self.gold - (maint[0] + maint[1])

    def hire_inf(self, x, y):
        '''
        Hires a single stack of infantry and places it on [x,y] position.
        If there is already player's army there, it joins both armies.
        The new infantry stack has 0 morale.
        '''
        self.gold = self.gold - self.inf_price
        inf = Infantry(*self.inf_stats)
        cav = Cavlary(*self.cav_stats)
        cav.ammount = 0
        army = Army(inf, cav, x, y, self)
        army.morale = 0
        self.armies.append(army)
        for arm in self.armies:
            if arm.pos_x == x and arm.pos_y == y and arm is not army:
                arm.join(army)
                return arm
        return army

    def hire_cav(self, x, y):
        '''
        Hires a single stack of cavlary and places it on [x,y] position.
        If there is already player's army there, it joins both armies.
        The new cavlary stack has 0 morale.
        '''
        self.gold = self.gold - self.cav_price
        inf = Infantry(*self.inf_stats)
        inf.ammount = 0
        cav = Cavlary(*self.cav_stats)
        army = Army(inf, cav, x, y, self)
        army.morale = 0
        self.armies.append(army)
        for arm in self.armies:
            if arm.pos_x == x and arm.pos_y == y and arm is not army:
                arm.join(army)
                return arm
        return army

    def can_hire_inf(self):
        return self.gold >= self.inf_price

    def can_hire_cav(self):
        return self.gold >= self.cav_price

    def reset_armies(self):
        '''
        Resets the armies moved flag when player's turn ends.
        '''
        for army in self.armies:
            army.moved = False
            army.recover_morale()
        self.end_turn = False

    def is_active(self):
        return self.active

    def income(self):
        income = 0
        for ter in self.territories:
            income = income + ter.get_income()
        return income

    def ally(self, other):
        if other not in self.enemies:
            self.allies.add(other)
            other.allies.add(self)

    def break_ally(self, other):
        if other in self.allies:
            self.allies.remove(other)
            other.allies.remove(self)

    def declare_war(self, other):
        if other not in self.allies:
            self.enemies.add(other)
            other.enemies.add(self)

    def can_call_to_arms(self, other):
        can_call = other in self.allies
        for enemy in self.enemies:
            if enemy in other.allies or enemy in other.enemies:
                can_call = False
        can_call = can_call and len(self.enemies) > 0
        return can_call

    def upgr_cav(self):
        '''
        Upgrades player's cavlary units in all armies.
        '''
        attack = self.cav_stats[0] + 1
        defence = self.cav_stats[1] + 1
        morale = self.cav_stats[3] + 1
        self.cav_stats = (attack, defence, 1000, morale)
        for army in self.armies:
            army.troops[1].attack = attack
            army.troops[1].defence = defence
            army.troops[1].morale = morale
        self.gold = self.gold - self.cav_price * 2
        self.cav_price = self.cav_price + self.cav_price // 3

    def upgr_inf(self):
        '''
        Upgrades player's infantry units in all armies.
        '''
        attack = self.inf_stats[0] + 1
        defence = self.inf_stats[1] + 1
        morale = self.inf_stats[3] + 1
        self.inf_stats = (attack, defence, 1000, morale)
        for army in self.armies:
            army.troops[0].attack = attack
            army.troops[0].defence = defence
            army.troops[0].morale = morale
        self.gold = self.gold - self.inf_price * 2
        self.inf_price = self.inf_price + self.inf_price // 3

    def can_upgr_cav(self):
        return self.gold >= self.cav_price * 2

    def can_upgr_inf(self):
        return self.gold >= self.inf_price * 2

    def is_eliminated(self):
        return self.armies == [] and self.territories == []


class Offer:
    '''
    Offer class for offers between players during the game. Has methods for
    alliance, peace and call to arms. Returns a message to the sender if
    the receiver of the offer accepts if.
    '''
    def __init__(self, type, receiver, sender, gold=0, msg=None):
        self.type = type
        self.sender = sender
        self.gold = gold
        self.receiver = receiver
        self.msg = msg

    def accept(self):
        if self.type == "alliance":
            self.accept_alliance()
        elif self.type == "peace":
            self.accept_peace()
        elif self.type == "call to arms":
            self.accept_call_to_arms()

    def accept_alliance(self):
        self.receiver.ally(self.sender)
        msg = " accepted your alliance offer"
        self.return_message(msg, self.sender)
        self.pay_gold()

    def accept_peace(self):
        self.receiver.enemies.remove(self.sender)
        self.sender.enemies.remove(self.receiver)
        msg = " accepted your peace offer"
        self.return_message(msg, self.sender)
        self.pay_gold()

    def accept_call_to_arms(self):
        msg = " joined the war against you"
        for enemy in self.sender.enemies:
            self.receiver.declare_war(enemy)
            self.return_message(msg, enemy)
        msg = " accepted your call to arms offer"
        self.return_message(msg, self.sender)
        self.pay_gold()

    def pay_gold(self):
        self.receiver.gold = self.receiver.gold + self.gold
        self.sender.gold = self.sender.gold - self.gold

    def return_message(self, msg, target):
        offer = Offer("message", target, self.receiver, 0, msg)
        target.offers.append(offer)
