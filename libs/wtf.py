#-*- coding: UTF-8 -*-
from flask.ext.wtf import Form as BaseForm


class Form(BaseForm):

    def disable_all(self):
        for field in self:
            field.disabled = True
