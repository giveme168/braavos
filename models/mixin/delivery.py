from models.delivery import Delivery, DELIVERY_TYPE_MONITOR, DELIVERY_TYPE_CLICK


class DeliveryMixin():

    def get_delivery_num(self, date, delivery_type):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=delivery_type).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    delivery_type, 0)
        return delivery.value

    def get_monitor_num(self, date):
        delivery_type = DELIVERY_TYPE_MONITOR
        return self.get_delivery_num(date, delivery_type)

    def get_click_num(self, date):
        delivery_type = DELIVERY_TYPE_CLICK
        return self.get_delivery_num(date, delivery_type)

    def get_monitor_num_all(self):
        delivery_type = DELIVERY_TYPE_MONITOR
        deliverys = Delivery.query.filter_by(target_type=self.target_type,
                                             target_id=self.target_id,
                                             delivery_type=delivery_type)
        return sum([x.value for x in deliverys]) if deliverys.count() else 0

    def get_click_num_all(self):
        delivery_type = DELIVERY_TYPE_CLICK
        deliverys = Delivery.query.filter_by(target_type=self.target_type,
                                             target_id=self.target_id,
                                             delivery_type=delivery_type)
        return sum([x.value for x in deliverys]) if deliverys.count() else 0

    def set_delivery_num(self, date, delivery_type, num):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=delivery_type).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    delivery_type, num)
        else:
            delivery.value = max(delivery.value, num)
            delivery.save()

    def set_monitor_num(self, date, num):
        delivery_type = DELIVERY_TYPE_MONITOR
        return self.set_delivery_num(date, delivery_type, num)

    def set_click_num(self, date, num):
        delivery_type = DELIVERY_TYPE_CLICK
        return self.set_delivery_num(date, delivery_type, num)
