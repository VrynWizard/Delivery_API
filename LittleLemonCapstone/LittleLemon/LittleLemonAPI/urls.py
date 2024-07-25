from django.urls import path, include
from .views import (
    MenuItemList, MenuItemDetail, 
    ManagerUsers, ManagerUserDetail, 
    DeliveryCrewUsers, DeliveryCrewUserDetail, 
    CartMenuItems, CustomerOrderList, CustomerOrderDetail, 
    ManagerOrderList, ManagerOrderDetail, 
    DeliveryCrewOrderList, DeliveryCrewOrderDetail
)

urlpatterns = [
    path('menu-items/', MenuItemList.as_view(), name='menu-items'),
    path('menu-items/<int:pk>/', MenuItemDetail.as_view(), name='menu-item-detail'),
    path('groups/manager/users/', ManagerUsers.as_view(), name='manager-users'),
    path('groups/manager/users/<int:userId>/', ManagerUserDetail.as_view(), name='manager-user-detail'),
    path('groups/delivery-crew/users/', DeliveryCrewUsers.as_view(), name='delivery-crew-users'),
    path('groups/delivery-crew/users/<int:userId>/', DeliveryCrewUserDetail.as_view(), name='delivery-crew-user-detail'),
    path('cart/menu-items/', CartMenuItems.as_view(), name='cart-menu-items'),
    path('orders/', CustomerOrderList.as_view(), name='customer-orders'),
    path('orders/<int:pk>/', CustomerOrderDetail.as_view(), name='customer-order-detail'),
    path('orders/all/', ManagerOrderList.as_view(), name='manager-orders'),  # For Manager
    path('orders/all/<int:pk>/', ManagerOrderDetail.as_view(), name='manager-order-detail'),  # For Manager
    path('orders/delivery-crew/', DeliveryCrewOrderList.as_view(), name='delivery-crew-orders'),  # For Delivery Crew
    path('orders/<int:orderId>/status/', DeliveryCrewOrderDetail.as_view(), name='delivery-crew-order-detail'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
