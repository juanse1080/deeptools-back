from django.db import models
from .managers import UserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser


class User(AbstractBaseUser, PermissionsMixin):

    role_choices = (
        ('admin', 'Administrador'),
        ('creator', 'Creator'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=role_choices)
    birth = models.DateField(null=True)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    email = models.CharField(max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
            This method get full name 
            Returns:
                {str}
                    This is the full name
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
            This method get short name
            Returns:
                {str}
                    This is the fist name
        """
        return self.first_name

    def get_template(self):
        template = {
            'admin': 'navbar/layout.html',
            'creator': 'navbar/layout.html',
            'user': 'navbar/user.html'
        }
        return template[self.role]

    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     '''
    #     Sends an email to this User.
    #     '''
    #     send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        """
            This method cast user to str
            Returns:
                {str}
                    This is user identification
        """
        return str(self.id)

    def show(self):
        """
            This method cast user to dict
            Returns:
                {dict}
                    This is user in dict format
        """
        return self.__dict__


class Notification(models.Model):
    title = models.CharField(max_length=100)
    kind = models.CharField(max_length=10)
    description = models.TextField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
