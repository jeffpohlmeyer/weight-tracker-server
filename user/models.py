from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256)
    email = fields.CharField(max_length=256)
    hashed_password = fields.CharField(max_length=256)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    token = fields.CharField(max_length=512, null=True)
    token_expiration = fields.DatetimeField(null=True)
    is_superuser = fields.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} <{self.email}>"
