# Custom Invoicing

This Django application assists you with managing client details, keep track of
time spent on a project and generate time sheets and invoices.

**disclaimer: this is a work in progress**

# Install

- Install the requirements in [the requirements file](./requirements.txt)
- Configure your database in [the settings file](./webapp/settings.py) (or
don't if you're ok with a local sqlite database)
- Run the database migrations: `python manage.py migrate`
- Create an admin user: `python manage.py createsuperuser`
- Run the tests: *sorry, no tests yet*
- Run the application: `python manage.py runserver`
- Go to the [admin page](http://localhost:8000/admin)

# Models in the application

View the [models file](./invoicing/models.py) to see the different models in the
application and their relations.

# Reports

Reporting is currently a work in progress. I've added two admin actions:
`Generate invoice` and `Generate timesheet`. These are defined in the [admin
file](./invoicing/admin.py). As you can see there, they redirect to urls that
are defined in the [urls file](./webapp/urls.py) and they link to the views in
the [views file](./invoicing/views.py). As you can see there, those views search for
query parameters to generate the report, but the actions don't pass them to the url
yet.

# Toggl

I use [toggl](http://toggl.com) to track my time so there is a tight connection between Toggl and this
application. Both the Project and the TimeEntry model have a togglId. For the project, that id is used
to link the data from toggl to the right project in the database. For the time entry, that is used to
prevent us to load the same entry from toggl twice.

There is a management command
[`toggle-import`](./invoicing/management/commands/toggle-import.py) that can be
used to import new time entries from toggl in the application. Note that for this
to work, you will have to set your toggl API key in the settings as `TOGGL_API_KEY`.

Run `python manage.py toggle-import --help` to view its help information.