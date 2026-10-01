<p align="center">
  <img src="static/img/logo-vendera-blanco.png" alt="Vendera Academy" width="180">
</p>

<h1 align="center">Vendera Academy</h1>

<p align="center">
  A bilingual sales academy web application built as a full-stack portfolio project with Flask, SQLite, HTML, CSS and JavaScript.
</p>

<p align="center">
  <a href="https://vendera-academy.onrender.com"><strong>Live Demo</strong></a>
</p>

## About the project

Vendera Academy is a fictional online sales academy created to demonstrate a complete web application flow: landing page, authentication, simulated checkout, plan-based access control, protected course resources and a responsive bilingual interface.

The project is designed as a portfolio application. Payments are simulated and no real charges are processed.

## Features

- Responsive landing page for desktop, tablet and mobile
- Spanish / English language switcher
- User registration and login
- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Session-based authentication
- Simulated checkout flow
- Hierarchical plan access:
  - **Basic** → Sales Fundamentals
  - **Standard** → Fundamentals + Prospecting
  - **Premium** → Fundamentals + Prospecting + Closing
- Protected course, video and PDF resources
- User dashboard with unlocked courses and demo purchase history
- SQLite database initialization on startup
- Environment-based configuration for development and production
- Production deployment with Gunicorn on Render

## Tech stack

### Backend
- Python
- Flask
- SQLite
- Flask-WTF
- Werkzeug
- python-dotenv
- Gunicorn

### Frontend
- HTML5
- CSS3
- JavaScript
- Jinja templates

### Deployment
- GitHub
- Render

## Project structure

```text
Vendera-Academy/
├── app.py
├── translations.py
├── requirements.txt
├── contenido_privado/
│   ├── fundamentos/
│   ├── prospeccion/
│   └── closing/
├── static/
│   ├── css/
│   ├── img/
│   ├── js/
│   └── video/
└── templates/
    ├── index.html
    ├── login.html
    ├── registro.html
    ├── checkout.html
    ├── mis_cursos.html
    ├── curso.html
    └── leccion.html