import datetime

from models.attachment import (Attachment, ATTACHMENT_TYPE_CONTRACT, ATTACHMENT_TYPE_SCHEDULE,
                               ATTACHMENT_TYPE_OUTSOURCE, ATTACHMENT_TYPE_OTHERS, ATTACHMENT_TYPE_AGENT,
                               ATTACHMENT_TYPE_FINISH, ATTACHMENT_TYPE_USER_PIC, ATTACHMENT_TYPE_MEDIUM)


class AttachmentMixin():

    def get_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id
                                          ).order_by(Attachment.create_time.desc())

    def delete_attachments(self):
        for a in self.get_attachments():
            a.delete()

    def add_medium_files(self, user, filename, type):
        Attachment.add(self.target_type, self.target_id, filename,
                       type, user, datetime.datetime.now())
        return self.get_last_medium(type)

    def add_contract_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_CONTRACT, user, datetime.datetime.now())
        return self.get_last_contract()

    def get_medium_files(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id
                                          ).order_by(Attachment.create_time.desc())

    def get_medium_files_by_type(self, type):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=type
                                          ).order_by(Attachment.create_time.desc())

    def get_last_medium(self, type):
        return self.get_medium_files_by_type(type).first()

    def get_contract_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_CONTRACT
                                          ).order_by(Attachment.create_time.desc())

    def get_last_contract(self):
        return self.get_contract_attachments().first()

    def add_finish_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_FINISH, user, datetime.datetime.now())
        return self.get_last_finish()

    def get_finish_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_FINISH
                                          ).order_by(Attachment.create_time.desc())

    def get_last_finish(self):
        return self.get_finish_attachments().first()

    def add_schedule_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_SCHEDULE, user, datetime.datetime.now())
        return self.get_last_schedule()

    def add_outsource_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_OUTSOURCE, user, datetime.datetime.now())
        return self.get_last_schedule()

    def add_agent_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_AGENT, user, datetime.datetime.now())
        return self.get_last_schedule()

    def get_agent_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_AGENT
                                          ).order_by(Attachment.create_time.desc())

    def add_medium_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_MEDIUM, user, datetime.datetime.now())
        return self.get_last_schedule()

    def get_medium_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_MEDIUM
                                          ).order_by(Attachment.create_time.desc())

    def get_schedule_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_SCHEDULE
                                          ).order_by(Attachment.create_time.desc())

    def get_outsource_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_OUTSOURCE
                                          ).order_by(Attachment.create_time.desc())

    def add_other_attachment(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_OTHERS, user, datetime.datetime.now())
        return self.get_last_others()

    def get_other_attachments(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_OTHERS
                                          ).order_by(Attachment.create_time.desc())

    def get_last_others(self):
        return self.get_other_attachments().first()

    def get_last_schedule(self):
        return self.get_schedule_attachments().first()

    def is_attachment_ready(self):
        return self.get_last_contract() and self.get_last_schedule()

    def add_user_pic_file(self, user, filename):
        Attachment.add(self.target_type, self.target_id, filename,
                       ATTACHMENT_TYPE_USER_PIC, user, datetime.datetime.now())
        return self.get_last_user_pic_file()

    def get_user_pic_files(self):
        return Attachment.query.filter_by(target_type=self.target_type,
                                          target_id=self.target_id,
                                          attachment_type=ATTACHMENT_TYPE_USER_PIC
                                          ).order_by(Attachment.create_time.desc())

    def get_last_user_pic_file(self):
        return self.get_user_pic_files().first()
