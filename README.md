# ZSSN (Zombie Survival Social Network)

A system to share resources between non-infected humans on a zombie apocalyptic scenario.

## []()Getting Started

### []()Prerequisites

```
Python3
Pip
Python virtualenv
Django
Django Rest Framework
```

Activate your virtual environment before proceeding with the installation.

### []()Installing

To install the requirements:

```
make setup
```
or
```
pip install -r requirements.txt
```

To do database migrations:

```
make migrate
```

## []()Running the tests

To run the tests:

```
make test
```

## []()Running the Rest API

To run the Rest API:

```
make run
```
or
```
./manage.py runserver
```

> Access in: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## []()Built With

-   [Django Rest Framework]([https://www.django-rest-framework.org/](https://www.django-rest-framework.org/))  - The web framework used

# REST API

The REST API to the ZSSN is described below.

## All API endpoints:

 - GET: `/` - API root
 - GET/POST: `/survivors` - List all survivors / Add survivors
 - GET: `/survivors/<id>` - Get survivor
 - GET/PUT: `/survivors/<id>/last-location` - Update survivor location
 - GET/PATCH: `/survivors/<id-reporter>/report-infected/<id-reported>` - Flag survivor as infected
 - GET/PATCH: `/survivors/<id-survivor-1>/trade-items/<id-survivor-2>` - Trade items between non infected survivors
 - GET: `/survivors/reports` - Get reports

## How to use API endpoints

### List all survivors / Add survivors

- GET/POST: `/survivors`

URL example:

> [http://127.0.0.1:8000/survivors/](http://127.0.0.1:8000/survivors/)

JSON example:

```
{
   "name": "Ana Paula",
   "age": 22,
   "gender": "F",
   "last_location": {
      "latitude": "51.522906000000000000000000000000",
      "longitude": "11.411560000000000000000000000000"
   },
   "inventory": {
      "items": [
      {
        "name": "Water",
        "points": 4,
        "quantity": 10
      },
      {
        "name": "Food",
        "points": 3,
        "quantity": 5
      },
      {
        "name": "Medication",
        "points": 2,
        "quantity": 8
      },
      {
        "name": "Ammunition",
        "points": 1,
        "quantity": 15
      }
      ]
   },
   "infected": false,
   "reported_infected": 0
}
```

Observations:

> It's forbidden to register zombies!


### Get survivor

 - GET: `/survivors/<id>`
	 - `<id> is the identifier of the survivor.`

URL example:

> [http://127.0.0.1:8000/survivors/1/](http://127.0.0.1:8000/survivors/1/)


### Update survivor location

 - GET/PUT: `/survivors/<id>/last-location`
	 - `<id> is the identifier of the survivor.`

URL example:

> [http://127.0.0.1:8000/survivors/1/last-location](http://127.0.0.1:8000/survivors/1/last-location)

JSON example:

```
{
   "last_location": {
      "latitude": "52.522906000000000000000000000000",
      "longitude": "10.411560000000000000000000000000"
   }
}
```

### Flag survivor as infected

 - GET/PATCH: `/survivors/<id-reporter>/report-infected/<id-reported>`
	 -  `<id-reporter> is the identifier of the reporter`
	 -  `<id-reported> is the identifier of the reported`

URL example:

> [http://127.0.0.1:8000/survivors/1/report-infected/2](http://127.0.0.1:8000/survivors/1/report-infected/3)

JSON example:

```
{
   "name": "Ana Paula",
   "age": 22,
   "gender": "F",
   "last_location": {
      "latitude": "52.522906000000000000000000000000",
      "longitude": "10.411560000000000000000000000000"
   },
   "inventory": {
      "items": [
      {
        "name": "Water",
        "points": 4,
        "quantity": 10
      },
      {
        "name": "Food",
        "points": 3,
        "quantity": 5
      },
      {
        "name": "Medication",
        "points": 2,
        "quantity": 8
      },
      {
        "name": "Ammunition",
        "points": 1,
        "quantity": 15
      }
      ]
   },
   "infected": true,
   "reported_infected": 0
}
```

Observations:

> It'll have **"infected": true** in **GET** when **reported_infected >= 3**.


### Trade items between non infected survivors

 - GET/PATCH: `/survivors/<id-survivor-1>/trade-items/<id-survivor-2>`
	-  `<id-survivor-1> is the identifier of the survivor 1`
	-  `<id-survivor-2> is the identifier of the survivor 2`

 URL example:

> [http://127.0.0.1:8000/survivors/1/trade-items/3](http://127.0.0.1:8000/survivors/1/trade-items/3)

JSON example:

```
[
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
   "id": 3,
   "survivor_2": {
      "trade_item": {
         "Food": 1,
         "Ammunition": 3
      }      
   }
  }
]
```

Observations:

> It's important to keep in order according to the exchange of items you
> want between them.


### Get reports

 - GET: `/survivors/reports`

URL example:

> [http://127.0.0.1:8000/survivors/reports](http://127.0.0.1:8000/survivors/reports)

Observations:

> The API will offer the following reports:
>
> 1.  Percentage of infected survivors.
> 2.  Percentage of non-infected survivors.
> 3.  Average amount of each kind of resource by survivor (e.g. 5 waters per survivor)
> 4.  Points lost because of infected survivor.

## Authors

-   [**Ana Paula Mendes**]([https://anapaulamendes.github.io/](https://anapaulamendes.github.io/))
