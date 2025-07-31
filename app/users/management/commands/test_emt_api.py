import json
import os
import re

import listmonk
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from listmonk.models import MailingList

User = get_user_model()

class Command(BaseCommand):
    help = 'Tests the connection of EMT'

    def handle(self, *args, **options):
        listmonk.set_url_base(settings.LISTMONK_API_URL)
        listmonk.login(settings.LISTMONK_API_USERNAME, settings.LISTMONK_API_TOKEN)
        valid: bool = listmonk.verify_login()

        print("VALID: ", valid)

        up: bool = listmonk.is_healthy()

        print("UP: ", up)

        the_list: MailingList = listmonk.list_by_id(list_id=2)

        new_subscriber = listmonk.create_subscriber(
            'mschuchowski@gmx.de',
            'Michael Schuchowski',
            {2},
            pre_confirm=True,
            attribs={'premium': 'yes'},
        )

        listmonk.confirm_optin(new_subscriber.uuid, the_list.uuid)

        self.stdout.write(self.style.SUCCESS(f'Successfully tested the EMT API.'))
