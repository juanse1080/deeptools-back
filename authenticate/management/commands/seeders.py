from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.apps import apps

from importlib import import_module
from django.apps.config import AppConfig
from inspect import getmembers, isfunction
# import apps.user.seeders

import traceback
import sys


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        import_elements = []
        names = []
        for app in apps.get_app_configs():
            seeder_module_name = '%s.%s' % (app.module.__name__, 'seeders')
            try:
                import_elements.append(import_module(seeder_module_name))
                names.append(seeder_module_name)
                self.stdout.write(self.style.SUCCESS(
                    "imported %s" % seeder_module_name))
            except ImportError as error:

                if seeder_module_name not in str(error):
                    self.stdout.write(self.style.ERROR(
                        'Error in  %s: %s' % (seeder_module_name, error)))
                    exc_type, exc_obj, tb = sys.exc_info()
                    print(exc_type)
                    print(exc_obj)
                    traceback.print_exc()
                else:
                    self.stdout.write(self.style.ERROR(
                        'seeders.py does not exist in module %s' % app.module.__name__))

        print("\n")

        for item, seeder in enumerate(import_elements):
            try:
                seeder.create_seeder()
                self.stdout.write(self.style.SUCCESS(
                    '%s create_seeder() executed' % names[item]))
            except IntegrityError as error:
                self.stdout.write(self.style.WARNING(
                    error))
            except:
                self.stdout.write(self.style.ERROR(
                    'Error during execute %s.py' % names[item]))
                exc_type, exc_obj, tb = sys.exc_info()
                print(exc_type)
                print(exc_obj)
                traceback.print_exc()
