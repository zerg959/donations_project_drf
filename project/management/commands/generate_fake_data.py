# myapp/management/commands/fill_fake_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from project.models import Collect, Payment
from faker import Faker
import random
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populates the database with fake users, collections, and payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--collections',
            type=int,
            default=50,
            help='Number of collections to create'
        )
        parser.add_argument(
            '--payments',
            type=int,
            default=100,
            help='Number of payments to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        fake = Faker('en_US')  # English localization

        num_users = options['users']
        num_collections = options['collections']
        num_payments = options['payments']
        clear = options['clear']

        if clear:
            self.stdout.write('Clearing existing data...')
            Payment.objects.all().delete()
            Collect.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        # Create users
        users = []
        for i in range(num_users):
            username = fake.user_name() + str(random.randint(100, 999))
            email = fake.email()
            user, created = User.objects.get_or_create(
                username=username[:150],
                defaults={
                    'email': email,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
            if i % 100 == 0 and i > 0:
                self.stdout.write(f'Created {i} users...')

        if not users:
            users = list(User.objects.filter(is_superuser=False))

        self.stdout.write(self.style.SUCCESS(f'Created/Retrieved {len(users)} users.'))

        # Create collections
        PURPOSE_CHOICES = [choice[0] for choice in Collect.PURPOSE_CHOICES]

        collections = []
        for i in range(num_collections):
            author = random.choice(users)
            title = fake.sentence(nb_words=4).rstrip('.')
            purpose = random.choice(PURPOSE_CHOICES)
            description = fake.paragraph(nb_sentences=3)

            # 30% of collections have no target amount
            target_amount = None if random.random() < 0.3 else Decimal(random.randint(5000, 100000))

            # Current amount: 0 to target_amount (if set)
            current_amount = Decimal(0)
            if target_amount:
                current_amount = min(
                    Decimal(random.randint(0, int(target_amount))),
                    target_amount
                )

            # Participants: 1 to 50
            participants = random.randint(1, 50)

            # 10% of completed collections (if target set)
            ended_at = None
            if target_amount and current_amount >= target_amount and random.random() < 0.1:
                ended_at = fake.date_time_between(
                    start_date='-2y',
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                    )

            collect = Collect.objects.create(
                author=author,
                title=title,
                purpose=purpose,
                description=description,
                target_amount=target_amount,
                current_amount=current_amount,
                participants=participants,
                created_at=fake.date_time_between(
                    start_date='-3y',
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                    ),
                ended_at=ended_at,
            )
            collections.append(collect)

            if i % 100 == 0 and i > 0:
                self.stdout.write(f'Created {i} collections...')

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(collections)} collections.')
            )

        # Create payments
        for i in range(num_payments):
            collect = random.choice(collections)
            user = random.choice(users)
            amount = Decimal(random.randint(100, 5000))

            Payment.objects.create(
                user=user,
                amount=amount,
                collect=collect,
                timestamp=fake.date_time_between(
                    start_date=collect.created_at,
                    end_date=timezone.now() if not collect.ended_at else collect.ended_at,
                    tzinfo=timezone.get_current_timezone()
                )
            )

            if i % 500 == 0 and i > 0:
                self.stdout.write(f'Created {i} payments...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Database successfully populated:\n'
                f'{len(users)} users\n'
                f'{len(collections)} collections\n'
                f'{num_payments} payments'
            )
        )
