import datetime

from models.attachment import Attachment, ATTACHMENT_TYPE_CONTRACT, ATTACHMENT_TYPE_SCHEDULE


class AttachmentMixin():

    def get_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id
                                          ).order_by(Attachment.create_time.desc())

    def delete_attachments(self):
        for a in self.get_attachments():
            a.delete()

    def add_contract_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_CONTRACT, user, datetime.datetime.now())
        return self.get_last_contract()

    def get_contract_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_CONTRACT
                                          ).order_by(Attachment.create_time.desc())

    def get_last_contract(self):
        return self.get_contract_attachments().first()

    def add_schedule_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_SCHEDULE, user, datetime.datetime.now())
        return self.get_last_schedule()

    def get_schedule_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_SCHEDULE
                                          ).order_by(Attachment.create_time.desc())

    def get_last_schedule(self):
        return self.get_schedule_attachments().first()

    def is_attachment_ready(self):
        return self.get_last_contract() and self.get_last_schedule()
