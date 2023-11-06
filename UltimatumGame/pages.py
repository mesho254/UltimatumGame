from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Player1, Player2, Player3
from otree.forms import Form


class SendAmount(Page):
    form_model = "player"
    form_fields = ["sent_amount"]

    def is_displayed(self):
        return True

    def vars_for_template(self):
        if self.player.id_in_group == 1:
            player1 = self.player
            player1.endowment = c(200)
            player1.save()
        return {
            "form": Form(),
        }

    def before_next_page(self):
        if self.player.id_in_group == 1:
            if self.player.sent_amount > self.player.endowment:
                self.player.sent_amount = self.player.endowment


class MyPage(Page):
    def is_displayed(self):
        return self.player.id_in_group == 1

    def vars_for_template(self):
        # Your template context data
        return {
            "key1": "value1",
            "key2": "value2",
        }

    def before_next_page(self):
        self.player.payoff = self.player.payoff * 2


class WaitForAmount(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

    def vars_for_template(self):
        sent_amount = self.group.get_player_by_role("Player1").sent_amount
        return {"sent_amount": sent_amount}


class PunishOrNot(Page):
    form_model = "player"
    form_fields = ["punish_decision"]

    def is_displayed(self):
        return self.player.id_in_group == 3

    def vars_for_template(self):
        sent_amount = self.group.get_player_by_role("Player1").sent_amount
        return {"sent_amount": sent_amount}

    def before_next_page(self):
        for player in self.group.get_players():
            player.participant.vars["sent_amount"] = self.group.get_player_by_role(
                "Player1"
            ).sent_amount


class Results(Page):
    def vars_for_template(self):
        p1 = self.group.get_player_by_role("Player1")
        p2 = self.group.get_player_by_role("Player2")
        punish_decision = self.player.punish_decision

        return {
            "sent_amount": self.player.participant.vars["sent_amount"],
            "punish_decision": punish_decision,
            "p1_payoff": p1.payoff,
            "p2_payoff": p2.payoff,
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for group in self.subsession.get_groups():
            p1 = group.get_player_by_role("Player1")
            p2 = group.get_player_by_role("Player2")
            p3 = group.get_player_by_role("Player3")

            if p3.punish_decision:
                p1.payoff = c(0)
                p2.payoff = c(0)
            else:
                p1.payoff = c(200) - p1.sent_amount
                p2.payoff = p1.sent_amount


class ExitSurvey(Page):
    form_model = "player"
    form_fields = ["capital_city", "math_question", "population"]

    def is_displayed(self):
        return self.round_number == 1

    def math_question_error_message(self, value):
        if value != 29:
            return "Your answer to the math question is incorrect. Please try again."

    def get_form_fields(self):
        return ["capital_city", "math_question", "population"]

    def vars_for_template(self):
        return {
            "capital_city_text": "Q1. What is the capital City of Kenya? (Choose one from the given options)",
            "math_question_text": "Q2. What is 14 + 15? (Input a number)",
            "population_text": "What is the population of Kenya? (Input a number)",
        }


page_sequence = [
    MyPage,
    SendAmount,
    WaitForAmount,
    PunishOrNot,
    Results,
    ResultsWaitPage,
    ExitSurvey,
]
