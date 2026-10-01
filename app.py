import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

from translations import TEXTOS

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

from flask_wtf.csrf import CSRFProtect

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)


# =========================
# CONFIGURACIÓN
# =========================

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Falta configurar la variable de entorno SECRET_KEY."
    )


app.config["SECRET_KEY"] = SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get(
        "SESSION_COOKIE_SECURE",
        "false"
    ).lower()
    == "true"
)

csrf = CSRFProtect(app)

IDIOMAS_VALIDOS = {
    "es",
    "en"
}


def obtener_idioma():

    idioma = session.get(
        "idioma",
        "es"
    )

    if idioma not in IDIOMAS_VALIDOS:
        idioma = "es"

    return idioma


def traducir(clave):

    idioma = obtener_idioma()

    return TEXTOS.get(
        idioma,
        TEXTOS["es"]
    ).get(
        clave,
        clave
    )


@app.context_processor
def variables_globales():

    return {
        "t": traducir,
        "idioma": obtener_idioma()
    }

PLANES = {
    "basic": {
        "nombre": "Basic",
        "curso": "Fundamentos",
        "precio": 29
    },

    "standard": {
        "nombre": "Standard",
        "curso": "Prospección",
        "precio": 59
    },

    "premium": {
        "nombre": "Premium",
        "curso": "Closing",
        "precio": 99
    }
}

PRIORIDAD_PLANES = {
    "basic": 1,
    "standard": 2,
    "premium": 3
}

ACCESOS_POR_PLAN = {
    "basic": [
        "fundamentos"
    ],

    "standard": [
        "fundamentos",
        "prospeccion"
    ],

    "premium": [
        "fundamentos",
        "prospeccion",
        "closing"
    ]
}

CURSOS = {
    "fundamentos": {
        "numero": "01",
        "nombre": "Fundamentos de Ventas",
        "descripcion": (
            "Aprendé las bases del proceso comercial, "
            "cómo entender al cliente y cómo comunicar valor."
        ),
        "modulos": [
            {
                "numero": "01",
                "titulo": "Introducción a las ventas",
                "descripcion": "Qué significa vender y cómo funciona un proceso comercial.",
                "tipo": "video",
                "archivo": "introduccion.mp4"
            },
            {
                "numero": "02",
                "titulo": "Entender al cliente",
                "descripcion": "Necesidades, problemas y motivaciones de compra.",
                "tipo": "video"
            },
            {
                "numero": "03",
                "titulo": "Comunicar valor",
                "descripcion": "Cómo presentar una oferta con claridad.",
                "tipo": "pdf",
                "archivo": "comunicar-valor.pdf"
            },
            {
                "numero": "04",
                "titulo": "Primeras objeciones",
                "descripcion": "Cómo interpretar dudas y respuestas del cliente.",
                "tipo": "video"
            }
        ]
    },

    "prospeccion": {
        "numero": "02",
        "nombre": "Prospección y Captación",
        "descripcion": (
            "Aprendé a encontrar oportunidades, iniciar conversaciones "
            "y organizar tus potenciales clientes."
        ),
        "modulos": [
            {
                "numero": "01",
                "titulo": "Qué es prospectar",
                "descripcion": "Cómo identificar posibles clientes.",
                "tipo": "video",
                "archivo": "que-es-prospectar.mp4"
            },
            {
                "numero": "02",
                "titulo": "Contacto inicial",
                "descripcion": "Cómo iniciar una conversación comercial.",
                "tipo": "video"
            },
            {
                "numero": "03",
                "titulo": "Scripts de prospección",
                "descripcion": "Ejemplos de mensajes para diferentes situaciones.",
                "tipo": "pdf",
                "archivo": "scripts-prospeccion.pdf"
            },
            {
                "numero": "04",
                "titulo": "Seguimiento",
                "descripcion": "Cómo organizar contactos y oportunidades.",
                "tipo": "video"
            }
        ]
    },

    "closing": {
        "numero": "03",
        "nombre": "Closing y Negociación",
        "descripcion": (
            "Profundizá en objeciones, negociación, cierre "
            "y seguimiento avanzado."
        ),
        "modulos": [
            {
                "numero": "01",
                "titulo": "Preparación del cierre",
                "descripcion": "Cómo detectar intención de compra.",
                "tipo": "video",
                "archivo": "preparacion-cierre.mp4"
            },
            {
                "numero": "02",
                "titulo": "Objeciones avanzadas",
                "descripcion": "Cómo trabajar dudas complejas.",
                "tipo": "video"
            },
            {
                "numero": "03",
                "titulo": "Guía de cierre",
                "descripcion": "Material práctico con ejemplos de cierre.",
                "tipo": "pdf",
                "archivo": "guia-cierre.pdf"
            },
            {
                "numero": "04",
                "titulo": "Negociación",
                "descripcion": "Cómo buscar acuerdos sin perder valor.",
                "tipo": "video"
            }
        ]
    }
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CONTENIDO_PRIVADO = os.path.join(
    BASE_DIR,
    "contenido_privado"
)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(
        BASE_DIR,
        "vendera.db"
    )
)


def get_db_connection():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def crear_base_de_datos():

    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            monto INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'aprobado',
            fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS accesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            recurso TEXT NOT NULL,
            fecha_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(usuario_id, recurso),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )

    connection.commit()

    connection.close()

crear_base_de_datos()

@app.route("/")
def inicio():

    plan_actual = None

    if "usuario_id" in session:

        usuario_id = session["usuario_id"]

        connection = get_db_connection()

        compras = connection.execute(
            """
            SELECT plan
            FROM compras
            WHERE usuario_id = ?
            AND estado = 'aprobado'
            """,
            (usuario_id,)
        ).fetchall()

        connection.close()


        for compra in compras:

            plan_compra = compra["plan"]

            if plan_actual is None:

                plan_actual = plan_compra

            elif PRIORIDAD_PLANES.get(
                plan_compra,
                0
            ) > PRIORIDAD_PLANES.get(
                plan_actual,
                0
            ):

                plan_actual = plan_compra


    return render_template(
        "index.html",
        plan_actual=plan_actual
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    plan = request.args.get("plan", "").lower()

    if request.method == "POST":

        plan = (
            request.form.get("plan")
            or request.args.get("plan")
            or ""
        ).lower()

    if plan not in PLANES:
        plan = None


    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        if not email:
            error = traducir("error_email")

        elif not password:
            error = traducir("error_password")

        else:

            connection = get_db_connection()

            usuario = connection.execute(
                """
                SELECT
                    id,
                    nombre,
                    email,
                    password_hash
                FROM usuarios
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

            connection.close()


            if usuario is None:

                error = traducir("error_login")

            elif not check_password_hash(
                usuario["password_hash"],
                password
            ):

                error = traducir("error_login")

            else:

                idioma_actual = obtener_idioma()

                session.clear()

                session["idioma"] = idioma_actual
                session["usuario_id"] = usuario["id"]
                session["nombre"] = usuario["nombre"]
                session["email"] = usuario["email"]


                if plan:

                    return redirect(
                        url_for(
                            "checkout",
                            plan=plan
                        )
                    )


                return redirect(
                    url_for("inicio")
                )


    return render_template(
        "login.html",
        error=error,
        plan=plan
    )

@app.route("/logout")
def logout():

    idioma_actual = obtener_idioma()

    session.clear()

    session["idioma"] = idioma_actual

    return redirect(
        url_for("inicio")
    )

@app.route("/idioma/<codigo>")
def cambiar_idioma(codigo):

    if codigo in IDIOMAS_VALIDOS:
        session["idioma"] = codigo

    siguiente = request.args.get(
        "next",
        ""
    )

    if (
        not siguiente
        or not siguiente.startswith("/")
        or siguiente.startswith("//")
    ):
        siguiente = url_for("inicio")

    return redirect(siguiente)

@app.route("/checkout/<plan>")
def checkout(plan):

    plan = plan.lower()

    if plan not in PLANES:
        return redirect(
            url_for("inicio")
        )


    if "usuario_id" not in session:

        return redirect(
            url_for(
                "login",
                plan=plan
            )
        )


    plan_seleccionado = PLANES[plan]


    return render_template(
        "checkout.html",
        plan=plan_seleccionado,
        plan_id=plan
    )

@app.route("/confirmar-compra/<plan>", methods=["POST"])
def confirmar_compra(plan):

    plan = plan.lower()

    if "usuario_id" not in session:
        return redirect(
            url_for(
                "login",
                plan=plan
            )
        )

    if plan not in PLANES:
        return redirect(
            url_for("inicio")
        )

    usuario_id = session["usuario_id"]

    plan_seleccionado = PLANES[plan]

    connection = get_db_connection()


    # =========================
    # COMPROBAR PLAN ACTUAL
    # =========================

    compras_usuario = connection.execute(
        """
        SELECT plan
        FROM compras
        WHERE usuario_id = ?
        AND estado = 'aprobado'
        """,
        (usuario_id,)
    ).fetchall()


    nivel_actual = 0

    for compra in compras_usuario:

        nivel_compra = PRIORIDAD_PLANES.get(
            compra["plan"],
            0
        )

        if nivel_compra > nivel_actual:
            nivel_actual = nivel_compra


    nivel_solicitado = PRIORIDAD_PLANES.get(
        plan,
        0
    )


    # Si ya tiene ese plan o uno superior,
    # no permitimos volver a comprarlo.

    if nivel_actual >= nivel_solicitado:

        connection.close()

        return redirect(
            url_for("mis_cursos")
        )


    # =========================
    # COMPROBAR COMPRA DUPLICADA
    # =========================

    compra_existente = connection.execute(
        """
        SELECT id
        FROM compras
        WHERE usuario_id = ?
        AND plan = ?
        AND estado = 'aprobado'
        """,
        (
            usuario_id,
            plan
        )
    ).fetchone()


    if compra_existente is None:

        connection.execute(
            """
            INSERT INTO compras (
                usuario_id,
                plan,
                monto,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                usuario_id,
                plan,
                plan_seleccionado["precio"],
                "aprobado"
            )
        )


        for recurso in ACCESOS_POR_PLAN[plan]:

            connection.execute(
                """
                INSERT OR IGNORE INTO accesos (
                    usuario_id,
                    recurso
                )
                VALUES (?, ?)
                """,
                (
                    usuario_id,
                    recurso
                )
            )


        connection.commit()


    connection.close()


    return redirect(
        url_for("mis_cursos")
    )

@app.route("/mis-cursos")
def mis_cursos():

    if "usuario_id" not in session:
        return redirect(
            url_for("login")
        )

    usuario_id = session["usuario_id"]

    connection = get_db_connection()

    accesos = connection.execute(
        """
        SELECT recurso
        FROM accesos
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    ).fetchall()


    compras = connection.execute(
        """
        SELECT
            plan,
            monto,
            estado,
            fecha_compra
        FROM compras
        WHERE usuario_id = ?
        ORDER BY fecha_compra DESC
        """,
        (usuario_id,)
    ).fetchall()

    connection.close()


    recursos = {
        acceso["recurso"]
        for acceso in accesos
    }


    plan_actual = None

    for compra in compras:

        if compra["estado"] != "aprobado":
            continue

        plan_compra = compra["plan"]

        if plan_actual is None:
            plan_actual = plan_compra

        elif PRIORIDAD_PLANES.get(
            plan_compra,
            0
        ) > PRIORIDAD_PLANES.get(
            plan_actual,
            0
        ):
            plan_actual = plan_compra


    return render_template(
        "mis_cursos.html",
        recursos=recursos,
        compras=compras,
        plan_actual=plan_actual
    )

@app.route("/curso/<curso_id>")
def curso(curso_id):

    if "usuario_id" not in session:
        return redirect(
            url_for("login")
        )

    if curso_id not in CURSOS:
        return redirect(
            url_for("mis_cursos")
        )

    usuario_id = session["usuario_id"]

    connection = get_db_connection()

    acceso = connection.execute(
        """
        SELECT id
        FROM accesos
        WHERE usuario_id = ?
        AND recurso = ?
        """,
        (
            usuario_id,
            curso_id
        )
    ).fetchone()

    connection.close()

    if acceso is None:
        return redirect(
            url_for("mis_cursos")
        )

    curso_seleccionado = CURSOS[curso_id]

    return render_template(
        "curso.html",
        curso=curso_seleccionado,
        curso_id=curso_id
    )

@app.route("/curso/<curso_id>/leccion/<int:numero>")
def leccion(curso_id, numero):

    if "usuario_id" not in session:
        return redirect(
            url_for("login")
        )

    if curso_id not in CURSOS:
        return redirect(
            url_for("mis_cursos")
        )

    usuario_id = session["usuario_id"]

    connection = get_db_connection()

    acceso = connection.execute(
        """
        SELECT id
        FROM accesos
        WHERE usuario_id = ?
        AND recurso = ?
        """,
        (
            usuario_id,
            curso_id
        )
    ).fetchone()

    connection.close()

    if acceso is None:
        return redirect(
            url_for("mis_cursos")
        )

    curso_seleccionado = CURSOS[curso_id]

    if numero < 1 or numero > len(curso_seleccionado["modulos"]):
        return redirect(
            url_for(
                "curso",
                curso_id=curso_id
            )
        )

    modulo = curso_seleccionado["modulos"][numero - 1]

    return render_template(
        "leccion.html",
        curso=curso_seleccionado,
        curso_id=curso_id,
        modulo=modulo,
        numero=numero
    )

@app.route("/recurso/<curso_id>/<int:numero>")
def recurso_privado(curso_id, numero):

    if "usuario_id" not in session:
        return redirect(
            url_for("login")
        )

    if curso_id not in CURSOS:
        return redirect(
            url_for("mis_cursos")
        )

    usuario_id = session["usuario_id"]

    connection = get_db_connection()

    acceso = connection.execute(
        """
        SELECT id
        FROM accesos
        WHERE usuario_id = ?
        AND recurso = ?
        """,
        (
            usuario_id,
            curso_id
        )
    ).fetchone()

    connection.close()

    if acceso is None:
        return redirect(
            url_for("mis_cursos")
        )

    curso_seleccionado = CURSOS[curso_id]

    if numero < 1 or numero > len(curso_seleccionado["modulos"]):
        return redirect(
            url_for(
                "curso",
                curso_id=curso_id
            )
        )

    modulo = curso_seleccionado["modulos"][numero - 1]

    archivo = modulo.get("archivo")

    if not archivo:
        return redirect(
            url_for(
                "leccion",
                curso_id=curso_id,
                numero=numero
            )
        )

    carpeta_curso = os.path.join(
        CONTENIDO_PRIVADO,
        curso_id
    )

    return send_from_directory(
        carpeta_curso,
        archivo
    )

@app.route("/registro", methods=["GET", "POST"])
def registro():

    error = None

    plan = request.args.get("plan", "").lower()

    if request.method == "POST":
        plan = request.form.get("plan", "").lower()

    if plan not in PLANES:
        plan = None


    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        if not nombre:
            error = traducir("error_nombre")

        elif not email:
            error = traducir("error_email")

        elif not password:
            error = traducir("error_password")

        elif len(password) < 8:
            error = traducir("error_password_corta")

        elif password != confirm_password:
            error = traducir("error_passwords")


        if error is None:

            password_hash = generate_password_hash(
                password
            )

            connection = get_db_connection()

            usuario_existente = connection.execute(
                """
                SELECT id
                FROM usuarios
                WHERE email = ?
                """,
                (email,)
            ).fetchone()


            if usuario_existente:

                error = traducir("error_email_existente")

            else:

                connection.execute(
                    """
                    INSERT INTO usuarios (
                        nombre,
                        email,
                        password_hash
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        nombre,
                        email,
                        password_hash
                    )
                )

                connection.commit()

                connection.close()

                return redirect(
                    url_for(
                        "login",
                        plan=plan
                    )
                )


            connection.close()


    return render_template(
        "registro.html",
        error=error,
        plan=plan
    )


if __name__ == "__main__":

    debug_local = (
        os.environ.get(
            "FLASK_DEBUG",
            "false"
        ).lower()
        == "true"
    )

    app.run(
        debug=debug_local
    )