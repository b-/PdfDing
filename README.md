_# PdfDing
<hr>

## Overview

- [Introduction](#introduction)
- [Installation](#installation)
  - [Using Docker](#using-docker) 
  - [Using Docker Compose](#using-docker-compose)
  - [Admin User](#admin-user) 
  - [SSO](#single-sign-on-sso)
- [Configuration](#configuration)
- [Tech Stack](#tech-stack)
- [Acknowledgements](#acknowledements)
- [Contributing](#contributing)

## Introduction
<hr>

PdfDing is a PDF manager and viewer that you can host yourself. It offers a seamless user experience on multiple
devices. It's designed be to be minimal, fast, and easy to set up using Docker.

PdfDing was created because I was searching for a selfhostable browser based PDF viewer that I can seamlessly use on my
desktop and my mobiles. However, the existing solution were either too heavy and feature rich or did
not match my use case. Thus, I am developing PDfDing as a simple webapp with a clear focus on a single thing: viewing
and managing PDFs. This is also why you won't find any fancy AI or OCR in this project.

The name is a combination of PDF and *ding*. Ding is the German word for thing. Thus, PdfDing is a thing for
your PDFs. The name and the design of PdfDing are inspired by [linkding](https://github.com/sissbruecker/linkding).
Linkding is an excellent selfhostable bookmark manager. If you are unfamiliar with it be sure to check it out!

### Feature Overview
* Seamless browser based PDF viewing on multiple devices
* Organize PDFs with tags
* Clean and responsive UI
* Dark Mode and colored themes
* Remembers current position - continue where you stopped reading
* SSO support via OIDC
* Every user can upload its own PDFs. There is no admin curating the content.
* Simple Admin area for user management

### Demo Video
![Demo gif](demo.gif)

## Installation
PdfDing is designed to be run with container solutions like Docker. The Docker image is compatible with ARM64 platforms,
so it can be run on a Raspberry Pi 4.

PdfDing uses an SQLite database by default. Alternatively PdfDing supports PostgreSQL.

### Using Docker

To install PdfDing using Docker you can just run the image from [Docker Hub](https://hub.docker.com/r/mrmn/pdfding):

```
docker run --name pdfding \
    -p 8000:8000 \
    -v sqlite_data:/home/nonroot/pdfding/db -v media:/home/nonroot/pdfding/media \
    -e HOST_NAME=127.0.0.1 -e SECRET_KEY=some_secret -e CSRF_COOKIE_SECURE=FALSE -e SESSION_COOKIE_SECURE=FALSE \
    -d \
    mrmn/pdfding:latest
```

If everything completed successfully, the application should now be running
and can be accessed at http://127.0.0.1:8000.

### Using Docker Compose
To install linkding using Docker Compose, you can use one of the files in the
[deploy](https://codeberg.org/mrmn/PdfDing/src/branch/master/deploy) directory and run e.g.:

```
docker-compose -d -f sqlite.docker-compose.yaml
```

### Admin user
If needed or wished it is possible to create an admin user. Admin users can view and delete users.
Creating an admin user is optional. To give a user admin rights execute
```
python pdfding/manage.py make_admin -e admin@pdfding.com
```
inside the shell of the running container and specify the correct email address.
Admin users can can also give other users admin rights via the ui.

### Single Sign on (SSO)
PdfDing supports SSO via OIDC. OIDC is set up by using environment variables: 
```
OIDC_ENABLE: "TRUE"
OIDC_CLIENT_ID: "pdfding"
OIDC_CLIENT_SECRET: "client_secret"
OIDC_AUTH_URL: "https://auth.pdfding.com/.well-known/openid-configuration"
OIDC_PROVIDER_NAME: "Authelia"
```

More information about the environment variables can be found in the [Configuration](#configuration) section.

Once PdfDing is set up for using OIDC the same needs to be done on the OIDC identity provider's side. Of course, this 
configuration depends on the used identity provider. Here is an example configuration
for [Authelia](https://www.authelia.com/):
```
oidc:
    ## The other portions of the mandatory OpenID Connect 1.0 configuration go here.
    ## See: https://www.authelia.com/c/oidc
    clients:
      - id: pdfding
            description: PdfDing
            # create client secret and hash with
            # docker run --rm authelia/authelia:latest authelia crypto rand --length 64 --charset alphanumeric
            secret: '$pbkdf2-sha512$310000$<rest_of_hashed_secret>'
            public: false
            authorization_policy: two_factor
            scopes:
              - openid
              - email
              - profile
            redirect_uris:
              - https://pdfding.com/accountoidc/login/callback/
```

## Configuration
### `SECRET_KEY`
Values: `string` | Default = `None`

This value is the key to securing signed data. Should be to a large random value! Example: `some_secret`

### `HOST_NAME`
Values: `string` | Default = `None`

The host/domain name where PdfDing will be reachable. Example: `pdfding.com`   

### `HOST_PORT`
Values: `integer` | Default: `8000`

Allows to set a custom port for the PdfDing server. 

### `DATABASE_TYPE`
Values: `SQLITE`, `POSTGRES` | Default `POSTGRES`

Specify which database type should be used.

### `POSTGRES_PASSWORD`
Values: `string` | Default = `None`

The password for the postgres DB: Example: `password`

### `POSTGRES_PORT`
Values: `integer` | Default: `5432`

The port of the postgres DB.

### `ACCOUNT_EMAIL_VERIFICATION`
Values: `TRUE`, `FALSE` | Default: `TRUE`

Block users until they have verified their email address.

### `OIDC_ENABLE`
Values: `TRUE`, `FALSE` | Default: `FALSE`

Flag for enabling SSO via OIDC. By setting this value to `TRUE` OIDC will be activated.

### `OIDC_CLIENT_ID`
Values: `string` | Default = `None`

PdfDing's OIDC client id. Example: `pdfding`

### `OIDC_CLIENT_SECRET`
Values: `string` | Default = `None`

PdfDing's OIDC client secret. Should be a large random value! Example: `another_long_secret`

### `OIDC_AUTH_URL`
Values: `string` | Default = `None`

The URL to the OpenID configuration of the auth server. Example: 
`https://auth.pdfding.com/.well-known/openid-configuration`

### `OIDC_ONLY`
Values: `TRUE`, `FALSE` | Default: `TRUE`

By setting this to `TRUE` users will only be able to authenticate using OIDC.

### `OIDC_PROVIDER_NAME`
Values: `string` | Default = `OIDC`

The name of the OIDC provider. The name will be displayed on the login screen as `OIDC_LOG IN VIA <PROVIDER_NAME>`.
Example: `Authelia`

### `CSRF_COOKIE_SECURE`
Values: `TRUE`, `FALSE` | Default: `TRUE`

Set this to True to avoid transmitting the CSRF cookie over HTTP accidentally.

### `SESSION_COOKIE_SECURE`
Values: `TRUE`, `FALSE` | Default: `TRUE`

Set this to True to avoid transmitting the session cookie over HTTP accidentally. 

### `SECURE_SSL_REDIRECT`
Values: `FALSE`, `TRUE` | Default: `FALSE`

Redirects all non-HTTPS requests to HTTPS. If PdfDing is running behind a reverse proxy this can cause infinite 
redirects.

### `SECURE_HSTS_SECONDS`
Values: `integer` | Default: `None`

For sites that should only be accessed over HTTPS, you can instruct modern browsers to refuse to connect to your domain
name via an insecure connection (for a given period of time) by setting the “Strict-Transport-Security” header. 
`SECURE_HSTS_SECONDS` will set this header for you on all HTTPS responses for the specified number of seconds. Test this
with a small value first. If everything works it can be set to a large value, e.g. `31536000` (1 year) , in order to
protect infrequent visitors.

### `ACCOUNT_DEFAULT_HTTP_PROTOCOL`
Values: `https`, `http` | Default: `https`

The default protocol for account related URLs, e.g. for the password forgotten procedure.

### `EMAIL_BACKEND `
Values: `CONSOLE`, `SMTP` | Default: `CONSOLE`

Whether to send account related emails, e.g a password reset or account verification, to the console or via an SMTP
server.

### `SMTP_HOST`
Values: `string` | Default = `None`

The host/domain name of the SMTP server. Example: `pdfding.com`

### `SMTP_PORT`
Values: `integer` | Default: `587`

The port of the SMTP server.

### `SMTP_USER`
Values: `string` | Default = `None`

The username used for logging into the SMTP server.

### `SMTP_PASSWORD`
Values: `string` | Default = `None`

The password used for logging into the SMTP server.

### `SMTP_USE_TLS`
Values: `FALSE`, `TRUE` | Default: `FALSE`

Secure the connection to the SMTP server with TLS. Some SMTP servers support only one kind and
some support both. Note that `SMTP_USE_TLS`/`SMTP_USE_SSL` are mutually exclusive.

### `EMAIL_USE_SSL`
Values: `FALSE`, `TRUE` | Default: `FALSE`

Secure the connection to the SMTP server with SSL. Some SMTP servers support only one kind and
some support both. Note that `SMTP_USE_TLS`/`SMTP_USE_SSL` are mutually exclusive.

## Tech Stack
* The web app is build using the Python web framework [Django](https://www.djangoproject.com/)
* Mozilla's [PDF.js](https://mozilla.github.io/pdf.js/) is used for viewing PDF files in the browser
* The frondend is build using [Alpine.js](https://alpinejs.dev/), [htmx](https://htmx.org/),
[jQuery](https://jquery.com/) and [Tailwind CSS](https://tailwindcss.com/)
* Authentication, registration, account management and OIDC is achieved by [django-allauth](https://docs.allauth.org/en/latest/)

## Acknowledements
* This project started by adjusting the django starter of Andreas Jud: [django-starter](https://github.com/andyjud/django-starter), [django-starter-assets](https://github.com/andyjud/django-starter-assets)
* As mentioned above, inspired by [linkding](https://github.com/sissbruecker/linkding).

## Contributing
PdfDing is open source, so you are free to modify or contribute. PdfDing is built using the Django web framework. You
can get started by checking out the excellent [Django docs](https://docs.djangoproject.com/en/stable/). Currently, 
PdfDing consists of four applications: 
* Inside the `pdf` folder is the one related to managing and viewing PDFs
* the folder `users` contains the logic related to users
* the admin area is implemented inside the `admin` folder
* `core` is the Django root application

Other than that the code should be self-explanatory / standard Django stuff 🙂.

### Prerequisites

* Python 3
* pipx
* Poetry: `pipx install poetry`
* Node.js

### Setup

Clone the repository:
```
git clone https://codeberg.org/mrmn/PdfDing.git
```

cd into the project:
```
cd PdfDing
```

Create the virtual environment and install all dependencies:
```
poetry install
```

Activate the environment for your shell:
```
poetry shell
```

Install frontend dependencies:
```
mkdir ./js && mkdir ./css
npm ci
npm run build
```

Initialize the database:
```
python pdfding/manage.py migrate
```

Create a user for the frontend:
```
python pdfding/manage.py createsuperuser
```

Start the development server with:

```
# in one shell run
python pdfding/manage.py runserver
# in another run
npx tailwindcss -i pdfding/static/css/input.css -o pdfding/static/css/tailwind.css -c tailwind.config.js --watch
```
The frontend is now available under http://127.0.0.1:8000. Any changes in regard to Tailwind CSS will be automatically
reflected.

### Testing 

Run all tests with:
```
pytest
```
It's also possible to run unit tests and e2e tests separately. Unit tests can be run with:
```
pytest pdfding/admin pdfding/pdf pdfding/users --cov=pdfding/admin --cov=pdfding/pdf --cov=pdfding/users
```
E2e tests with
```
pytest pdfding/e2e
```

### Code Quality
Formatting is done via `black`: 
```
black .
```

Further code quality checks are done via `flake8`:
```
flake8
```







