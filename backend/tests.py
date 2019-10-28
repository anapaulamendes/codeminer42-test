import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import Survivor
from .survivors import SURVIVOR_1_POST, SURVIVOR_2_POST, SURVIVOR_3_POST, \
    SURVIVOR_4_POST, SURVIVOR_ERROR_POST, ZOMBIE_POST

LAST_LOCATION_POST = {
    "latitude": "52.522906000000000000000000000000",
    "longitude": "10.411560000000000000000000000000"
}

TRADE_ITEMS_POST = [
{
    "id": 1,
    "survivor_1": {
        "trade_item": {
            "Water": 1,
            "Medication": 1
        }
    }
},
{
    "id": 2,
    "survivor_2": {
        "trade_item": {
            "Food": 1,
            "Ammunition": 3
        }
    }
}
]

ERROR_TRADE_ITEMS_POST = [
{
    "id": 1,
    "survivor_1": {
        "trade_item": {
            "Water": 1,
            "Medication": 1
        }
    }
},
{
    "id": 2,
    "survivor_2": {
        "trade_item": {
            "Food": 2,
            "Ammunition": 3
        }
    }
}
]


class Test(TestCase):

    def create_survivor(self, SURVIVOR_POST):
        response = self.client.post(
            reverse('survivor_list'),
            data=json.dumps(SURVIVOR_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        survivor = Survivor.objects.get(name=SURVIVOR_POST["name"])
        return survivor


class SurvivorTest(Test):

    def test_create_survivors(self):
        self.create_survivor(SURVIVOR_1_POST)
        self.create_survivor(SURVIVOR_2_POST)
        self.create_survivor(SURVIVOR_3_POST)
        survivors = Survivor.objects.all()
        self.assertEqual(3, survivors.count())
        survivor = survivors.first()
        self.assertEqual("Ana Paula", survivor.name)
        self.assertEqual(22, survivor.age)
        self.assertEqual("F", survivor.gender)
        self.assertEqual(Decimal('51.522906000000000000000000000000'), survivor.last_location.latitude)
        self.assertEqual(Decimal('11.411560000000000000000000000000'), survivor.last_location.longitude)
        self.assertEqual(4, survivor.inventory.items.get(name="Water").points)
        self.assertEqual(10, survivor.inventory.items.get(name="Water").quantity)
        self.assertEqual(3, survivor.inventory.items.get(name="Food").points)
        self.assertEqual(5, survivor.inventory.items.get(name="Food").quantity)
        self.assertEqual(2, survivor.inventory.items.get(name="Medication").points)
        self.assertEqual(8, survivor.inventory.items.get(name="Medication").quantity)
        self.assertEqual(1, survivor.inventory.items.get(name="Ammunition").points)
        self.assertEqual(15, survivor.inventory.items.get(name="Ammunition").quantity)
        self.assertEqual(False, survivor.infected)
        self.assertEqual(0, survivor.reported_infected)

    def test_error_create_survivors(self):
        response = self.client.post(
            reverse('survivor_list'),
            data=json.dumps(SURVIVOR_ERROR_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_error_create_zombie(self):
        with self.assertRaises(Exception):
            self.client.post(
                reverse('survivor_list'),
                data=json.dumps(ZOMBIE_POST),
                content_type='application/json'
            )

    def test_get_all_survivors(self):
        self.create_survivor(SURVIVOR_1_POST)
        self.create_survivor(SURVIVOR_2_POST)
        self.create_survivor(SURVIVOR_3_POST)
        response = self.client.get(reverse('survivor_list'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Ana Paula", response.content.decode())
        self.assertIn("Marcus Vinicius", response.content.decode())
        self.assertIn("Josylene", response.content.decode())

    def test_get_survivor(self):
        survivor = self.create_survivor(SURVIVOR_1_POST)
        response = self.client.get(reverse('survivor_detail', kwargs={"pk": survivor.id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("Ana Paula", survivor.name)
        self.assertIn("Ana Paula", response.content.decode())

    def test_error_get_survivor_inexistent(self):
        response = self.client.get(reverse('survivor_detail', kwargs={"pk": 1}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class LastLocationTest(Test):

    def test_update_last_location(self):
        survivor = self.create_survivor(SURVIVOR_1_POST)
        self.assertEqual(Decimal('51.522906000000000000000000000000'), survivor.last_location.latitude)
        self.assertEqual(Decimal('11.411560000000000000000000000000'), survivor.last_location.longitude)
        response = self.client.patch(
            reverse('last_location_update', kwargs={"pk": survivor.id}),
            data=json.dumps(LAST_LOCATION_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survivor.refresh_from_db()
        self.assertEqual(Decimal('52.522906000000000000000000000000'), survivor.last_location.latitude)
        self.assertEqual(Decimal('10.411560000000000000000000000000'), survivor.last_location.longitude)

    def test_error_zombie_update_last_location(self):
        survivor = self.create_survivor(SURVIVOR_1_POST)
        survivor.infected = True
        survivor.reported_infected = 3
        survivor.save()
        with self.assertRaises(Exception):
            self.client.patch(
                reverse('last_location_update', kwargs={"pk": survivor.id}),
                data=json.dumps(LAST_LOCATION_POST),
                content_type='application/json'
            )


class ReportInfectedTest(Test):

    def test_report_infected(self):
        reporter_1 = self.create_survivor(SURVIVOR_1_POST)
        reporter_2 = self.create_survivor(SURVIVOR_2_POST)
        reporter_3 = self.create_survivor(SURVIVOR_3_POST)
        reported = self.create_survivor(SURVIVOR_4_POST)
        SURVIVOR_4_POST["infected"] = True
        response = self.client.patch(
            reverse('report_infected', kwargs={"pk_reporter": reporter_1.id, "pk_reported": reported.id}),
            data=json.dumps(SURVIVOR_4_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reported.refresh_from_db()
        self.assertEqual(False, reported.infected)
        self.assertEqual(1, reported.reported_infected)
        response = self.client.patch(
            reverse('report_infected', kwargs={"pk_reporter": reporter_2.id, "pk_reported": reported.id}),
            data=json.dumps(SURVIVOR_4_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reported.refresh_from_db()
        self.assertEqual(False, reported.infected)
        self.assertEqual(2, reported.reported_infected)
        response = self.client.patch(
            reverse('report_infected', kwargs={"pk_reporter": reporter_3.id, "pk_reported": reported.id}),
            data=json.dumps(SURVIVOR_4_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reported.refresh_from_db()
        self.assertEqual(True, reported.infected)
        self.assertEqual(3, reported.reported_infected)
        SURVIVOR_4_POST["infected"] = False

    def test_error_zombie_report_infected(self):
        reporter = self.create_survivor(SURVIVOR_1_POST)
        reporter.infected = True
        reporter.reported_infected = 3
        reporter.save()
        reported = self.create_survivor(SURVIVOR_2_POST)
        with self.assertRaises(Exception):
            self.client.patch(
                reverse('report_infected', kwargs={"pk_reporter": reporter.id, "pk_reported": reported.id}),
                data=json.dumps(SURVIVOR_2_POST),
                content_type='application/json'
            )


class TradeItemsTest(Test):

    def test_trade_items(self):
        survivor_1 = self.create_survivor(SURVIVOR_1_POST)
        survivor_2 = self.create_survivor(SURVIVOR_2_POST)
        self.assertEqual(10, survivor_1.inventory.items.get(name="Water").quantity)
        self.assertEqual(5, survivor_1.inventory.items.get(name="Food").quantity)
        self.assertEqual(8, survivor_1.inventory.items.get(name="Medication").quantity)
        self.assertEqual(15, survivor_1.inventory.items.get(name="Ammunition").quantity)
        self.assertEqual(5, survivor_2.inventory.items.get(name="Water").quantity)
        self.assertEqual(10, survivor_2.inventory.items.get(name="Food").quantity)
        self.assertEqual(6, survivor_2.inventory.items.get(name="Medication").quantity)
        self.assertEqual(20, survivor_2.inventory.items.get(name="Ammunition").quantity)
        response = self.client.patch(
            reverse('trade_items', kwargs={"pk_sur_1": survivor_1.id, "pk_sur_2": survivor_2.id}),
            data=json.dumps(TRADE_ITEMS_POST),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survivor_1.refresh_from_db()
        survivor_2.refresh_from_db()
        self.assertEqual(9, survivor_1.inventory.items.get(name="Water").quantity)
        self.assertEqual(6, survivor_1.inventory.items.get(name="Food").quantity)
        self.assertEqual(7, survivor_1.inventory.items.get(name="Medication").quantity)
        self.assertEqual(18, survivor_1.inventory.items.get(name="Ammunition").quantity)
        self.assertEqual(6, survivor_2.inventory.items.get(name="Water").quantity)
        self.assertEqual(9, survivor_2.inventory.items.get(name="Food").quantity)
        self.assertEqual(7, survivor_2.inventory.items.get(name="Medication").quantity)
        self.assertEqual(17, survivor_2.inventory.items.get(name="Ammunition").quantity)

    def test_error_zombie_trade_items(self):
        survivor_1 = self.create_survivor(SURVIVOR_1_POST)
        survivor_1.infected = True
        survivor_1.reported_infected = 3
        survivor_1.save()
        survivor_2 = self.create_survivor(SURVIVOR_2_POST)
        with self.assertRaises(Exception):
            self.client.patch(
                reverse('trade_items', kwargs={"pk_sur_1": survivor_1.id, "pk_sur_2": survivor_2.id}),
                data=json.dumps(TRADE_ITEMS_POST),
                content_type='application/json'
            )

    def test_error_miss_item_trade_items(self):
        survivor_1 = self.create_survivor(SURVIVOR_1_POST)
        survivor_2 = self.create_survivor(SURVIVOR_4_POST)
        with self.assertRaises(Exception):
            self.client.patch(
                reverse('trade_items', kwargs={"pk_sur_1": survivor_1.id, "pk_sur_2": survivor_2.id}),
                data=json.dumps(TRADE_ITEMS_POST),
                content_type='application/json'
            )

    def test_error_diff_points_trade_items(self):
        survivor_1 = self.create_survivor(SURVIVOR_1_POST)
        survivor_2 = self.create_survivor(SURVIVOR_2_POST)
        with self.assertRaises(Exception):
            self.client.patch(
                reverse('trade_items', kwargs={"pk_sur_1": survivor_1.id, "pk_sur_2": survivor_2.id}),
                data=json.dumps(ERROR_TRADE_ITEMS_POST),
                content_type='application/json'
            )


class GetReportsTest(Test):

    def test_get_reports(self):
        self.create_survivor(SURVIVOR_1_POST)
        self.create_survivor(SURVIVOR_2_POST)
        self.create_survivor(SURVIVOR_3_POST)
        survivor_infected = self.create_survivor(SURVIVOR_4_POST)
        survivor_infected.infected = True
        survivor_infected.save()
        response = self.client.get(reverse('reports'), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('"per_infected":"25.000000000000000000000000000000"', response.content.decode())
        self.assertIn('"per_not_infected":"75.000000000000000000000000000000"', response.content.decode())
        self.assertIn('"average_water":"6.666666666666667000000000000000"', response.content.decode())
        self.assertIn('"average_food":"10.000000000000000000000000000000"', response.content.decode())
        self.assertIn('"average_medication":"8.000000000000000000000000000000"', response.content.decode())
        self.assertIn('"average_ammunition":"20.000000000000000000000000000000"', response.content.decode())
        self.assertIn('"lost_points":3', response.content.decode())
