class Trader():

    def trade_items(self, request, survivor_1, survivor_2):
        items = ["Water", "Food", "Medication", "Ammunition"]
        points_survivor_1 = 0
        points_survivor_2 = 0
        if survivor_1.infected == False and survivor_2.infected == False:
            for item_key in request.data[0]["survivor_1"]["trade_item"].keys():
                item_qt = survivor_1.inventory.items.get(name=item_key).quantity
                if item_qt - request.data[0]["survivor_1"]["trade_item"][item_key] >= 0:
                    item_points = survivor_1.inventory.items.get(name=item_key).points
                    points_survivor_1 += request.data[0]["survivor_1"]["trade_item"][item_key] * item_points
                else:
                    raise Exception("It isn't enough to trade! Permission denied!")
            for item_key in request.data[1]["survivor_2"]["trade_item"].keys():
                item_qt = survivor_2.inventory.items.get(name=item_key).quantity
                if item_qt - request.data[1]["survivor_2"]["trade_item"][item_key] >= 0:
                    item_points = survivor_2.inventory.items.get(name=item_key).points
                    points_survivor_2 += request.data[1]["survivor_2"]["trade_item"][item_key] * item_points
                else:
                    raise Exception("It isn't enough to trade! Permission denied!")
            if points_survivor_1 == points_survivor_2:
                for data in request.data:
                    if data["id"] == survivor_1.id:
                        for trade_item in data["survivor_1"]["trade_item"].keys():
                            for item in items:
                                if trade_item == item:
                                    trade_sur_1 = survivor_1.inventory.items.get(name=item)
                                    trade_sur_1.quantity -= data["survivor_1"]["trade_item"][item]
                                    trade_sur_1.save()
                                    trade_sur_2 = survivor_2.inventory.items.get(name=item)
                                    trade_sur_2.quantity += data["survivor_1"]["trade_item"][item]
                                    trade_sur_2.save()
                    else:
                        for trade_item in data["survivor_2"]["trade_item"].keys():
                            for item in items:
                                if trade_item == item:
                                    trade_sur_2 = survivor_2.inventory.items.get(name=item)
                                    trade_sur_2.quantity -= data["survivor_2"]["trade_item"][item]
                                    trade_sur_2.save()
                                    trade_sur_1 = survivor_1.inventory.items.get(name=item)
                                    trade_sur_1.quantity += data["survivor_2"]["trade_item"][item]
                                    trade_sur_1.save()
                return True
            else:
                raise Exception("You must have the same amount of points to trade! Permission denied!")
