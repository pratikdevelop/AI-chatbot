from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, name=None, phone=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        if not phone:
            raise ValueError('The Phone field must be set')
        if not name:
            raise ValueError('The Name field must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, name=name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, name='Admin', phone='0000000000', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, name, phone, **extra_fields)