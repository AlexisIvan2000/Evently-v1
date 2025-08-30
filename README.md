# Evently 

Evently is a web application built with **Flask** that allows users to:
- Create an account (with hashed passwords),
- Log in and log out securely,
- Search for events using the **Ticketmaster API** (filter by city, state/province, and type),
- View results as event cards (name, date, venue, and link to Ticketmaster).

A welcome email is sent upon registration (can be disabled or replaced with Mailtrap for demo purposes).



##  Features

- Secure authentication (Flask-Login + password hashing with Werkzeug).
- Styled registration and login forms.
- AJAX requests with **fetch** to load events without reloading the page.
- Dynamic pagination (Previous / Next).
- Modern responsive design.

## Demo Video
[Watch the demo on Google Drive](https://drive.google.com/file/d/1Ah82oJfM-46ck9833KNrp10EnEgD_44N/view?usp=sharing)

Here is a preview of Evently
[receiving mail]("docs/demo.png")

