# Django Backend for Local Restaurants

This project provides a fully functional API for local restaurants, enabling developers to build comprehensive web and mobile applications. It supports user-specific roles and capabilities, facilitating a wide range of operations from menu management to order processing and role-based access control.

## Motivation

This API project serves as the capstone project for the Coursera course "APIs" offered by Meta.

## API Endpoints

### User Registration and Token Generation

| Endpoint                | Role                            | Method | Purpose                                                            |
|-------------------------|---------------------------------|--------|--------------------------------------------------------------------|
| `/api/users`            | No role required                | POST   | Creates a new user with name, email, and password                  |
| `/api/users/users/me/`  | Anyone with a valid user token  | GET    | Displays only the current user                                     |
| `/token/login/`         | Anyone with a valid username and password | POST   | Generates access tokens for other API calls                        |

### Menu Items Endpoints

| Endpoint                    | Role                   | Method                | Purpose                                     |
|-----------------------------|------------------------|-----------------------|---------------------------------------------|
| `/api/menu-items`           | Customer, delivery crew| GET                   | Lists all menu items. Returns a 200 – Ok HTTP status code |
| `/api/menu-items`           | Customer, delivery crew| POST, PUT, PATCH, DELETE | Denies access and returns 403 – Unauthorized HTTP status code |
| `/api/menu-items/{menuItem}`| Customer, delivery crew| GET                   | Lists single menu item                      |
| `/api/menu-items/{menuItem}`| Customer, delivery crew| POST, PUT, PATCH, DELETE | Returns 403 - Unauthorized |
| `/api/menu-items`           | Manager                | GET                   | Lists all menu items                        |
| `/api/menu-items`           | Manager                | POST                  | Creates a new menu item and returns 201 - Created |
| `/api/menu-items/{menuItem}`| Manager                | GET                   | Lists single menu item                      |
| `/api/menu-items/{menuItem}`| Manager                | PUT, PATCH            | Updates single menu item                    |
| `/api/menu-items/{menuItem}`| Manager                | DELETE                | Deletes menu item                           |

### User Group Management Endpoints

| Endpoint                                   | Role    | Method | Purpose                                            |
|--------------------------------------------|---------|--------|----------------------------------------------------|
| `/api/groups/manager/users`                | Manager | GET    | Returns all managers                               |
| `/api/groups/manager/users`                | Manager | POST   | Assigns the user in the payload to the manager group and returns 201-Created |
| `/api/groups/manager/users/{userId}`       | Manager | DELETE | Removes this particular user from the manager group and returns 200 – Success. Returns 404 – Not found if the user is not found |
| `/api/groups/delivery-crew/users`          | Manager | GET    | Returns all delivery crew                          |
| `/api/groups/delivery-crew/users`          | Manager | POST   | Assigns the user in the payload to the delivery crew group and returns 201-Created |
| `/api/groups/delivery-crew/users/{userId}` | Manager | DELETE | Removes this user from the delivery crew group and returns 200 – Success. Returns 404 – Not found if the user is not found |

### Cart Management Endpoints

| Endpoint                     | Role     | Method | Purpose                                          |
|------------------------------|----------|--------|--------------------------------------------------|
| `/api/cart/menu-items`       | Customer | GET    | Returns current items in the cart for the current user token |
| `/api/cart/menu-items`       | Customer | POST   | Adds the menu item to the cart. Sets the authenticated user as the user id for these cart items |
| `/api/cart/menu-items`       | Customer | DELETE | Deletes all menu items created by the current user token |

### Order Management Endpoints

| Endpoint               | Role          | Method   | Purpose                                                                 |
|------------------------|---------------|----------|-------------------------------------------------------------------------|
| `/api/orders`          | Customer      | GET      | Returns all orders with order items created by this user                |
| `/api/orders`          | Customer      | POST     | Creates a new order item for the current user. Deletes all items from the cart for this user after adding to order |
| `/api/orders/{orderId}`| Customer      | GET      | Returns all items for this order id. Displays an error if not the user’s order |
| `/api/orders`          | Manager       | GET      | Returns all orders with order items by all users                        |
| `/api/orders/{orderId}`| Customer      | PUT, PATCH | Updates the order. Manager can set a delivery crew to this order, update order status |
| `/api/orders/{orderId}`| Manager       | DELETE   | Deletes this order                                                      |
| `/api/orders`          | Delivery crew | GET      | Returns all orders with order items assigned to the delivery crew       |
| `/api/orders/{orderId}`| Delivery crew | PATCH    | Delivery crew can update the order status to 0 or 1. Only allowed updates specified |

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.
