class FlagInfected():

    def report_infected(self, request, reporter, reported):
        if reporter.infected == False:
            if reported.reported_infected < 2:
                if request.data["infected"] == True:
                    data = {
                        "infected": False,
                        "reported_infected": reported.reported_infected + 1
                    }
                else:
                    raise Exception("Flag as infected!")
            else:
                if request.data["infected"] == True:
                    data = {
                        "infected": True,
                        "reported_infected": reported.reported_infected + 1
                    }
                else:
                    raise Exception("Flag as infected!")
            return data
        else:
            raise Exception("Zombie invasion! Permission denied!")
