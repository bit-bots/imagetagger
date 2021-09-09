from django.core.management import BaseCommand

from imagetagger.annotations.models import Verification
from imagetagger.users.models import User


class Command(BaseCommand):
    help = '''
    Update the points for all users.
    While the points are updated by database triggers, this command explicitly
    calculates the points for all users. This is useful to fix inconsistencies
    or to calculate initial point values if the points migration is applied
    with existing data.
    '''

    def handle(self, *args, **options):
        for user in User.objects.all():
            user.points = Verification.objects.filter(
                verified=True,
                annotation__user=user).count()
            user.save(update_fields=('points',))
