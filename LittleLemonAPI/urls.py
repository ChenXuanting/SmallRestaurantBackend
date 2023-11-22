from django.urls import path
from .views import (UserMe, MenuItemList, 
                    SingleMenuItemView, GroupUsersView,
                    SingleGroupUserView, CartAPIView,
                    CustomerOrderListCreateView, SingleCustomerOrderView)

urlpatterns = [
    path('users/users/me', UserMe.as_view(), name='me'),
    path('menu-items', MenuItemList.as_view(), name='menu-items'),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view(), name='menu-item-detail'),
    path('groups/<str:group_name>/users', GroupUsersView.as_view(), name='managers'),
    path('groups/<str:group_name>/users/<int:pk>', SingleGroupUserView.as_view()),
    path('cart/menu-items', CartAPIView.as_view()),
    path('orders', CustomerOrderListCreateView.as_view()),
    path('orders/<int:pk>', SingleCustomerOrderView.as_view()),
]