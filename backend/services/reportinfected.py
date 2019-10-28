class FlagInfected:
    def __init__(self, infected, reporter, reported):
        self.infected = infected
        self.reporter = reporter
        self.reported = reported

    def allowed_to_report(self):
        return self.reporter.infected == False

    def reported_not_infected(self):
        return self.reported.reported_infected < 2

    def perform(self):
        if not self.allowed_to_report():
            raise Exception("Zombie invasion! Permission denied!")

        if self.reported_not_infected():
            if self.infected:
                data = {
                    "infected": False,
                    "reported_infected": self.reported.reported_infected + 1
                }
            else:
                raise Exception("Flag as infected!")
        else:
            if self.infected:
                data = {
                    "infected": True,
                    "reported_infected": self.reported.reported_infected + 1
                }
            else:
                raise Exception("Flag as infected!")
        return data
