**All endpoints**

**Merchant Endpoint:**

| URL                                       | Method     | Serializer                           | Logic                                                                                                     | Permission                                     | App   |
|-------------------------------------------|------------|--------------------------------------|-----------------------------------------------------------------------------------------------------------|------------------------------------------------|-------|
| /api/v1/we/default/<uuid:organizatin_uid> | Patch      | PrivateOrganizationDefaultSerializer | Merchant change their organization. Just pass the organization**uid** in payload                          | IsOrganization                                 | weapi |
| /api/v1/we/user/                          | Post       | PrivateOrganizationSerializer        | Merchant can add user into a organization                                                                 | IsAuthenticated and role admin and staff       | weapi |
| /api/v1/we/products/                      | List, Post | PrivateProductSerializers            | Merchant can add product                                                                                  | IsOrganization                                 | weapi |
| /api/v1/we/search/products/               | Post       | PrivateBaseProductSearchSerializers  | Merchant can search base product                                                                          | IsOrganizationStaff                            | weapi |
| /api/v1/we/                               | Get, Post  | PrivateOrganizationSerializers       | If merchant is owner, he can create a new organization otherwise any merchant can see their organizations | IsOrganizationOwner(Post), IsOrganization(Get) | weapi |

**Customer Endpoint:**

| URL                      | Method                    | Serializer                                   | Logic                                                                               | Permission      | App   |
|--------------------------|---------------------------|----------------------------------------------|-------------------------------------------------------------------------------------|-----------------|-------|
| /api/v1/me/addresses/    | Get,Post,Put,Delete(soft) | PublicAddressSerializers                     | Customer can make operation CRUD their address                                      | IsAuthenticated | meapi |
| /api/v1/me/cart/         | Get,Post                  | PrivateAddToCart (Post),   PrivateCarts(Get) | Customer can add product/update product quantity/ can see the cart products         | IsAuthenticated | meapi |
| /api/v1/me/order/        | Post                      | PublicOrderSerializer                        | Customer can add products to orders which is come from the cart                     | IsAuthenticated | meapi |
| /api/v1/me/organization/ | Post                      | PublicOrganization                           | Customer can send request with their organization to django-admin and role of owner | IsAuthenticated | meapi |
| /api/v1/me               | Get                       | PublicMeSerializer                           | User can see their information                                                      | IsAuthenticated | meapi |

**Global Endpoint:**

| URL                         | Method | Serializer                                 | Logic                                                      | Permission | App  |
|-----------------------------|--------|--------------------------------------------|------------------------------------------------------------|------------|------|
| /api/v1/auth/registration/  | Post   | PublicUserRegistrationSerializer           | A user can register                                        | All        | core |
| /api/v1/auth/token/         | Post   | TokenRefreshView (default by SimpleJWT)    | A user get access and refresh token                        | All        | core |
| /api/v1/auth/token/logout/  | Post   | LogoutView (default by SimpleJWT)          | A user can logout from the server                          | All        | core |
| /api/v1/auth/token/refresh/ | Post   | TokenObtainPairView (default by SimpleJWT) | A user can access and refresh token from the refresh token | All        | core |
