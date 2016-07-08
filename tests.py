import unittest
from logic import *


class TestPlayer(unittest.TestCase):
    def test_hire(self):
        player = Player("test", (255, 255, 0))
        gold = player.gold
        player.hire_inf(1, 1)
        self.assertTrue(player.can_hire_inf())
        self.assertTrue(player.can_hire_cav())
        self.assertNotEqual(gold, player.gold)
        self.assertNotEqual([], player.armies)
        maint = player.get_armies_maint()
        self.assertLess(0, maint[0])
        self.assertEqual(0, maint[1])
        armies = len(player.armies)
        player.hire_cav(1, 2)
        self.assertLess(armies, len(player.armies))

    def test_income(self):
        player = Player("test", (0, 0, 0))
        self.assertEqual(0, player.income())
        player.territories.append(Territory(1, 1, Buildings(), player))
        player.armies.append(Army(Infantry(), Cavlary(), 1, 1, player))
        self.assertLess(0, player.income())
        gold = player.gold
        player.pay_maintenance()
        self.assertLess(player.gold, gold)
        gold = player.gold
        player.get_income()
        self.assertLess(gold, player.gold)

    def test_ally(self):
        player1 = Player("one", (0, 255, 0))
        player2 = Player("two", (255, 0, 0))
        player1.ally(player2)
        self.assertTrue(player1 in player2.allies)
        self.assertTrue(player2 in player1.allies)
        player1.break_ally(player2)
        self.assertFalse(player1 in player2.allies)
        self.assertFalse(player2 in player1.allies)

    def test_war(self):
        player1 = Player("one", (0, 255, 0))
        player2 = Player("two", (255, 0, 0))
        player1.declare_war(player2)
        self.assertTrue(player1 in player2.enemies)
        self.assertTrue(player2 in player1.enemies)
        player3 = Player("3", (0, 15, 33))
        self.assertFalse(player1.can_call_to_arms(player3))
        player1.ally(player3)
        self.assertTrue(player1.can_call_to_arms(player3))

    def test_upgrade_units(self):
        player = Player("player", (0, 0, 0))
        player.armies.append(Army(Infantry(), Cavlary(), 1, 1, player))
        inf = player.inf_stats
        cav = player.cav_stats
        self.assertTrue(player.can_upgr_inf())
        self.assertTrue(player.can_upgr_cav())
        player.upgr_inf()
        player.upgr_cav()
        for army in player.armies:
            attI = army.troops[0].attack
            attC = army.troops[1].attack
            self.assertEqual(attI, player.inf_stats[0])
            self.assertEqual(attC, player.cav_stats[0])

    def test_offers(self):
        player1 = Player("one", (0, 255, 0))
        player2 = Player("two", (255, 0, 0))
        player3 = Player("3", (0, 11, 13))
        player1.declare_war(player3)
        ally = Offer("alliance", player1, player2, 10)
        ally.accept()
        self.assertTrue(player1 in player2.allies)
        self.assertNotEqual(player2.gold, player1.gold)
        call = Offer("call to arms", player2, player1)
        call.accept()
        self.assertTrue(player3 in player2.enemies)
        peace = Offer("peace", player3, player2)
        peace.accept()
        self.assertFalse(player2 in player3.enemies)


class TestArmy(unittest.TestCase):
    def test_fight(self):
        player1 = Player("one", (0, 255, 0))
        player2 = Player("two", (255, 0, 0))
        army1 = Army(Infantry(), Cavlary(), 1, 1, player1)
        army2 = Army(Infantry(), Cavlary(), 1, 1, player2)
        ammount = army1.get_ammount()
        morale = army1.morale
        ter = Territory(1, 1, Buildings())
        army1.fight(army2, ter)
        self.assertLess(army1.morale, morale)
        self.assertLess(army1.get_ammount(), ammount)
        morale = army2.morale
        army2.recover_morale()
        self.assertLess(morale, army2.morale)

    def test_split_join(self):
        player = Player("player", (0, 255, 0))
        army1 = Army(Infantry(), Cavlary(), 1, 1, player)
        cnt = len(player.armies)
        ammount = army1.get_ammount()
        army2 = army1.split((ammount // 4, ammount // 4))
        self.assertEqual(army1.get_ammount(), army2.get_ammount())
        self.assertLess(cnt, len(player.armies))
        cnt = len(player.armies)
        army1.join(army2)
        self.assertLess(len(player.armies), cnt)
        self.assertEqual(ammount, army1.get_ammount())

    def test_move(self):
        player = Player("player", (0, 255, 0))
        player.active = True
        army = Army(Infantry(), Cavlary(), 1, 1, player)
        player.armies.append(army)
        self.assertTrue(army.can_move(1, 2))
        army.move(1, 2)
        self.assertTrue(army.moved)
        player.reset_armies()
        self.assertFalse(army.moved)


class TestGame(unittest.TestCase):
    def test(self):
        game = Game(2)
        game.players[0].end_turn = True
        game.players[1].end_turn = True
        game.start(2)
        self.assertTrue(len(game.players[1].armies) > 0)
        self.assertTrue(len(game.players[1].territories) > 0)
        self.assertLess(game.turn, 3)


if __name__ == "__main__":
    unittest.main()