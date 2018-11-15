from django.core.management.base import BaseCommand, CommandError
from imagetagger.users.models import User, Team, TeamMembership
from imagetagger.tagger_messages.models import TeamMessage, GlobalMessage
from datetime import timedelta
from django.utils import timezone
from random import randint
from faker import Faker

faker = Faker()

class Command(BaseCommand):
    help = 'Test database performance for the messages'

    def handle(self, *args, **options):
        user_count = 5000
        team_count = 30
        message_count = 50000
        announcement_count = 5000
        if self.confirm():
            self.create_users(user_count)
            self.create_teams(team_count)
            self.create_messages(message_count) 
            self.create_announcements(announcement_count)       

    def create_users(self, user_count):
        User.objects.all().delete()
        for i in range(user_count):
            fake_name = faker.user_name()
            while User.objects.filter(username=fake_name).exists():
                fake_name = faker.user_name()
            User.objects.create(username=fake_name)
    
    def create_teams(self, team_count):
        TeamMembership.objects.all().delete()
        Team.objects.all().delete()
        user_count = User.objects.all().count()
        for i in range(team_count):
            fake_team_name = faker.user_name()
            team = Team.objects.create(name=fake_team_name)
            added_users = set()
            for user in range(int(randint(0,user_count)/2)):
                rand_user_id = randint(0,user_count - 1)
                if rand_user_id not in added_users:
                    user_obj = User.objects.all()[rand_user_id]
                    TeamMembership.objects.create(user=user_obj, team=team)
                added_users.add(rand_user_id)

    def create_messages(self, message_count):
        TeamMessage.objects.all().delete()
        user_count = User.objects.all().count()
        team_count = Team.objects.all().count()
        for i in range(message_count):
            team_obj = Team.objects.all()[randint(0,team_count - 1)]
            user_obj = User.objects.all()[randint(0,user_count - 1)]
            offset = timedelta(days=randint(-200,200))
            start_date = timezone.now() + timedelta(days=randint(-20,0)) + offset
            exp_date = timezone.now() + timedelta(days=randint(0,30)) + offset
            TeamMessage.objects.create(title=faker.sentences(nb=1, ext_word_list=None)[0], \
                                        content=faker.text(max_nb_chars=200, ext_word_list=None), \
                                        team=team_obj, creator=user_obj, start_time=start_date, \
                                        expire_time=exp_date)

    def create_announcements(self, announcement_count):
        GlobalMessage.objects.all().delete()
        user_count = User.objects.all().count()
        for i in range(announcement_count):
            user_obj = User.objects.all()[randint(0,user_count - 1)]
            offset = timedelta(days=randint(-200,200))
            start_date = timezone.now() + timedelta(days=randint(-20,0)) + offset
            exp_date = timezone.now() + timedelta(days=randint(0,30)) + offset
            GlobalMessage.objects.create(title=faker.sentences(nb=1, ext_word_list=None)[0], creator=user_obj, start_time=start_date, expire_time=exp_date)

    def confirm(self):
        print("Do you realy want flush the Database!!! (yes/no)")
        yes = {'yes','y', 'ye', ''}
        no = {'no','n'}

        choice = input().lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'")