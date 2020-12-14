Upgrade instructions
====================

Upgrading 0.5 to 0.6
--------------------

Release 0.6 changed the application configuration to be largely based on environment variables instead of the operator
providing a custom `settings.py` file.

Most settings which previously had to be defined can now be given as environment variables but with an `IT_` prefix.
See [the README](https://github.com/bit-bots/imagetagger#configuration) on more details.

If desired, a custom configuration file can still be supplied. This is explained in the README as well.

Upgrading 0.4 to 0.5
--------------------

Release 0.5 introduces a custom user model and changes the settings layout.
Therefore, additional steps are required for an upgrade from pre-0.5.

### Custom User Model

The following steps should be taken with commit 362a36a868a68fd0623cc549edee3d4105d9e0c8 checked out (i.e., the commit that initially introduced the user model).

Make sure that your settings contain the following (after returning to master, that configuration value can be removed again as it is contained in the new settings_base):

    AUTH_USER_MODEL = 'users.User'

Then, open a database shell (e.g., ./manage.py dbshell):

    TRUNCATE django_migrations;
    ALTER TABLE auth_user RENAME TO users_user;
    ALTER SEQUENCE auth_user_id_seq RENAME TO users_user_id_seq;
    ALTER TABLE auth_user_groups RENAME TO users_user_groups;
    ALTER SEQUENCE auth_user_groups_id_seq RENAME TO users_user_groups_id_seq;
    ALTER TABLE auth_user_user_permissions RENAME TO users_user_user_permissions;
    ALTER SEQUENCE auth_user_user_permissions_id_seq RENAME TO users_user_user_permission_id_seq;

Populate the migrations table again:

    ./manage.py migrate --fake

Afterwards, the user model should be usable. You can check out the most recent commit of the release and run normal migrations up to there:

    ./manage.py migrate


### Configuration

Make sure that your settings contain the following line at the top:

    from .settings_base import *

The configuration layout was changed to allow simpler updates to the configs in the future. All generic settings
are in the settings_base.py file now, which is loaded by the settings.py file. This way, the settings.py contains only the
settings the admin needs to change. For some of them, defaults are defined in the settings_base.

To migrate it would be best to apply your changes to the new settings.py.example template as then new settings with
defaults can be introduced without braking your deployment.

### Calculating points

If you have existing data after updating from 0.4, the points (which are incremented and decremented by a database trigger will be wrong. To recalculate them, run:

    ./manage.py updatepoints
