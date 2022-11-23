[![License](https://img.shields.io/badge/License-BSD_3--Clause-yellow.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![wakatime](https://wakatime.com/badge/user/54ad05ce-f39b-4fa3-9f2a-6fe4b1c53ba4/project/f72c5f1f-a6f5-439e-ad6e-92ef9ccaaf6d.svg)](https://wakatime.com/badge/user/54ad05ce-f39b-4fa3-9f2a-6fe4b1c53ba4/project/f72c5f1f-a6f5-439e-ad6e-92ef9ccaaf6d)
[![tokei](https://tokei.rs/b1/github/mbrav/client-transactions-api?category=lines)](https://tokei.rs/b1/github/mbrav/client-transactions-api)

# client-transactions-api

A fault tolerant, asynchronous funds transaction API

## Summary

This is a funds transaction API written using the FastAPI framework and uses Postres DB. It manages user authorizations and keeps track of their funds and balances is a simple SQL table. Users can view their balances (`GET /api/balances/my`) and post transactions (`POST /api/balances`) to update their balances.

The main feature of this API is that it can still carry out transactions once the DB goes down. While the DB is offline down, the user can still carry out transactions, while also being declined, in case there not enough funds.

Along with these features, the service also uses the following stack.

- Integration with [SQLAlchemy's](https://www.sqlalchemy.org/) new ORM statement paradigm to be implemented in [v2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html);
- Asynchronous PostgreSQL database via [asyncpg](https://github.com/MagicStack/asyncpg), one of the fastest and high performant Database Client Libraries for python/asyncio;
- A token authorization system using the [argon2 password hashing algorithm](https://github.com/P-H-C/phc-winner-argon2), the password-hashing function that won the [Password Hashing Competition (PHC)](https://www.password-hashing.net/).

## Installation

The API can be spun up with docker-compose and interacted with using FastAPI's integrated Swagger UI the following way:

```bash
git clone https://github.com/mbrav/client-transactions-api.git
cd client-transactions-api
```

```bash
docker-compose up
```

After that, the Swagger UI will be available at: <http://0.0.0.0:8000/docs>

## Offline Transactions Feature Demo

⚠️ Before the offline transaction feature can work, the following steps must be satisfied **before offline transactions can work without DB**:

1. The API was started with DB in online state;
2. A user should have authenticated during the API's runtime (i.e after it started);
3. A user should have used the `GET /api/balances/my` or `POST /api/balances` method **at least once** during the API's runtime

These are steps are necessary so that the API can cache the necessary info to carry out offline transactions after the DB goes offline.

### 1. Starting up services separately

Make sure to stop all client-transactions-api instances, then start DB in one terminal window:

```bash
docker-compose up cta-db
```

Then start the API in a second window:

```bash
docker-compose up cta-api
```

### 2. Register User

First, to do a `POST /api/auth/register` ([Swagger Docs](http://0.0.0.0:8000/docs#/Auth/register_user_api_auth_register_post)) request:

Request:

```json
{
  "username": "user",
  "password": "password"
}
```

Response 201:

```json
{
  "username": "user"
}
```

### 3. Login User

Now go to Swagger UI and click "Authorize form". This will save an OAuth cookie in your browser until you reload the window.

Also note the id of your user with `GET /api/users/me` ([Swagger Docs](http://0.0.0.0:8000/docs#/Users/user_info_api_users_me_get)):

Response 200:

```json
{
  "username": "user",
  "password": null,
  "is_admin": false,
  "is_active": true,
  "id": "2"
}
```

If you get a Response 401, make sure to follow [step 2](#2-register-user) with SwaggerUI:

```json
{
  "detail": "Not authenticated"
}
```

### 4. See your balance

Check your balance with the `GET /api/balances/my` ([Swagger Docs](http://0.0.0.0:8000/docs#/Balances/balance_get_api_balances_my_get)) endpoint:

Response 200:

```json
{
  "user_id": 2,
  "value": 0,
  "created_at": "2100-01-01T00:15:00.433723",
  "updated_at": null,
  "id": 1
}
```

### 5. Make a transaction

To add a transaction, do request to `POST /api/balances` ([Swagger Docs](http://0.0.0.0:8000/docs#/Balances/balance_post_api_balances_post)) endpoint where `value` is the transaction you want to make (can be neagative as well):

Request:

```json
{
  "user_id": 2,
  "value": 420.69
}
```

Response 201:

```json
{
  "user_id": 2,
  "value": 420.69,
  "created_at": "2100-01-01T10:23:03.433723",
  "updated_at": "2100-01-01T10:26:48.021738",
  "id": 1
}
```

If you make a transaction with not enoughs funds, you get a 402 error:

Request:

```json
{
  "user_id": 2,
  "value": -12312.17
}
```

Response 402:

```json
{
  "detail": "Not enough funds (420.69) for a -12312.17 transaction!"
}
```

### 6. Bring DB Offline ⛔

Now switch bring down the DB in the first terminal, or:

```bash
docker stop cta-db
```

### 7. Make offline transactions

Once you do transaction with `POST /api/balances` ([Swagger Docs](http://0.0.0.0:8000/docs#/Balances/balance_post_api_balances_post)) endpoint, you get the following:

Response 201:

```json
{
  "detail": {
    "user_id": 2,
    "value": 420.69,
    "balance": 5889.659999999998,
    "message": "Service partially down. But your transaction is being processed offline and will be processed once online"
  }
}
```

If there not enough funds, the following response will appear:

Response 402:

```json
{
  "detail": {
    "user_id": 2,
    "value": -1420.69,
    "balance": 358.63000000000056,
    "message": "Not enough funds (358.63) for a -1420.69 transaction!"
  }
}
```

### 8. Bring DB back online

Now it is possible to bring up the db back online and all transaction that were done offline by a given user will be synced with the DB:

```bash
docker-compose up cta-db
```

Do a `POST /api/balances` ([Swagger Docs](http://0.0.0.0:8000/docs#/Balances/balance_post_api_balances_post)) request:

Response 201:

```json
{
  "user_id": 2,
  "value": 1779.320000000001,
  "created_at": "2100-01-01T10:48:06.211594",
  "updated_at": "2100-01-01T10:59:08.082144",
  "id": 1
}
```
