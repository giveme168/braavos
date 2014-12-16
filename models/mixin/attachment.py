import datetime

from models.attachment import Attachment

ATTACHMENT_TYPE_CONTRACT = 0
ATTACHMENT_TYPE_SCHEDULE = 1


class AttachmentMixin():

    def add_contract_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename, ATTACHMENT_TYPE_CONTRACT, user, datetime.datetime.now())

    def get_contract_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_CONTRACT).order_by(Attachment.create_time.desc())

    def get_last_contract_path(self):
        attachs = self.get_contract_attachments()
        return attachs[0].path if attachs.count() else ""

    def add_schedule_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename, ATTACHMENT_TYPE_SCHEDULE, user, datetime.datetime.now())

    def get_schedule_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_SCHEDULE).order_by(Attachment.create_time.desc())

    def get_last_schedule_path(self):
        attachs = self.get_schedule_attachments()
        return attachs[0].path if attachs.count() else ""
