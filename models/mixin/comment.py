import datetime

from models.comment import Comment


class CommentMixin():

    def add_comment(self, user, msg, msg_channel=0):
        Comment.add(self.target_type, self.target_id, msg, user, datetime.datetime.now(), msg_channel)

    def get_comments(self, msg_channel=0):
        all_comments = Comment.query.filter_by(target_type=self.target_type,
                                               target_id=self.target_id).order_by(Comment.create_time.desc())
        if msg_channel:
            return [c for c in all_comments if c.msg_channel == int(msg_channel)]
        else:
            return [c for c in all_comments if not c.msg_channel]

    def get_mention_users(self, except_user, msg_channel=0):
        return list(set([c.creator for c in self.get_comments(msg_channel) if c.creator is not except_user]))

    def delete_comments(self):
        for com in Comment.query.filter_by(target_type=self.target_type, target_id=self.target_id):
            com.delete()
