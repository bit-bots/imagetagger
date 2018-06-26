Upgrade instructions
====================

Upgrading 0.4 to 0.5
--------------------

Release 0.5 introduces a custom user model and changes the settings layout.
Therefore, additional steps are required for an upgrade from pre-0.5.

### Configuration 

First of all, make sure that your settings contain the following line:

    from .settings_base import *

at the top.


The configuration layout was changed to allow simpler updates to the configs in the future. Now all basic settings
are in the settings_base.py file and the settings.py file loads them, so in the settings.py file are only the
settings the Admin is supposed to change. For some of them defaults are defined in the settings_base.

To migrate it would be best to apply your changes to the new settings.py.example template as then new settings with
defaults can be introduced without braking your deployment.

### Databse

The following steps should be taken with commit 362a36a868a68fd0623cc549edee3d4105d9e0c8 checked out (i.e., the commit that initially introduced the user model).

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

