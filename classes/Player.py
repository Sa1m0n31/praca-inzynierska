class Player:
    def __init__(self, name, position, country, age, minutes, goals, assists, pens_made, pens_att, shots,
                 shots_on_target, yellow_cards, red_cards, touches, xg, passes, passes_completed,
                 progressive_passes, dribbles, dribbles_completed):
        self.name = name
        self.position = position
        self.country = country
        self.age = age
        self.minutes = minutes
        self.goals = goals
        self.assists = assists
        self.pens_made = pens_made
        self.pens_att = pens_att
        self.shots = shots
        self.shots_on_target = shots_on_target
        self.yellow_cards = yellow_cards
        self.red_cards = red_cards
        self.touches = touches
        self.xg = xg
        self.passes = passes
        self.passes_completed = passes_completed
        self.progressive_passes = progressive_passes
        self.dribbles = dribbles
        self.dribbles_completed = dribbles_completed

    def __str__(self):
        return f'{self.name}, {self.age}, {self.minutes}, {self.goals}'