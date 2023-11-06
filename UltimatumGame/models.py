from otree.api import models, BasePlayer


class Player1(BasePlayer):
    endowment = models.CurrencyField(initial=200)
    sent_amount = models.CurrencyField(min=0, max=200)


class Player2(BasePlayer):
    received_amount = models.CurrencyField()


class Player3(BasePlayer):
    punish_decision = models.BooleanField()

    def set_payoffs(self):
        p1 = self.get_others_in_group()[0]  # Player1
        p2 = self.get_others_in_group()[1]  # Player2

        if self.punish_decision:
            p1.payoff = 0
            p2.payoff = 0
        else:
            p1.payoff = p1.endowment - p1.sent_amount
            p2.payoff = p1.sent_amount
