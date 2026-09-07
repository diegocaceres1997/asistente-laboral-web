import io
import json
import os
import re
from pathlib import Path

import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Asistente Laboral",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLOR_PRINCIPAL = "#1B304A"
COLOR_SECUNDARIO = "#B78A3E"
COLOR_FONDO = "#F7F9FC"
COLOR_TEXTO = "#1F2937"

BASE_DIR = Path(__file__).resolve().parent
LOGO_CANDIDATOS = [
    BASE_DIR / "ism logo.jpg",
    BASE_DIR / "ism logo.jpeg",
    BASE_DIR / "logo.png",
]


def buscar_logo():
    for ruta in LOGO_CANDIDATOS:
        if ruta.exists():
            return ruta
    return None


st.markdown(
    f"""
    <style>
        .stApp {{ background: {COLOR_FONDO}; }}
        .block-container {{ max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }}
        h1, h2, h3 {{ color: {COLOR_PRINCIPAL}; }}
        div[data-testid="stSidebar"] {{ background: #EEF3F8; }}
        div[data-testid="stSidebar"] h1,
        div[data-testid="stSidebar"] h2,
        div[data-testid="stSidebar"] h3 {{ color: {COLOR_PRINCIPAL}; }}
        .hero {{
            background: white;
            border: 1px solid #DFE7F0;
            border-radius: 18px;
            padding: 26px 28px;
            margin-bottom: 20px;
            box-shadow: 0 3px 14px rgba(27,48,74,.06);
        }}
        .hero-title {{
            font-size: 2.1rem;
            line-height: 1.15;
            font-weight: 800;
            color: {COLOR_PRINCIPAL};
            margin-bottom: 8px;
        }}
        .hero-subtitle {{ color: #526170; font-size: 1rem; }}
        .card {{
            background: white;
            border: 1px solid #E1E7EF;
            border-radius: 15px;
            padding: 18px;
            min-height: 118px;
            box-shadow: 0 2px 10px rgba(27,48,74,.05);
        }}
        .card-title {{ font-size: 1.05rem; font-weight: 700; color: {COLOR_PRINCIPAL}; }}
        .card-text {{ color: #607080; font-size: .94rem; margin-top: 7px; }}
        .section-note {{
            background: #F0F5FA;
            border-left: 4px solid {COLOR_SECUNDARIO};
            padding: 12px 14px;
            border-radius: 8px;
            margin: 4px 0 18px 0;
            color: #465665;
        }}
        .institutional {{ font-size: .88rem; color: #5C6875; line-height: 1.55; }}
        .gold-line {{ height: 3px; background: {COLOR_SECUNDARIO}; border-radius: 3px; margin: 8px 0 18px 0; }}
        div.stButton > button {{ border-radius: 9px; font-weight: 650; }}
        div.stDownloadButton > button {{
            background: {COLOR_PRINCIPAL};
            color: white;
            border: 0;
            border-radius: 9px;
            font-weight: 700;
        }}
        div.stDownloadButton > button:hover {{ color: white; border: 0; }}

        /* Ajustes generales de legibilidad */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        h1, h2, h3 {{
            color: #1B304A !important;
        }}

        /* Mejoras responsive para celulares y tablets */
        @media (max-width: 768px) {{
            .block-container {{
                max-width: 100%;
                padding-top: 0.8rem;
                padding-left: 0.9rem;
                padding-right: 0.9rem;
                padding-bottom: 2rem;
            }}

            .hero {{
                padding: 18px 18px;
                border-radius: 15px;
                margin-bottom: 14px;
            }}

            .hero-title {{
                font-size: 1.72rem;
                line-height: 1.12;
                margin-bottom: 10px;
            }}

            .hero-subtitle {{
                font-size: 0.98rem;
                line-height: 1.55;
            }}

            .card {{
                min-height: auto;
                padding: 16px;
                margin-bottom: 10px;
            }}

            .card-title {{
                font-size: 1rem;
                line-height: 1.3;
            }}

            .card-text {{
                font-size: 0.93rem;
                line-height: 1.5;
            }}

            .section-note {{
                padding: 11px 12px;
                font-size: 0.94rem;
            }}

            section.main div[data-testid="stImage"] img {{
                width: 88px !important;
                max-width: 88px !important;
                height: auto !important;
            }}

            div[data-testid="stHorizontalBlock"] {{
                gap: 0.75rem;
            }}

            div.stButton > button,
            div.stDownloadButton > button {{
                min-height: 46px;
                font-size: 0.98rem;
            }}

            textarea, input {{
                font-size: 16px !important;
            }}

            .institutional {{
                font-size: 0.82rem;
            }}
        }}

        @media (max-width: 480px) {{
            .hero-title {{
                font-size: 1.48rem;
            }}

            .hero-subtitle {{
                font-size: 0.94rem;
            }}

            .block-container {{
                padding-left: 0.7rem;
                padding-right: 0.7rem;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DATOS / ESTADO
# ============================================================


def datos_vacios():
    return {
        "personales": {
            "nombre": "",
            "apellido": "",
            "fecha_nacimiento": "",
            "ciudad": "",
            "provincia": "",
            "pais": "Argentina",
            "telefono": "",
            "email": "",
            "linkedin": "",
            "licencia": "No",
            "movilidad": "No",
        },
        "objetivo": {
            "primer_empleo": "No",
            "trabajo_buscado": "",
            "areas_interes": "",
            "modalidad": "Indistinto",
            "disponibilidad": "",
            "jornada_completa": "Sí",
            "viajar": "No",
            "mudarse": "No",
        },
        "experiencias": [],
        "educacion": [],
        "cursos": [],
        "habilidades": {
            "informaticas": [],
            "laborales": [],
            "otras": "",
        },
        "idiomas": [],
        "referencias": "Disponibles a solicitud",
    }


if "datos" not in st.session_state:
    st.session_state.datos = datos_vacios()


datos = st.session_state.datos

# ============================================================
# UTILIDADES
# ============================================================


def limpio(valor):
    if valor is None:
        return ""
    texto = str(valor).strip()
    if texto.lower() in {"", "ninguno", "ninguna", "no aplica", "n/a", "-"}:
        return ""
    return texto


def texto_titulo(valor):
    texto = limpio(valor)
    if not texto:
        return ""
    return texto[0].upper() + texto[1:]


def lista_legible(items):
    return ", ".join([limpio(x) for x in items if limpio(x)])


def nombre_completo():
    p = datos["personales"]
    return " ".join(x for x in [limpio(p.get("nombre")), limpio(p.get("apellido"))] if x) or "Currículum Vitae"


def json_actual():
    return json.dumps(datos, ensure_ascii=False, indent=2).encode("utf-8")




# ============================================================
# ORIENTACIÓN LABORAL SEGURA (BASE WEB)
# ============================================================

def texto_perfil_completo(datos_cv):
    partes = []
    p = datos_cv.get("personales", {})
    o = datos_cv.get("objetivo", {})
    partes.extend([
        limpio(o.get("trabajo_buscado")),
        limpio(o.get("areas_interes")),
        limpio(o.get("disponibilidad")),
        limpio(o.get("modalidad")),
    ])
    for exp in datos_cv.get("experiencias", []):
        partes.extend([limpio(exp.get(k)) for k in ("tipo", "empresa", "puesto", "tareas", "herramientas", "logros")])
    for edu in datos_cv.get("educacion", []):
        partes.extend([limpio(edu.get(k)) for k in ("nivel", "institucion", "titulo", "estado")])
    for curso in datos_cv.get("cursos", []):
        partes.extend([limpio(curso.get(k)) for k in ("nombre", "institucion")])
    hab = datos_cv.get("habilidades", {})
    partes.extend(hab.get("informaticas", []))
    partes.extend(hab.get("laborales", []))
    partes.append(limpio(hab.get("otras")))
    for idi in datos_cv.get("idiomas", []):
        partes.extend([
            limpio(idi.get("idioma")), limpio(idi.get("comprension")),
            limpio(idi.get("escritura")), limpio(idi.get("conversacion"))
        ])
    partes.extend([limpio(p.get("licencia")), limpio(p.get("movilidad"))])
    return " ".join(x for x in partes if x).lower()


def fortalezas_declaradas(datos_cv, limite=7):
    salida = []
    hab = datos_cv.get("habilidades", {})
    for x in hab.get("laborales", []) + hab.get("informaticas", []):
        x = limpio(x)
        if x and x not in salida:
            salida.append(x)
    for exp in datos_cv.get("experiencias", []):
        tareas = limpio(exp.get("tareas"))
        if tareas:
            for trozo in tareas.replace(";", ",").split(","):
                trozo = texto_titulo(trozo.strip().rstrip("."))
                if trozo and trozo not in salida:
                    salida.append(trozo)
    return salida[:limite]


def analizar_perfil_seguro(datos_cv):
    o = datos_cv.get("objetivo", {})
    objetivo = limpio(o.get("trabajo_buscado"))
    areas = limpio(o.get("areas_interes"))
    disponibilidad = limpio(o.get("disponibilidad"))
    tiene_exp = bool(datos_cv.get("experiencias"))
    tiene_form = bool(datos_cv.get("educacion") or datos_cv.get("cursos"))
    fortalezas = fortalezas_declaradas(datos_cv)

    frases = []
    if objetivo:
        frases.append(f"Su objetivo laboral se orienta a {objetivo}.")
    elif areas:
        frases.append(f"Sus áreas de interés declaradas son {areas}.")
    else:
        frases.append("Todavía no se definió un objetivo laboral específico.")
    if tiene_exp:
        frases.append("Cuenta con experiencia laboral declarada que aporta conocimientos prácticos para su búsqueda de empleo.")
    if tiene_form:
        frases.append("Además, posee formación y/o capacitaciones registradas en su perfil.")
    if disponibilidad:
        frases.append(f"Disponibilidad declarada: {disponibilidad}.")

    faltantes = []
    if not objetivo and not areas:
        faltantes.append("Definir el trabajo buscado o las áreas de interés.")
    if not datos_cv.get("experiencias"):
        faltantes.append("Agregar experiencia, prácticas, emprendimientos o actividades relevantes si corresponde.")
    if not fortalezas:
        faltantes.append("Registrar habilidades que realmente posea.")
    if not faltantes:
        faltantes.append("El perfil contiene información suficiente para realizar una orientación inicial.")

    lineas = ["PERFIL PROFESIONAL", "", " ".join(frases), "", "FORTALEZAS", ""]
    lineas += [f"• {x}" for x in fortalezas] if fortalezas else ["• Aún no hay fortalezas suficientes cargadas."]
    lineas += ["", "PARA COMPLETAR EL PERFIL", ""]
    lineas += [f"• {x}" for x in faltantes]
    return "\n".join(lineas)


def trabajos_recomendados(datos_cv):
    texto = texto_perfil_completo(datos_cv)
    candidatos = []
    reglas = [
        (("venta", "comercio", "cliente", "caja", "cobro", "stock"), ["Vendedor/a", "Atención al cliente", "Cajero/a", "Repositor/a"]),
        (("administr", "document", "excel", "word", "oficina", "archivo"), ["Auxiliar administrativo/a", "Asistente administrativo/a", "Recepcionista"]),
        (("informática", "informatica", "soporte", "comput", "program", "sistema"), ["Soporte informático inicial", "Operador/a de sistemas", "Asistente de soporte técnico"]),
        (("redes sociales", "diseño", "diseno", "comunicación", "comunicacion", "contenido"), ["Asistente de comunicación", "Community manager junior", "Asistente de contenidos"]),
        (("depósito", "deposito", "mercadería", "mercaderia", "logística", "logistica"), ["Auxiliar de depósito", "Control de stock", "Repositor/a"]),
    ]
    for claves, puestos in reglas:
        if any(k in texto for k in claves):
            for puesto in puestos:
                if puesto not in candidatos:
                    candidatos.append(puesto)

    if not candidatos:
        objetivo = limpio(datos_cv.get("objetivo", {}).get("trabajo_buscado"))
        if objetivo:
            candidatos.append(objetivo)
        for puesto in ["Atención al cliente", "Auxiliar administrativo/a", "Asistente general"]:
            if puesto not in candidatos:
                candidatos.append(puesto)

    candidatos = candidatos[:5]
    palabras = []
    o = datos_cv.get("objetivo", {})
    for fuente in [limpio(o.get("trabajo_buscado")), limpio(o.get("areas_interes"))]:
        if fuente:
            palabras.append(fuente)
    palabras.extend(datos_cv.get("habilidades", {}).get("laborales", [])[:4])
    palabras = [x for i, x in enumerate(palabras) if x and x not in palabras[:i]]

    lineas = ["TRABAJOS RECOMENDADOS", ""]
    lineas += [f"{i}. {p}" for i, p in enumerate(candidatos, 1)]
    lineas += ["", "PALABRAS CLAVE PARA BUSCAR", "", "• " + (", ".join(palabras) if palabras else "empleo, primer empleo, oportunidades laborales")]
    lineas += ["", "POR QUÉ ENCAJAN CON TU PERFIL", "", "Estas opciones se relacionan con las tareas, intereses y habilidades que cargaste en tu perfil. Revisá siempre los requisitos de cada aviso antes de postularte."]
    return "\n".join(lineas)


def analizar_oferta_seguro(datos_cv, oferta):
    oferta_l = (oferta or "").lower()
    if not oferta_l.strip():
        return "Pegá primero el texto de una oferta laboral para poder analizarla."

    perfil_l = texto_perfil_completo(datos_cv)
    categorias = [
        ("Atención al cliente", ["atención al cliente", "atencion al cliente", "cliente", "público", "publico"]),
        ("Manejo de caja o cobros", ["caja", "cobro", "cobranza", "posnet"]),
        ("Organización de mercadería o stock", ["stock", "mercadería", "mercaderia", "reposición", "reposicion"]),
        ("Conocimientos de informática", ["informática", "informatica", "computación", "computacion", "excel", "word", "sistemas"]),
        ("Experiencia o interés en ventas", ["venta", "vendedor", "comercio"]),
        ("Tareas administrativas", ["administrativo", "administrativa", "documentación", "documentacion", "archivo"]),
        ("Redes sociales / comunicación", ["redes sociales", "comunicación", "comunicacion", "contenido"]),
    ]
    coincidencias, pendientes = [], []
    for nombre, claves in categorias:
        pide = any(k in oferta_l for k in claves)
        tiene = any(k in perfil_l for k in claves)
        if pide and tiene:
            coincidencias.append(nombre)
        elif pide:
            pendientes.append(nombre + " (la oferta lo solicita y no está declarado en el perfil)")

    requisitos_generales = [
        ("Responsabilidad", ["responsable", "responsabilidad"]),
        ("Predisposición", ["predisposición", "predisposicion"]),
        ("Comunicación", ["comunicación", "comunicacion", "comunicativo", "comunicativa"]),
        ("Disponibilidad horaria", ["disponibilidad horaria", "horarios rotativos", "turnos rotativos"]),
    ]
    for nombre, claves in requisitos_generales:
        if any(k in oferta_l for k in claves) and not any(k in perfil_l for k in claves):
            pendientes.append(nombre + " (no está declarado explícitamente en el perfil)")

    if len(coincidencias) >= 4:
        nivel = "ALTA"
        reco = "Tu perfil presenta varias coincidencias con la oferta, por lo que sería razonable postularte. Revisá los requisitos pendientes antes de enviar tu CV."
    elif len(coincidencias) >= 2:
        nivel = "MEDIA"
        reco = "Hay coincidencias relevantes, aunque conviene revisar los requisitos pendientes antes de postularte."
    else:
        nivel = "BAJA"
        reco = "Por ahora se observan pocas coincidencias declaradas. Podés postularte si cumplís realmente los requisitos, pero no conviene agregar información al CV que no sea verdadera."

    lineas = ["ANÁLISIS DE LA OFERTA", "", f"COMPATIBILIDAD: {nivel}", "", "COINCIDENCIAS", ""]
    lineas += [f"• {x}" for x in coincidencias] if coincidencias else ["• No se detectaron coincidencias claras con los datos cargados."]
    lineas += ["", "REQUISITOS A REVISAR", ""]
    lineas += [f"• {x}" for x in pendientes] if pendientes else ["• No se detectaron requisitos pendientes evidentes en el texto analizado."]
    lineas += ["", "RECOMENDACIÓN", "", reco]
    return "\n".join(lineas)


def respuesta_asistente(datos_cv, pregunta):
    q = (pregunta or "").strip().lower()
    if not q:
        return "Escribí una consulta sobre tu CV, tu perfil, trabajos posibles o una oferta laboral."
    if any(x in q for x in ["qué trabajos", "que trabajos", "trabajo puedo", "empleos", "puestos"]):
        return trabajos_recomendados(datos_cv)
    if any(x in q for x in ["perfil", "fortaleza", "fortalezas", "mejorar mi perfil"]):
        return analizar_perfil_seguro(datos_cv)
    if any(x in q for x in ["cv", "currículum", "curriculum"]):
        faltan = []
        p = datos_cv.get("personales", {})
        if not limpio(p.get("nombre")) or not limpio(p.get("apellido")):
            faltan.append("nombre y apellido")
        if not limpio(p.get("email")):
            faltan.append("correo electrónico")
        if not datos_cv.get("educacion"):
            faltan.append("educación")
        if faltan:
            return "Para fortalecer el CV, revisá estos datos antes de descargarlo: " + ", ".join(faltan) + ". Solo agregá información verdadera."
        return "Tu CV ya tiene los datos básicos cargados. Revisá la sección '9. Vista previa y PDF' antes de descargarlo y comprobá que toda la información sea correcta."
    return (
        "Puedo orientarte sobre tu perfil laboral, los trabajos que podrías buscar y la preparación de tu CV. "
        "En esta etapa web respondo usando exclusivamente los datos que cargaste, sin inventar experiencias, estudios ni habilidades."
    )


# ============================================================
# IA ONLINE (GROQ) + RESPALDO SEGURO
# ============================================================

MODELO_GROQ = "qwen/qwen3.6-27b"

def perfil_para_ia(datos_cv):
    """Devuelve solo información profesional útil; excluye datos de contacto y fecha de nacimiento."""
    return {
        "objetivo_laboral": {
            "primer_empleo": limpio(datos_cv.get("objetivo", {}).get("primer_empleo")),
            "trabajo_buscado": limpio(datos_cv.get("objetivo", {}).get("trabajo_buscado")),
            "areas_interes": limpio(datos_cv.get("objetivo", {}).get("areas_interes")),
            "modalidad": limpio(datos_cv.get("objetivo", {}).get("modalidad")),
            "disponibilidad": limpio(datos_cv.get("objetivo", {}).get("disponibilidad")),
            "jornada_completa": limpio(datos_cv.get("objetivo", {}).get("jornada_completa")),
            "viajar": limpio(datos_cv.get("objetivo", {}).get("viajar")),
            "mudarse": limpio(datos_cv.get("objetivo", {}).get("mudarse")),
        },
        "experiencias": [
            {
                "tipo": limpio(x.get("tipo")),
                "puesto": limpio(x.get("puesto")),
                "tareas": limpio(x.get("tareas")),
                "herramientas": limpio(x.get("herramientas")),
                "logros": limpio(x.get("logros")),
            }
            for x in datos_cv.get("experiencias", [])
        ],
        "educacion": [
            {
                "nivel": limpio(x.get("nivel")),
                "titulo": limpio(x.get("titulo")),
                "estado": limpio(x.get("estado")),
            }
            for x in datos_cv.get("educacion", [])
        ],
        "cursos": [
            {
                "nombre": limpio(x.get("nombre")),
                "anio": limpio(x.get("anio")),
            }
            for x in datos_cv.get("cursos", [])
        ],
        "habilidades": {
            "informaticas": datos_cv.get("habilidades", {}).get("informaticas", []),
            "laborales": datos_cv.get("habilidades", {}).get("laborales", []),
            "otras": limpio(datos_cv.get("habilidades", {}).get("otras")),
        },
        "idiomas": [
            {
                "idioma": limpio(x.get("idioma")),
                "comprension": limpio(x.get("comprension")),
                "escritura": limpio(x.get("escritura")),
                "conversacion": limpio(x.get("conversacion")),
            }
            for x in datos_cv.get("idiomas", [])
        ],
        "licencia_conducir": limpio(datos_cv.get("personales", {}).get("licencia")),
        "movilidad_propia": limpio(datos_cv.get("personales", {}).get("movilidad")),
    }


def clave_groq():
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


def consultar_ia_web(instruccion, consulta, max_tokens=900):
    """Retorna (respuesta, True) si Groq responde; (None, False) para usar el respaldo local."""
    api_key = clave_groq()
    if Groq is None or not api_key:
        return None, False
    try:
        cliente = Groq(api_key=api_key)
        respuesta = cliente.chat.completions.create(
            model=MODELO_GROQ,
            messages=[
                {"role": "system", "content": instruccion},
                {"role": "user", "content": consulta},
            ],
            temperature=0.2,
            max_completion_tokens=max_tokens,
        )
        texto = (respuesta.choices[0].message.content or "").strip()

        # Algunos modelos de razonamiento pueden incluir su proceso interno
        # entre etiquetas <think>...</think>. Ese contenido no se muestra
        # al usuario: conservamos únicamente la respuesta final.
        texto = re.sub(
            r"<think\b[^>]*>.*?</think>",
            "",
            texto,
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()

        # Protección adicional por si quedara alguna etiqueta suelta.
        texto = re.sub(r"</?think\b[^>]*>", "", texto, flags=re.IGNORECASE).strip()

        return (texto, True) if texto else (None, False)
    except Exception:
        return None, False


INSTRUCCION_IA = """
Sos un asistente de orientación laboral y elaboración de currículum vitae. Respondé en español claro,
profesional y útil. Debés basarte EXCLUSIVAMENTE en la información declarada en el perfil que recibís.
Nunca inventes experiencia, estudios, títulos, cursos, habilidades, idiomas, certificaciones, logros ni datos personales.
Si un requisito o capacidad no aparece en el perfil, indicá expresamente que no está declarado.
Podés sugerir puestos, mejoras de redacción, palabras clave y próximos pasos, pero distinguí siempre una sugerencia
de un dato real del usuario. No solicites ni uses datos sensibles innecesarios.
No muestres razonamientos internos, procesos de pensamiento, etiquetas <think> ni explicaciones sobre cómo llegaste
a la respuesta. Entregá únicamente la respuesta final destinada al usuario.
""".strip()


def analizar_perfil_ia(datos_cv):
    perfil = json.dumps(perfil_para_ia(datos_cv), ensure_ascii=False, indent=2)
    consulta = f"""
Analizá este perfil laboral:
{perfil}

Entregá una respuesta breve y organizada con estos apartados:
1. PERFIL PROFESIONAL
2. FORTALEZAS DECLARADAS
3. ASPECTOS A COMPLETAR O MEJORAR
4. RECOMENDACIÓN PARA LA BÚSQUEDA LABORAL
No agregues capacidades que no estén declaradas.
"""
    respuesta, uso_ia = consultar_ia_web(INSTRUCCION_IA, consulta)
    return (respuesta if respuesta else analizar_perfil_seguro(datos_cv)), uso_ia


def trabajos_recomendados_ia(datos_cv):
    perfil = json.dumps(perfil_para_ia(datos_cv), ensure_ascii=False, indent=2)
    consulta = f"""
A partir únicamente de este perfil:
{perfil}

Proponé hasta 5 puestos o tipos de empleo razonables para buscar. Para cada uno explicá en una frase
qué dato declarado del perfil respalda la recomendación. Después agregá palabras clave de búsqueda y
una advertencia para revisar los requisitos reales de cada aviso. No afirmes que la persona cumple un
requisito que no figure en el perfil.
"""
    respuesta, uso_ia = consultar_ia_web(INSTRUCCION_IA, consulta)
    return (respuesta if respuesta else trabajos_recomendados(datos_cv)), uso_ia


def analizar_oferta_ia(datos_cv, oferta):
    if not (oferta or "").strip():
        return "Pegá primero el texto de una oferta laboral para poder analizarla.", False
    perfil = json.dumps(perfil_para_ia(datos_cv), ensure_ascii=False, indent=2)
    consulta = f"""
PERFIL DECLARADO:
{perfil}

OFERTA LABORAL:
{oferta}

Compará la oferta con el perfil. Indicá:
- compatibilidad general (ALTA, MEDIA o BAJA) con una explicación prudente;
- coincidencias comprobables;
- requisitos que la oferta pide y que NO están declarados;
- recomendación final para postularse o completar información.
Nunca conviertas un requisito de la oferta en una habilidad del usuario.
"""
    respuesta, uso_ia = consultar_ia_web(INSTRUCCION_IA, consulta, max_tokens=1100)
    return (respuesta if respuesta else analizar_oferta_seguro(datos_cv, oferta)), uso_ia


def respuesta_asistente_ia(datos_cv, pregunta, historial=None):
    q = (pregunta or "").strip()
    if not q:
        return "Escribí una consulta sobre tu CV, tu perfil, trabajos posibles o una oferta laboral.", False
    perfil = json.dumps(perfil_para_ia(datos_cv), ensure_ascii=False, indent=2)
    contexto = ""
    if historial:
        ultimos = historial[-6:]
        contexto = "\
".join(f"{rol}: {mensaje}" for rol, mensaje in ultimos)
    consulta = f"""
PERFIL PROFESIONAL DECLARADO:
{perfil}

CONTEXTO RECIENTE DEL CHAT:
{contexto or 'Sin mensajes anteriores relevantes.'}

CONSULTA DEL USUARIO:
{q}

Respondé de forma concreta y orientadora. Si la pregunta requiere un dato que no está en el perfil,
decí que no está declarado en lugar de asumirlo.
"""
    respuesta, uso_ia = consultar_ia_web(INSTRUCCION_IA, consulta, max_tokens=850)
    return (respuesta if respuesta else respuesta_asistente(datos_cv, q)), uso_ia


# ============================================================
# PDF
# ============================================================


def crear_pdf_cv(datos_cv):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Currículum Vitae",
        author="Asistente Laboral",
    )

    azul = colors.HexColor(COLOR_PRINCIPAL)
    dorado = colors.HexColor(COLOR_SECUNDARIO)
    gris = colors.HexColor("#536171")
    gris_claro = colors.HexColor("#D9E1E8")

    estilos = getSampleStyleSheet()
    estilo_nombre = ParagraphStyle(
        "NombreCV",
        parent=estilos["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=azul,
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    estilo_contacto = ParagraphStyle(
        "ContactoCV",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9.4,
        leading=13,
        textColor=gris,
    )
    estilo_seccion = ParagraphStyle(
        "SeccionCV",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14,
        textColor=azul,
        spaceBefore=10,
        spaceAfter=5,
    )
    estilo_item = ParagraphStyle(
        "ItemCV",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9.6,
        leading=13.4,
        textColor=colors.HexColor("#26323E"),
        spaceAfter=3,
    )
    estilo_item_bold = ParagraphStyle(
        "ItemBoldCV",
        parent=estilo_item,
        fontName="Helvetica-Bold",
        fontSize=10.1,
        textColor=azul,
        spaceAfter=2,
    )
    estilo_pequeno = ParagraphStyle(
        "PequenoCV",
        parent=estilo_item,
        fontSize=8.9,
        leading=12,
        textColor=gris,
    )

    historia = []
    p = datos_cv.get("personales", {})
    o = datos_cv.get("objetivo", {})

    nombre = " ".join(
        x for x in [limpio(p.get("nombre")), limpio(p.get("apellido"))] if x
    ) or "CURRÍCULUM VITAE"

    contacto = []
    ubicacion = ", ".join(
        x for x in [limpio(p.get("ciudad")), limpio(p.get("provincia")), limpio(p.get("pais"))] if x
    )
    if ubicacion:
        contacto.append(ubicacion)
    for campo in ["telefono", "email", "linkedin"]:
        valor = limpio(p.get(campo))
        if valor and valor.lower() != "no":
            contacto.append(valor)

    logo = buscar_logo()
    bloque_nombre = [Paragraph(nombre.upper(), estilo_nombre)]
    if contacto:
        bloque_nombre.append(Paragraph(" &nbsp; | &nbsp; ".join(contacto), estilo_contacto))

    if logo:
        try:
            img = Image(str(logo), width=26 * mm, height=26 * mm)
            tabla_encabezado = Table([[img, bloque_nombre]], colWidths=[32 * mm, 145 * mm])
            tabla_encabezado.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            historia.append(tabla_encabezado)
        except Exception:
            historia.extend(bloque_nombre)
    else:
        historia.extend(bloque_nombre)

    linea = Table([[""]], colWidths=[177 * mm], rowHeights=[2.2 * mm])
    linea.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), dorado)]))
    historia += [Spacer(1, 3 * mm), linea, Spacer(1, 4 * mm)]

    def titulo_seccion(titulo):
        return [
            Paragraph(titulo.upper(), estilo_seccion),
            Table(
                [[""]],
                colWidths=[177 * mm],
                rowHeights=[0.45 * mm],
                style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), dorado)]),
            ),
            Spacer(1, 1.6 * mm),
        ]

    # Perfil / objetivo
    perfil_partes = []
    trabajo = limpio(o.get("trabajo_buscado"))
    areas = limpio(o.get("areas_interes"))
    if trabajo:
        perfil_partes.append(f"Objetivo laboral: <b>{trabajo}</b>.")
    if areas:
        perfil_partes.append(f"Áreas de interés: {areas}.")
    if limpio(o.get("modalidad")):
        perfil_partes.append(f"Modalidad preferida: {limpio(o.get('modalidad'))}.")
    if limpio(o.get("disponibilidad")):
        perfil_partes.append(f"Disponibilidad: {limpio(o.get('disponibilidad'))}.")
    if perfil_partes:
        historia += titulo_seccion("Perfil y objetivo laboral")
        historia.append(Paragraph(" ".join(perfil_partes), estilo_item))

    # Experiencia
    experiencias = datos_cv.get("experiencias", [])
    if experiencias:
        historia += titulo_seccion("Experiencia laboral")
        for exp in experiencias:
            puesto = texto_titulo(exp.get("puesto"))
            empresa = texto_titulo(exp.get("empresa"))
            tipo = texto_titulo(exp.get("tipo"))
            if puesto and empresa:
                encabezado = f"{puesto} — {empresa}"
            else:
                encabezado = puesto or empresa or tipo or "Experiencia"
            elementos = [Paragraph(encabezado, estilo_item_bold)]

            fecha = " – ".join(x for x in [limpio(exp.get("inicio")), texto_titulo(exp.get("fin"))] if x)
            ubic = limpio(exp.get("ciudad"))
            metadatos = " | ".join(x for x in [ubic, fecha] if x)
            if metadatos:
                elementos.append(Paragraph(metadatos, estilo_pequeno))

            tareas = limpio(exp.get("tareas"))
            herramientas = limpio(exp.get("herramientas"))
            logros = limpio(exp.get("logros"))
            if tareas:
                elementos.append(Paragraph(texto_titulo(tareas), estilo_item))
            if herramientas:
                elementos.append(Paragraph(f"<b>Herramientas:</b> {herramientas}", estilo_item))
            if logros:
                elementos.append(Paragraph(f"<b>Logros / responsabilidades:</b> {logros}", estilo_item))
            elementos.append(Spacer(1, 2.2 * mm))
            historia.append(KeepTogether(elementos))

    # Educación
    educacion = datos_cv.get("educacion", [])
    if educacion:
        historia += titulo_seccion("Educación")
        for edu in educacion:
            titulo = texto_titulo(edu.get("titulo")) or texto_titulo(edu.get("nivel")) or "Formación"
            institucion = texto_titulo(edu.get("institucion"))
            estado = texto_titulo(edu.get("estado"))
            fechas = " – ".join(x for x in [limpio(edu.get("inicio")), limpio(edu.get("fin"))] if x)
            elementos = [Paragraph(titulo, estilo_item_bold)]
            segunda = " | ".join(x for x in [institucion, estado, fechas] if x)
            if segunda:
                elementos.append(Paragraph(segunda, estilo_pequeno))
            elementos.append(Spacer(1, 2 * mm))
            historia.append(KeepTogether(elementos))

    # Cursos
    cursos = datos_cv.get("cursos", [])
    if cursos:
        historia += titulo_seccion("Cursos y capacitaciones")
        for curso in cursos:
            nombre_curso = texto_titulo(curso.get("nombre")) or "Curso"
            institucion = texto_titulo(curso.get("institucion"))
            anio = limpio(curso.get("anio"))
            duracion = limpio(curso.get("duracion"))
            elementos = [Paragraph(f"• {nombre_curso}", estilo_item_bold)]
            detalle = " | ".join(x for x in [institucion, anio, duracion] if x)
            if detalle:
                elementos.append(Paragraph(detalle, estilo_pequeno))
            elementos.append(Spacer(1, 1.4 * mm))
            historia.append(KeepTogether(elementos))

    # Habilidades
    habilidades = datos_cv.get("habilidades", {})
    info = lista_legible(habilidades.get("informaticas", []))
    lab = lista_legible(habilidades.get("laborales", []))
    otras = limpio(habilidades.get("otras"))
    if info or lab or otras:
        historia += titulo_seccion("Habilidades")
        if info:
            historia.append(Paragraph(f"<b>Informáticas:</b> {info}", estilo_item))
        if lab:
            historia.append(Paragraph(f"<b>Laborales:</b> {lab}", estilo_item))
        if otras:
            historia.append(Paragraph(f"<b>Otras:</b> {otras}", estilo_item))

    # Idiomas
    idiomas = datos_cv.get("idiomas", [])
    if idiomas:
        historia += titulo_seccion("Idiomas")
        for idi in idiomas:
            nombre_idioma = texto_titulo(idi.get("idioma")) or "Idioma"
            comp = limpio(idi.get("comprension"))
            escr = limpio(idi.get("escritura"))
            conv = limpio(idi.get("conversacion"))
            niveles = [comp, escr, conv]
            if comp and comp == escr == conv:
                detalle = comp
            else:
                partes = []
                if comp:
                    partes.append(f"Comprensión: {comp}")
                if escr:
                    partes.append(f"Escritura: {escr}")
                if conv:
                    partes.append(f"Conversación: {conv}")
                detalle = ", ".join(partes)
            historia.append(Paragraph(f"• <b>{nombre_idioma}</b>{': ' + detalle if detalle else ''}", estilo_item))

    # Información adicional
    adicionales = []
    if limpio(p.get("licencia")) == "Sí":
        adicionales.append("Licencia de conducir")
    if limpio(p.get("movilidad")) == "Sí":
        adicionales.append("Movilidad propia")
    if limpio(o.get("jornada_completa")):
        adicionales.append(f"Jornada completa: {limpio(o.get('jornada_completa'))}")
    if limpio(o.get("viajar")) == "Sí":
        adicionales.append("Disponibilidad para viajar")
    if limpio(o.get("mudarse")) == "Sí":
        adicionales.append("Disponibilidad para mudarse")

    referencias = limpio(datos_cv.get("referencias"))
    if adicionales or referencias:
        historia += titulo_seccion("Información adicional")
        if adicionales:
            historia.append(Paragraph(" • ".join(adicionales), estilo_item))
        if referencias:
            historia.append(Paragraph(f"<b>Referencias:</b> {referencias}", estilo_item))

    def pie_pagina(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(gris_claro)
        canvas.line(16 * mm, 10 * mm, 194 * mm, 10 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(gris)
        canvas.drawString(16 * mm, 6.4 * mm, "Currículum generado con Asistente Laboral")
        canvas.drawRightString(194 * mm, 6.4 * mm, f"Página {doc_obj.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# ENCABEZADO / SIDEBAR
# ============================================================

logo = buscar_logo()

with st.sidebar:
    if logo:
        st.image(str(logo), width=105)
    st.markdown("## Asistente Laboral")
    st.caption("Versión web · IA online")
    pagina = st.radio(
        "Navegación",
        [
            "Inicio",
            "1. Datos personales",
            "2. Objetivo laboral",
            "3. Experiencia",
            "4. Educación",
            "5. Cursos",
            "6. Habilidades",
            "7. Idiomas",
            "8. Referencias",
            "9. Vista previa y PDF",
            "10. Analizar perfil laboral",
            "11. Trabajos recomendados",
            "12. Analizar oferta laboral",
            "13. Asistente laboral",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown(
        """
        <div class="institutional">
        <b>3º año - Profesorado de Informática</b><br>
        Instituto Superior del Profesorado General José de San Martín<br>
        Espacio curricular: Didáctica Específica II<br><br>
        <b>Creadores:</b><br>
        Cáceres, Diego<br>
        Insaurralde, Micaela<br>
        Jara, Florencia<br>
        Pintos, Cecilia<br>
        Sotelo, Octavio
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PÁGINAS
# ============================================================

if pagina == "Inicio":
    col_logo, col_texto = st.columns([1, 7])
    with col_logo:
        if logo:
            st.image(str(logo), width=110)
        else:
            st.markdown("# 💼")
    with col_texto:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-title">Asistente Inteligente para la Orientación Laboral</div>
                <div class="hero-subtitle">
                    Completá tu perfil laboral paso a paso, organizá la información de tu currículum
                    y generá un CV profesional en PDF.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### ¿Qué podés hacer en esta versión?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><div class="card-title">📄 Crear Currículum Vitae</div><div class="card-text">Cargá tus datos personales, experiencia, educación, cursos, habilidades e idiomas.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">🧾 Generar PDF</div><div class="card-text">Descargá un currículum profesional listo para revisar, imprimir o enviar.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><div class="card-title">🤖 Orientación laboral</div><div class="card-text">Analizá tu perfil, descubrí trabajos posibles y compará tu información con una oferta laboral.</div></div>', unsafe_allow_html=True)

    st.info("Los datos permanecen en la sesión actual del navegador. Para las funciones de IA se envía únicamente información profesional necesaria; no se envían correo, teléfono ni fecha de nacimiento. La aplicación mantiene un modo de respaldo si la IA online no está disponible.")

elif pagina == "1. Datos personales":
    st.header("1. Datos personales")
    st.markdown('<div class="section-note">Ingresá únicamente información que quieras incluir en tu perfil laboral.</div>', unsafe_allow_html=True)
    p = datos["personales"]

    c1, c2 = st.columns(2)
    with c1:
        p["nombre"] = st.text_input("Nombre", p["nombre"])
        p["fecha_nacimiento"] = st.text_input("Fecha de nacimiento", p["fecha_nacimiento"], placeholder="dd/mm/aaaa")
        p["ciudad"] = st.text_input("Ciudad", p["ciudad"])
        p["pais"] = st.text_input("País", p["pais"])
        p["email"] = st.text_input("Correo electrónico", p["email"])
        p["licencia"] = st.selectbox("¿Tenés licencia de conducir?", ["No", "Sí"], index=1 if p["licencia"] == "Sí" else 0)
    with c2:
        p["apellido"] = st.text_input("Apellido", p["apellido"])
        p["provincia"] = st.text_input("Provincia", p["provincia"])
        p["telefono"] = st.text_input("Teléfono", p["telefono"])
        p["linkedin"] = st.text_input("LinkedIn u otro perfil profesional (opcional)", p["linkedin"])
        p["movilidad"] = st.selectbox("¿Tenés movilidad propia?", ["No", "Sí"], index=1 if p["movilidad"] == "Sí" else 0)

    st.success("Los datos quedan guardados automáticamente mientras la aplicación permanezca abierta.")

elif pagina == "2. Objetivo laboral":
    st.header("2. Objetivo laboral")
    st.markdown('<div class="section-note">Definí qué tipo de trabajo buscás y tus preferencias de disponibilidad.</div>', unsafe_allow_html=True)
    o = datos["objetivo"]

    c1, c2 = st.columns(2)
    with c1:
        o["primer_empleo"] = st.selectbox("¿Buscás tu primer empleo?", ["No", "Sí"], index=1 if o["primer_empleo"] == "Sí" else 0)
        o["trabajo_buscado"] = st.text_input("¿Qué trabajo buscás?", o["trabajo_buscado"], placeholder="Ej.: Ventas, administración, soporte técnico")
        o["areas_interes"] = st.text_input("Áreas de interés", o["areas_interes"], placeholder="Ej.: Comercio, informática, atención al público")
        modalidades = ["Indistinto", "Presencial", "Remoto", "Híbrido"]
        o["modalidad"] = st.selectbox("Modalidad preferida", modalidades, index=modalidades.index(o["modalidad"]) if o["modalidad"] in modalidades else 0)
    with c2:
        o["disponibilidad"] = st.text_input("Disponibilidad horaria", o["disponibilidad"], placeholder="Ej.: Mañana, tarde, disponibilidad completa")
        o["jornada_completa"] = st.selectbox("¿Jornada completa?", ["Sí", "No"], index=0 if o["jornada_completa"] == "Sí" else 1)
        o["viajar"] = st.selectbox("¿Disponibilidad para viajar?", ["No", "Sí"], index=1 if o["viajar"] == "Sí" else 0)
        o["mudarse"] = st.selectbox("¿Disponibilidad para mudarse?", ["No", "Sí"], index=1 if o["mudarse"] == "Sí" else 0)

elif pagina == "3. Experiencia":
    st.header("3. Experiencia laboral")
    st.markdown('<div class="section-note">También podés incluir trabajos independientes, emprendimientos, trabajo familiar, pasantías, prácticas o voluntariados.</div>', unsafe_allow_html=True)

    with st.form("form_experiencia", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de experiencia", ["Empleo formal", "Trabajo independiente", "Emprendimiento", "Pasantía / práctica", "Voluntariado", "Trabajo familiar", "Otro"])
            empresa = st.text_input("Empresa, organización o lugar")
            puesto = st.text_input("Puesto, función o actividad")
            ciudad = st.text_input("Ciudad")
        with c2:
            inicio = st.text_input("Fecha de inicio (mes/año)")
            fin = st.text_input("Fecha de finalización (mes/año o Actualidad)")
            tareas = st.text_area("¿Qué tareas realizabas?", height=120)
            herramientas = st.text_area("Herramientas, máquinas, programas o sistemas utilizados", height=80)
            logros = st.text_area("Logros o responsabilidades importantes (opcional)", height=80)
        agregar = st.form_submit_button("➕ Agregar experiencia", use_container_width=True)
        if agregar:
            if empresa.strip() or puesto.strip():
                datos["experiencias"].append({
                    "tipo": tipo,
                    "empresa": empresa.strip(),
                    "puesto": puesto.strip(),
                    "ciudad": ciudad.strip(),
                    "inicio": inicio.strip(),
                    "fin": fin.strip(),
                    "tareas": tareas.strip(),
                    "herramientas": herramientas.strip(),
                    "logros": logros.strip(),
                })
                st.success("Experiencia agregada correctamente.")
                st.rerun()
            else:
                st.warning("Ingresá al menos la empresa/lugar o el puesto/actividad.")

    if datos["experiencias"]:
        st.subheader("Experiencias cargadas")
        for i, exp in enumerate(datos["experiencias"]):
            titulo = " — ".join(x for x in [exp.get("puesto", ""), exp.get("empresa", "")] if x) or f"Experiencia {i+1}"
            with st.expander(titulo, expanded=False):
                st.write(f"**Tipo:** {exp.get('tipo', '')}")
                if exp.get("ciudad"): st.write(f"**Ciudad:** {exp['ciudad']}")
                if exp.get("inicio") or exp.get("fin"): st.write(f"**Período:** {exp.get('inicio','')} – {exp.get('fin','')}")
                if exp.get("tareas"): st.write(f"**Tareas:** {exp['tareas']}")
                if exp.get("herramientas"): st.write(f"**Herramientas:** {exp['herramientas']}")
                if exp.get("logros"): st.write(f"**Logros / responsabilidades:** {exp['logros']}")
                if st.button("🗑️ Eliminar", key=f"del_exp_{i}"):
                    datos["experiencias"].pop(i)
                    st.rerun()

elif pagina == "4. Educación":
    st.header("4. Educación")
    st.markdown('<div class="section-note">Cargá tus estudios aunque estén incompletos o todavía estén en curso.</div>', unsafe_allow_html=True)

    with st.form("form_educacion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nivel = st.selectbox("Nivel educativo", ["Primario", "Secundario", "Terciario", "Universitario", "Posgrado", "Otro"])
            institucion = st.text_input("Institución")
            titulo = st.text_input("Título, carrera u orientación")
        with c2:
            estado = st.selectbox("Estado", ["Finalizado", "En curso", "Incompleto"])
            inicio = st.text_input("Año de inicio")
            fin = st.text_input("Año de finalización o estimado")
        agregar = st.form_submit_button("➕ Agregar formación", use_container_width=True)
        if agregar:
            if institucion.strip() or titulo.strip():
                datos["educacion"].append({
                    "nivel": nivel,
                    "institucion": institucion.strip(),
                    "titulo": titulo.strip(),
                    "estado": estado,
                    "inicio": inicio.strip(),
                    "fin": fin.strip(),
                })
                st.success("Formación agregada correctamente.")
                st.rerun()
            else:
                st.warning("Ingresá al menos una institución o un estudio.")

    if datos["educacion"]:
        st.subheader("Formación cargada")
        for i, edu in enumerate(datos["educacion"]):
            titulo_item = edu.get("titulo") or edu.get("institucion") or f"Formación {i+1}"
            with st.expander(titulo_item):
                st.write(f"**Nivel:** {edu.get('nivel','')}")
                st.write(f"**Institución:** {edu.get('institucion','')}")
                st.write(f"**Estado:** {edu.get('estado','')}")
                st.write(f"**Período:** {edu.get('inicio','')} – {edu.get('fin','')}")
                if st.button("🗑️ Eliminar", key=f"del_edu_{i}"):
                    datos["educacion"].pop(i)
                    st.rerun()

elif pagina == "5. Cursos":
    st.header("5. Cursos y capacitaciones")
    st.markdown('<div class="section-note">Agregá cursos, capacitaciones o certificados que puedan aportar a tu perfil.</div>', unsafe_allow_html=True)

    with st.form("form_curso", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre_curso = st.text_input("Nombre del curso o capacitación")
            institucion = st.text_input("Institución u organización")
            anio = st.text_input("Año")
        with c2:
            duracion = st.text_input("Duración (opcional)")
            certificado = st.selectbox("¿Tenés certificado?", ["Sí", "No"])
        agregar = st.form_submit_button("➕ Agregar curso", use_container_width=True)
        if agregar:
            if nombre_curso.strip():
                datos["cursos"].append({
                    "nombre": nombre_curso.strip(),
                    "institucion": institucion.strip(),
                    "anio": anio.strip(),
                    "duracion": duracion.strip(),
                    "certificado": certificado,
                })
                st.success("Curso agregado correctamente.")
                st.rerun()
            else:
                st.warning("Ingresá el nombre del curso.")

    if datos["cursos"]:
        st.subheader("Cursos cargados")
        for i, curso in enumerate(datos["cursos"]):
            with st.expander(curso.get("nombre") or f"Curso {i+1}"):
                st.write(f"**Institución:** {curso.get('institucion','')}")
                st.write(f"**Año:** {curso.get('anio','')}")
                if curso.get("duracion"): st.write(f"**Duración:** {curso['duracion']}")
                st.write(f"**Certificado:** {curso.get('certificado','')}")
                if st.button("🗑️ Eliminar", key=f"del_curso_{i}"):
                    datos["cursos"].pop(i)
                    st.rerun()

elif pagina == "6. Habilidades":
    st.header("6. Habilidades")
    st.markdown('<div class="section-note">Marcá únicamente herramientas o tareas que realmente sabés utilizar o realizar.</div>', unsafe_allow_html=True)

    h = datos["habilidades"]
    opciones_info = ["Word", "Excel", "PowerPoint", "Correo electrónico", "Redes sociales", "Sistemas administrativos", "Programación", "Diseño gráfico", "Videollamadas"]
    opciones_laborales = ["Atención al público", "Ventas", "Manejo de caja", "Organización de documentación", "Tareas administrativas", "Trabajo en equipo", "Supervisión de personas", "Control de stock", "Atención telefónica", "Manejo de herramientas o maquinaria", "Conducción de vehículos", "Organización de tareas"]

    c1, c2 = st.columns(2)
    with c1:
        h["informaticas"] = st.multiselect("Herramientas informáticas", opciones_info, default=[x for x in h["informaticas"] if x in opciones_info])
    with c2:
        h["laborales"] = st.multiselect("Tareas y habilidades laborales", opciones_laborales, default=[x for x in h["laborales"] if x in opciones_laborales])
    h["otras"] = st.text_area("Otras cosas que sabés hacer", value=h["otras"], height=110)

elif pagina == "7. Idiomas":
    st.header("7. Idiomas")
    st.markdown('<div class="section-note">Agregá los idiomas que conocés y el nivel que más se aproxime a tu situación.</div>', unsafe_allow_html=True)

    with st.form("form_idioma", clear_on_submit=True):
        idioma = st.text_input("Idioma")
        c1, c2, c3 = st.columns(3)
        niveles = ["Básico", "Intermedio", "Avanzado", "Nativo"]
        with c1: comprension = st.selectbox("Comprensión", niveles)
        with c2: escritura = st.selectbox("Escritura", niveles)
        with c3: conversacion = st.selectbox("Conversación", niveles)
        agregar = st.form_submit_button("➕ Agregar idioma", use_container_width=True)
        if agregar:
            if idioma.strip():
                datos["idiomas"].append({
                    "idioma": idioma.strip(),
                    "comprension": comprension,
                    "escritura": escritura,
                    "conversacion": conversacion,
                })
                st.success("Idioma agregado correctamente.")
                st.rerun()
            else:
                st.warning("Ingresá el idioma.")

    if datos["idiomas"]:
        st.subheader("Idiomas cargados")
        for i, idi in enumerate(datos["idiomas"]):
            with st.expander(idi.get("idioma") or f"Idioma {i+1}"):
                st.write(f"**Comprensión:** {idi.get('comprension','')}")
                st.write(f"**Escritura:** {idi.get('escritura','')}")
                st.write(f"**Conversación:** {idi.get('conversacion','')}")
                if st.button("🗑️ Eliminar", key=f"del_idioma_{i}"):
                    datos["idiomas"].pop(i)
                    st.rerun()

elif pagina == "8. Referencias":
    st.header("8. Referencias")
    st.markdown('<div class="section-note">Podés indicar si contás con referencias laborales o personales. No es obligatorio publicar datos de contacto en el CV.</div>', unsafe_allow_html=True)
    datos["referencias"] = st.text_area("Referencias", value=datos.get("referencias", "Disponibles a solicitud"), height=120)

elif pagina == "9. Vista previa y PDF":
    st.header("9. Vista previa y PDF")

    p = datos["personales"]
    o = datos["objetivo"]
    st.markdown(f"## {nombre_completo()}")
    contacto = [limpio(p.get("ciudad")), limpio(p.get("provincia")), limpio(p.get("telefono")), limpio(p.get("email"))]
    contacto = [x for x in contacto if x]
    if contacto:
        st.caption(" · ".join(contacto))

    st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)

    if limpio(o.get("trabajo_buscado")) or limpio(o.get("areas_interes")):
        st.subheader("Perfil y objetivo laboral")
        partes = []
        if limpio(o.get("trabajo_buscado")): partes.append(limpio(o.get("trabajo_buscado")))
        if limpio(o.get("areas_interes")): partes.append(f"Áreas de interés: {limpio(o.get('areas_interes'))}")
        st.write(". ".join(partes))

    if datos["experiencias"]:
        st.subheader("Experiencia laboral")
        for exp in datos["experiencias"]:
            st.markdown(f"**{exp.get('puesto') or exp.get('empresa') or 'Experiencia'}**")
            meta = " | ".join(x for x in [exp.get("empresa", ""), exp.get("ciudad", ""), " – ".join(y for y in [exp.get("inicio", ""), exp.get("fin", "")] if y)] if x)
            if meta: st.caption(meta)
            if exp.get("tareas"): st.write(exp["tareas"])

    if datos["educacion"]:
        st.subheader("Educación")
        for edu in datos["educacion"]:
            st.markdown(f"**{edu.get('titulo') or edu.get('nivel') or 'Formación'}**")
            st.caption(" | ".join(x for x in [edu.get("institucion", ""), edu.get("estado", ""), " – ".join(y for y in [edu.get("inicio", ""), edu.get("fin", "")] if y)] if x))

    if datos["cursos"]:
        st.subheader("Cursos y capacitaciones")
        for curso in datos["cursos"]:
            st.write(f"• **{curso.get('nombre','')}**" + (f" — {curso.get('institucion')}" if curso.get("institucion") else ""))

    h = datos["habilidades"]
    if h.get("informaticas") or h.get("laborales") or limpio(h.get("otras")):
        st.subheader("Habilidades")
        if h.get("informaticas"): st.write("**Informáticas:** " + lista_legible(h["informaticas"]))
        if h.get("laborales"): st.write("**Laborales:** " + lista_legible(h["laborales"]))
        if limpio(h.get("otras")): st.write("**Otras:** " + limpio(h["otras"]))

    if datos["idiomas"]:
        st.subheader("Idiomas")
        for idi in datos["idiomas"]:
            st.write(f"• **{idi.get('idioma','')}** — Comprensión: {idi.get('comprension','')}, Escritura: {idi.get('escritura','')}, Conversación: {idi.get('conversacion','')}")

    st.divider()
    pdf = crear_pdf_cv(datos)
    nombre_archivo = (nombre_completo().replace(" ", "_") or "curriculum") + ".pdf"

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📄 Descargar CV en PDF",
            data=pdf,
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "💾 Descargar respaldo del perfil (JSON)",
            data=json_actual(),
            file_name="perfil_laboral.json",
            mime="application/json",
            use_container_width=True,
        )

    st.caption("El PDF se genera exclusivamente con la información que vos cargaste. No se inventan experiencias, estudios ni habilidades.")


elif pagina == "10. Analizar perfil laboral":
    st.header("10. Analizar perfil laboral")
    st.markdown('<div class="section-note">La IA analiza únicamente la información profesional que cargaste. Los datos de contacto y la fecha de nacimiento no se envían al modelo.</div>', unsafe_allow_html=True)
    if st.button("🔎 Analizar mi perfil", type="primary", use_container_width=True):
        with st.spinner("Analizando tu perfil con IA..."):
            resultado, uso_ia = analizar_perfil_ia(datos)
        st.session_state["analisis_perfil_web"] = resultado
        st.session_state["analisis_perfil_modo_ia"] = uso_ia
    if st.session_state.get("analisis_perfil_web"):
        if st.session_state.get("analisis_perfil_modo_ia"):
            st.caption("✨ Análisis generado con IA online.")
        else:
            st.warning("La IA online no estuvo disponible. Se utilizó el análisis seguro de respaldo.")
        st.text_area("Resultado", st.session_state["analisis_perfil_web"], height=420, disabled=True)

elif pagina == "11. Trabajos recomendados":
    st.header("11. ¿Qué trabajos puedo buscar?")
    st.markdown('<div class="section-note">La IA propone opciones a partir de tus intereses, experiencias y habilidades declaradas, sin inventar conocimientos.</div>', unsafe_allow_html=True)
    if st.button("💼 Ver trabajos recomendados", type="primary", use_container_width=True):
        with st.spinner("Buscando opciones compatibles con tu perfil..."):
            resultado, uso_ia = trabajos_recomendados_ia(datos)
        st.session_state["trabajos_web"] = resultado
        st.session_state["trabajos_modo_ia"] = uso_ia
    if st.session_state.get("trabajos_web"):
        if st.session_state.get("trabajos_modo_ia"):
            st.caption("✨ Recomendaciones generadas con IA online.")
        else:
            st.warning("La IA online no estuvo disponible. Se utilizaron las recomendaciones de respaldo.")
        st.text_area("Resultado", st.session_state["trabajos_web"], height=440, disabled=True)

elif pagina == "12. Analizar oferta laboral":
    st.header("12. Analizar una oferta laboral")
    st.markdown('<div class="section-note">Pegá el texto de una oferta. La IA comparará sus requisitos con tu perfil y marcará como no declarado aquello que no figure en tus datos.</div>', unsafe_allow_html=True)
    oferta = st.text_area("Texto de la oferta laboral", height=260, placeholder="Pegá acá la publicación o los requisitos del puesto...")
    if st.button("🧾 Analizar oferta", type="primary", use_container_width=True):
        with st.spinner("Comparando la oferta con tu perfil..."):
            resultado, uso_ia = analizar_oferta_ia(datos, oferta)
        st.session_state["oferta_web"] = resultado
        st.session_state["oferta_modo_ia"] = uso_ia
    if st.session_state.get("oferta_web"):
        if st.session_state.get("oferta_modo_ia"):
            st.caption("✨ Oferta analizada con IA online.")
        elif oferta.strip():
            st.warning("La IA online no estuvo disponible. Se utilizó el análisis seguro de respaldo.")
        st.text_area("Resultado del análisis", st.session_state["oferta_web"], height=500, disabled=True)

elif pagina == "13. Asistente laboral":
    st.header("13. Asistente laboral con IA")
    st.markdown('<div class="section-note">Consultá sobre tu CV, tu perfil, trabajos posibles o una oferta. El asistente recibe solo la información profesional necesaria y tiene prohibido inventar antecedentes.</div>', unsafe_allow_html=True)
    if "chat_web" not in st.session_state:
        st.session_state.chat_web = []
    for rol, mensaje in st.session_state.chat_web:
        with st.chat_message(rol):
            st.write(mensaje)
    pregunta = st.chat_input("Escribí tu consulta laboral...")
    if pregunta:
        historial_previo = list(st.session_state.chat_web)
        st.session_state.chat_web.append(("user", pregunta))
        with st.spinner("Pensando..."):
            respuesta, uso_ia = respuesta_asistente_ia(datos, pregunta, historial_previo)
        st.session_state.chat_web.append(("assistant", respuesta))
        st.session_state["chat_modo_ia"] = uso_ia
        st.rerun()
    if st.session_state.get("chat_web"):
        if st.session_state.get("chat_modo_ia"):
            st.caption("✨ Asistente conectado a IA online.")
        else:
            st.caption("Modo de respaldo activo: respuestas basadas en reglas seguras del perfil.")
