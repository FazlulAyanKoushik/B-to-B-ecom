from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from orderio.models import CartProduct, ReturnOrderProduct, OrderDelivery


@receiver(pre_save, sender=CartProduct)
def add_organization_to_cartproduct(sender, instance, **kwargs):
    instance.organization = instance.product.organization


# @receiver(post_save, sender=OrderDelivery)
# def save_an_paid_order_to_a_transaction(sender, instance: Order, created, **kwargs):
#     if (
#         instance.status == OrderStatus.COMPLETED
#         and instance.stage == OrderStageChoices.CURRENT
#     ):
#         instance.order.completed = True
#         instance.order.save_dirty_fields()
#         # Added to transaction when the order is completed
#         TransactionOrganizationUser.objects.create(
#             organization=instance.order.organization,
#             user=instance.order.customer,
#             total_money=instance.order.total_price,
#             payable_money=instance.order.payable_amount,
#             order=instance.order,
#         )


# @receiver(post_save, sender=ReturnOrderProduct)
# def update_the_order_price_after_return(sender, instance: ReturnOrderProduct, **kwargs):
#     # update product's stock quantity
#     if instance.is_damage:
#         instance.order_product.product.damage_stock = (
#             instance.order_product.product.damage_stock + instance.returned_quantity
#         )
#         instance.order_product.product.save_dirty_fields()
#
#     else:
#         instance.order_product.product.stock = (
#             instance.order_product.product.stock + instance.returned_quantity
#         )
#         instance.order_product.product.save_dirty_fields()
#
#     # update order product's quantity
#     instance.order_product.updated_quantity = (
#         instance.order_product.updated_quantity - instance.returned_quantity
#     )
#
#     if instance.order_product.updated_quantity < 1:
#         instance.order_product.delete()
#     else:
#         instance.order_product.save_dirty_fields()
#
#     # update order product total price
#     instance.order_product.order.total_price = (
#         instance.order_product.order.calculate_updated_price()
#     )
#     instance.order_product.order.save_dirty_fields()
#
#     # update order product total price
#     instance.order.total_price = instance.order.calculate_updated_price()
#     instance.order.save_dirty_fields()
