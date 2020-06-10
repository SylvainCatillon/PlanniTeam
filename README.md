#PlanniTeam, team planning
With PlanniTeam, you can create a schedule with events, and ask your teammates 
to indicate their participation.

When a user creates a planning, they decide to let the access open, or to restrict it
to a list of users, by giving their emails.
At the planning creation, or at any time once its created, the creator can add
events, with for each:
* A date (required)
* A time
* A description
* An address

At any time, events information can be modified.

The users participating in a planning can:
* See events information
* Indicate their availability for each event
* See a summary of the availability of other participants
* See the exact answers of other participants
* Edit their previous answer

####PlanniTeam is online (in french) at https://planniteam.herokuapp.com/

If you install this application localy, you have to define the following environment
 variables:
* SECRET_KEY: The secret key used by Django
* DJANGO_SETTINGS_MODULE: The settings' module used by Django
* DB_PASSWORD: The password of your database admin
* DOMAIN: The domain of your server (to display a link in the notifications emails)
* EMAIL_HOST_PASSWORD: The password of your email server host