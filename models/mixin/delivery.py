from models.delivery import Delivery, DELIVERY_TYPE_MONITOR, DELIVERY_TYPE_CLICK


class DeliveryMixin():

    def get_monitor_num(self, date):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=DELIVERY_TYPE_MONITOR).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    DELIVERY_TYPE_MONITOR, 0)
        return delivery.value

    def set_monitor_num(self, date, num):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=DELIVERY_TYPE_MONITOR).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    DELIVERY_TYPE_MONITOR, num)
        else:
            delivery.value = num
            delivery.save()

    def get_click_num(self, date):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=DELIVERY_TYPE_CLICK).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    DELIVERY_TYPE_CLICK, 0)
        return delivery.value

    def set_click_num(self, date, num):
        delivery = Delivery.query.filter_by(target_type=self.target_type,
                                            target_id=self.target_id, date=date,
                                            delivery_type=DELIVERY_TYPE_CLICK).first()
        if not delivery:
            delivery = Delivery.add(self.target_type, self.id, date,
                                    DELIVERY_TYPE_CLICK, num)
        else:
            delivery.value = num
            delivery.save()
