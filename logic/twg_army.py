class Unit:
    '''
    Base abstract class Unit must be inherited by all units.
    '''

    def __init__(self, att, defence, ammount, morale, maint):
        self.attack = att
        self.defence = defence
        self.ammount = ammount
        self.morale = morale
        self.maint = maint

    def receive_damage(self, damage):
        '''
        Unit receives damage and returns damage left if there is such.
        '''
        units_left = self.ammount - int(damage / self.defence)
        if units_left <= 0:
            self.ammount = 0
            return abs(units_left * self.defence)
        elif self.ammount == units_left:
            return damage
        else:
            self.ammount = units_left
            return 0

    def get_health(self):
        return self.ammount * self.defence


class Infantry(Unit):
    def __init__(self, att=1, defence=5, ammount=1000, morale=5, maint=0.1):
        super().__init__(att, defence, ammount, morale, maint)


class Cavlary(Unit):
    def __init__(self, att=2, defence=2, ammount=1000, morale=5, maint=0.2):
        super().__init__(att, defence, ammount, morale, maint)


class Army:
    def __init__(self, inf, cav, pos_x, pos_y, owner, moved=False):
        self.troops = (inf, cav)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.moved = moved
        self.owner = owner
        self.morale = self.get_max_morale()

    def fight(self, other, territory):
        '''
        Main method for fighting with another army. Territory is the
        territory where the armies fight. The fight continues until
        one of the armies cannot fight anymore aka is defeated.
        '''
        if self.owner in other.owner.allies or self.owner is other.owner:
            return None
        duration = 0
        while self.can_fight() and other.can_fight():
            damage_done = self.get_damage()
            damage_taken = other.get_damage()
            self.lose_morale(other, damage_taken, duration)
            other.lose_morale(self, damage_done, duration)
            duration = duration + 1
            if damage_done > 0 and damage_taken > 0:
                received = self.troops[0].receive_damage(damage_taken // 2)
                damage_taken = damage_taken // 2 + received
                damage_taken = self.troops[1].receive_damage(damage_taken)
                self.troops[0].receive_damage(damage_taken)
                received = other.troops[0].receive_damage(damage_done // 2)
                damage_done = damage_done // 2 + received
                damage_done = other.troops[1].receive_damage(damage_done)
                other.troops[0].receive_damage(damage_done)
        if self.killed():
            self.owner.armies.remove(self)
        if other.killed():
            other.owner.armies.remove(other)
            territory.lift_siege(other.owner)
            territory.siege(self.owner)
        if self.killed() and other.killed():
            territory.lift_siege(self.owner)
            territory.lift_siege(other.owner)

    def can_fight(self):
        return not self.killed() and self.morale > 0

    def get_damage(self):
        '''
        Returns total damage that the army inflicts at the given moment.
        '''
        inf_damage = self.troops[0].attack * self.troops[0].ammount
        cav_damage = self.troops[1].attack * self.troops[1].ammount
        return inf_damage + cav_damage

    def get_ammount(self):
        return self.troops[0].ammount + self.troops[1].ammount

    def get_max_morale(self):
        cav = 1 if self.troops[1].ammount > 0 else 0
        inf = 1 if self.troops[0].ammount > 0 else 0
        inf_morale = self.troops[0].morale * inf
        cav_morale = self.troops[1].morale * cav
        if inf + cav > 0:
            return round((inf_morale + cav_morale) / (inf + cav), 2)
        else:
            return 0

    def get_maintenance(self):
        '''
        Return tuple with the maintenance cost of the infantry
        and the cavlary of the army.
        '''
        inf_stacks = self.troops[0].ammount // 1000
        cav_stacks = self.troops[1].ammount // 1000
        if self.troops[0].ammount % 1000 > 0:
            inf_stacks = inf_stacks + 1
        if self.troops[1].ammount % 1000 > 0:
            cav_stacks = cav_stacks + 1
        inf_price = round(inf_stacks * self.troops[0].maint, 2)
        cav_price = round(cav_stacks * self.troops[1].maint, 2)
        return (inf_price, cav_price)

    def can_move(self, x, y):
        d_x = abs(self.pos_x - x)
        d_y = abs(self.pos_y - y)
        if self.owner.is_active() and (d_x + d_y) == 1 and not self.moved:
            return True
        else:
            return False

    def move(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.moved = True
        for army in self.owner.armies:
            correct_pos = army.pos_x == self.pos_x and army.pos_y == self.pos_y
            if self is not army and correct_pos:
                self.join(army)

    def lose_morale(self, other, damage, duration_penalty):
        '''
        Method used for morale loss during battle. Other is the other army,
        damage is the damage received and duration penalty is the attrition
        during the long battles.
        '''
        number_advantage = self.get_ammount() / other.get_ammount()
        army_health = self.troops[0].get_health() + self.troops[1].get_health()
        deaths_penalty = (army_health - damage) / army_health
        penalty = (number_advantage + deaths_penalty) / 2
        if duration_penalty > 0:
            penalty = penalty / duration_penalty
        if penalty > 1:
            penalty = 0.9
        self.morale = round(self.morale * penalty, 2)
        if self.morale > self.get_max_morale():
            self.morale = self.get_max_morale()

    def recover_morale(self):
        '''
        Recovery of the morale every turn the army is not fighting.
        Recover rate is 30%.
        '''
        max_morale = self.get_max_morale()
        self.morale = self.morale + max_morale * 3 / 10
        if self.morale > max_morale:
            self.morale = max_morale

    def split(self, left):
        '''
        Splits the army in two, where the ammount of the second army is
        left[0] for infantry and left[1] for cavlary.
        '''
        infA = self.troops[0].ammount - left[0]
        cavA = self.troops[1].ammount - left[1]
        self.troops[0].ammount = left[0]
        self.troops[1].ammount = left[1]
        inf = self.troops[0]
        cav = self.troops[1]
        infantry = Infantry(inf.attack, inf.defence, infA, inf.morale)
        cavlary = Cavlary(cav.attack, cav.defence, cavA, cav.morale)
        army = Army(infantry, cavlary, self.pos_x, self.pos_y, self.owner)
        army.morale = self.morale
        if not army.killed():
            self.owner.armies.append(army)
        if self.killed():
            self.owner.armies.remove(self)
        return army

    def join(self, other):
        '''
        Joins two armies together. Morale of the new army is set to the
        average morale of both. The new army is the current army while
        the other is removed.
        '''
        self_morale = self.get_ammount() * self.morale
        other_morale = other.get_ammount() * other.morale
        other_inf = other.troops[0].ammount
        other_cav = other.troops[1].ammount
        self.troops[0].ammount = self.troops[0].ammount + other_inf
        self.troops[1].ammount = self.troops[1].ammount + other_cav
        morale = self_morale + other_morale
        self.morale = round(morale / self.get_ammount(), 2)
        other.troops[0].ammount = 0
        other.troops[1].ammount = 0
        if other in self.owner.armies:
            self.owner.armies.remove(other)

    def killed(self):
        return self.troops[0].ammount + self.troops[1].ammount <= 0
