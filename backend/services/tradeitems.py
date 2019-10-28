class Trader:
    def __init__(self, request, survivor_1, survivor_2):
        self.request = request
        self.survivor_1 = survivor_1
        self.survivor_2 = survivor_2
        self.items = ["Water", "Food", "Medication", "Ammunition"]

    def allowed_to_trade_items(self):
        return self.survivor_1.infected == False and self.survivor_2.infected == False

    def count_points(self, index, survivor_key, survivor):
        points_survivor = 0
        for item_key in self.request.data[index][survivor_key]["trade_item"].keys():
            item_qt = survivor.inventory.items.get(name=item_key).quantity
            if item_qt - self.request.data[index][survivor_key]["trade_item"][item_key] >= 0:
                item_points = survivor.inventory.items.get(name=item_key).points
                points_survivor += self.request.data[index][survivor_key]["trade_item"][item_key] * item_points
            else:
                raise Exception("It isn't enough to trade! Permission denied!")
        return points_survivor

    def trade_items(self, data, survivor_key, survivor_1, survivor_2):
        for trade_item in data[survivor_key]["trade_item"].keys():
            for item in self.items:
                if trade_item == item:
                    trade_sur_1 = survivor_1.inventory.items.get(name=item)
                    trade_sur_1.quantity -= data[survivor_key]["trade_item"][item]
                    trade_sur_1.save()
                    trade_sur_2 = survivor_2.inventory.items.get(name=item)
                    trade_sur_2.quantity += data[survivor_key]["trade_item"][item]
                    trade_sur_2.save()

    def perform(self):
        if self.allowed_to_trade_items():
            points_survivor_1 = self.count_points(0, "survivor_1", self.survivor_1)
            points_survivor_2 = self.count_points(1, "survivor_2", self.survivor_2)
            if points_survivor_1 == points_survivor_2:
                for data in self.request.data:
                    if data["id"] == self.survivor_1.id:
                        self.trade_items(data, "survivor_1", self.survivor_1, self.survivor_2)
                    else:
                        self.trade_items(data, "survivor_2", self.survivor_2, self.survivor_1)
                return True
            else:
                raise Exception("You must have the same amount of points to trade! Permission denied!")
