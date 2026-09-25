import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('judge', '0149_add_organization_private_problems_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemStarter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(blank=True, help_text='Python 3 code shown in the editor when a student opens the problem (their saved draft, if any, takes priority).', verbose_name='starter code')),
                ('problem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ee_starter', to='judge.problem')),
            ],
            options={
                'verbose_name': 'starter code',
                'verbose_name_plural': 'starter code',
            },
        ),
    ]
