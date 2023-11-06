from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Player1, Player2, Player3


# Page where all players decide the amount to send
class SendAmount(Page):
    form_model = "player"
    form_fields = ["sent_amount"]

    # Display this page for all players
    def is_displayed(self):
        return True

    # Logic to set endowment and enforce sent amount limit for Player 1
    def vars_for_template(self):
        if self.player.id_in_group == 1:
            self.player.endowment = c(200)  # Set the endowment for Player 1
        return {}

    def before_next_page(self):
        if self.player.id_in_group == 1:
            if self.player.sent_amount > self.player.endowment:
                self.player.sent_amount = (
                    self.player.endowment
                )  # Ensure Player 1 cannot send more than their endowment


# Page where Player 2 waits for the amount from Player 1
class WaitForAmount(Page):
    def is_displayed(self):
        return self.player.id_in_group == 2

    def vars_for_template(self):
        sent_amount = self.group.get_player_by_role("Player1").sent_amount
        return {"sent_amount": sent_amount}


# Page where Player 3 decides to punish or not
class PunishOrNot(Page):
    form_model = "player"
    form_fields = ["punish_decision"]

    # Display this page for Player 3 only
    def is_displayed(self):
        return self.player.id_in_group == 3

    # Pass the sent amount to the template for display
    def vars_for_template(self):
        sent_amount = self.group.get_player_by_role("Player1").sent_amount
        return {"sent_amount": sent_amount}

    # Store sent amount in participant vars for use in Results page
    def before_next_page(self):
        for player in self.group.get_players():
            player.participant.vars["sent_amount"] = self.group.get_player_by_role(
                "Player1"
            ).sent_amount


# Page to display results for all players
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


# WaitPage to calculate payoffs after all players make decisions
class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for group in self.subsession.get_groups():
            p1 = group.get_player_by_role("Player1")
            p2 = group.get_player_by_role("Player2")
            p3 = group.get_player_by_role("Player3")

            # Calculate payoffs based on Player 3's decision
            if p3.punish_decision:
                p1.payoff = c(0)
                p2.payoff = c(0)
            else:
                p1.payoff = c(200) - p1.sent_amount
                p2.payoff = p1.sent_amount


# Exit survey page with questions
class ExitSurvey(Page):
    form_model = "player"
    form_fields = ["capital_city", "math_question", "population"]

    def is_displayed(self):
        return self.round_number == 1  # Display only at the end of the game

    # Validate the math question and restrict progression until it's answered correctly
    def math_question_error_message(self, value):
        if value != 29:
            return "Your answer to the math question is incorrect. Please try again."

    # Capital City question as a choice
    def get_form_fields(self):
        return ["capital_city", "math_question", "population"]

    def vars_for_template(self):
        return {
            "capital_city_text": "Q1. What is the capital City of Kenya? (Choose one from the given options)",
            "math_question_text": "Q2. What is 14 + 15? (Input a number)",
            "population_text": "What is the population of Kenya? (Input a number)",
        }


# Define the sequence of pages for the game including the exit survey
page_sequence = [
    SendAmount,
    WaitForAmount,
    PunishOrNot,
    Results,
    ResultsWaitPage,
    ExitSurvey,
]
