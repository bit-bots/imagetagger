Upgrade instructions
====================

Upgrading 0.4 to 0.5
--------------------

Release 0.5 introduces a custom user model.
Therefore, additional steps are required for an upgrade from pre-0.5.

First of all, make sure that your settings contain the following line:

    AUTH_USER_MODEL = 'users.User'

The following steps should be taken with commit 73c6049bac41efd30eea9806d44c343b0f14c53d checked out (i.e., the commit that initially introduced the user model).

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
