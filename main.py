# main.py
import os
import json
import streamlit as st

# Función auxiliar para convertir a entero de forma segura
def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Importa funciones de los módulos internos
from src.ingestion.audio_extractor import transcribe_audio
from src.ingestion.video_processor import process_video
from src.ingestion.doc_extractor import extract_text_pdf, extract_text_docx
from src.nlp.entity_extraction import extract_entities
from src.nlp.groq_llm import refine_extraction
from src.generator.ppt_generator import generate_ppt
from src.utils.file_utils import ensure_directory_exists

# Directorios de trabajo
UPLOAD_DIR = "data/uploads"
PROCESSED_DIR = "data/processed"
TEMPLATE_PATH = os.path.abspath("templates/ppt_template.pptx")

# Asegura la existencia de los directorios necesarios
ensure_directory_exists(UPLOAD_DIR)
ensure_directory_exists(PROCESSED_DIR)

# Configuración de la página Streamlit
st.set_page_config(page_title="Automatización de Propuestas Comerciales - AUTODOC MONDAY", layout="wide")
st.title("Automatización de Propuestas Comerciales - AUTODOC MONDAY")

# Inicializar session_state para guardar la ruta del PPT generado
if "ppt_file" not in st.session_state:
    st.session_state["ppt_file"] = None

# Selección del tipo de archivo: Audio, Video, PDF, DOCX o ingreso manual
file_type = st.selectbox("Seleccione el tipo de archivo a subir", ["Audio", "Video", "PDF", "DOCX", "Input manual"])
uploaded_file = None
if file_type != "Input manual":
    if file_type == "DOCX":
        accepted_formats = ["docx"]
    elif file_type == "PDF":
        accepted_formats = ["pdf"]
    elif file_type == "Video":
        accepted_formats = ["mp4", "mov", "avi"]
    elif file_type == "Audio":
        accepted_formats = ["mp3", "wav"]
    else:
        accepted_formats = None
    uploaded_file = st.file_uploader(f"Suba el archivo {file_type}", type=accepted_formats)

extracted_text = ""
if uploaded_file is not None:
    # Guarda el archivo subido en el directorio correspondiente
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Archivo subido correctamente.")

    if file_type == "Audio":
        with st.spinner("Transcribiendo audio, por favor espere..."):
            extracted_text = transcribe_audio(file_path)
    elif file_type == "Video":
        with st.spinner("Procesando video: extrayendo audio y analizando diapositivas, por favor espere..."):
            extracted_text = process_video(file_path)
    elif file_type == "PDF":
        with st.spinner("Extrayendo texto de PDF, por favor espere..."):
            extracted_text = extract_text_pdf(file_path)
    elif file_type == "DOCX":
        with st.spinner("Extrayendo texto de DOCX, por favor espere..."):
            extracted_text = extract_text_docx(file_path)

    st.subheader("Texto Extraído")
    st.text_area("Texto extraído", extracted_text, height=200)

    # Extracción inicial 
    initial_data = extract_entities(extracted_text)
    st.subheader("Campos Extraídos Inicialmente")
    st.json(initial_data)

    # Refinamiento mediante Groq (se extrae el bloque JSON de la respuesta)
    refined_data = refine_extraction(extracted_text, initial_data)
    st.subheader("Campos Refinados (Groq API)")
    st.json(refined_data)

    # Formulario para que el usuario revise y edite los campos (incluyendo el campo "emails" para llenado manual)
    st.subheader("Revise y edite los campos si es necesario")
    with st.form("propuesta_form"):
        nombre_empresa = st.text_input("Nombre de la Empresa", value=refined_data.get("nombre_empresa", ""))
        descripcion_empresa = st.text_area("Descripción de la Empresa", value=refined_data.get("descripcion_empresa", ""))
        requerimientos_y_desafios = st.text_area("Requerimientos y Desafíos", value=refined_data.get("requerimientos_y_desafios", ""))
        cantidad_licencias = st.number_input("Cantidad de Licencias", min_value=0, value=safe_int(refined_data.get("cantidad_licencias", 0)))
        vigencia_contrato = st.text_input("Vigencia del Contrato", value=refined_data.get("vigencia_contrato", ""))
        tipo_licencia = st.text_input("Tipo de Licencia", value=refined_data.get("tipo_licencia", ""))
        caracteristicas_principales = st.text_area("Características Principales", value=refined_data.get("caracteristicas_principales", ""))
        tabla_solucion = st.text_input("Tabla Solución", value=refined_data.get("tabla_solucion", ""))
        precio_sub = st.text_input("Precio Sub", value=refined_data.get("precio_sub", ""))
        cantidad_meses = st.number_input("Cantidad de Meses", min_value=0, value=safe_int(refined_data.get("cantidad_meses", 0)))
        servicio_sub = st.checkbox("Servicio Sub", value=(str(refined_data.get("servicio_sub", "False")).lower() == "true"))
        servicio_proyecto = st.checkbox("Servicio Proyecto", value=(str(refined_data.get("servicio_proyecto", "False")).lower() == "true"))
        servicio_soporte = st.checkbox("Servicio Soporte", value=(str(refined_data.get("servicio_soporte", "False")).lower() == "true"))
        lugar_factura_sub = st.text_input("Lugar Facturación Sub", value=refined_data.get("lugar_factura_sub", ""))
        mes_facturacion_sub = st.text_input("Mes Facturación Sub", value=refined_data.get("mes_facturacion_sub", ""))
        modo_pago_sub = st.text_input("Modo de Pago Sub", value=refined_data.get("modo_pago_sub", ""))
        horas_implementacion = st.number_input("Horas Implementación", min_value=0, value=safe_int(refined_data.get("horas_implementacion", 0)))
        duracion_proyecto_implementacion = st.text_input("Duración Proyecto Implementación", value=refined_data.get("duracion_proyecto_implementacion", ""))
        principales_caracteristicas_pi = st.text_area("Principales Características PI", value=refined_data.get("principales_caracteristicas_pi", ""))
        alcances_pi = st.text_area("Alcances PI", value=refined_data.get("alcances_pi", ""))
        confi_capacitacion_cantidad_usr = st.text_input("Capacitación a Usuarios Clave", value=refined_data.get("confi_capacitacion_cantidad_usr", ""))
        duracion_implementacion_pi = st.text_input("Duración Implementación PI", value=refined_data.get("duracion_implementacion_pi", ""))
        hora_de_trabajo_pi = st.number_input("Hora de Trabajo PI", min_value=0, value=safe_int(refined_data.get("hora_de_trabajo_pi", 0)))
        costo_individual_hora_pi = st.text_input("Costo Individual por Hora PI", value=refined_data.get("costo_individual_hora_pi", ""))
        tipo_factura_pi = st.text_input("Tipo de Factura PI", value=refined_data.get("tipo_factura_pi", ""))
        modo_factura_pi = st.text_input("Modo de Factura PI", value=refined_data.get("modo_factura_pi", ""))
        lugar_factura_pi = st.text_input("Lugar de Facturación PI", value=refined_data.get("lugar_factura_pi", ""))
        emails = st.text_area("Contenido de Emails (llenar manualmente)", value="")

        submitted = st.form_submit_button("Generar Propuesta")
        if submitted:
            proposal_data = {
                "nombre_empresa": nombre_empresa,
                "descripcion_empresa": descripcion_empresa,
                "requerimientos_y_desafios": requerimientos_y_desafios,
                "cantidad_licencias": str(cantidad_licencias),
                "vigencia_contrato": vigencia_contrato,
                "tipo_licencia": tipo_licencia,
                "caracteristicas_principales": caracteristicas_principales,
                "tabla_solucion": tabla_solucion,
                "precio_sub": precio_sub,
                "cantidad_meses": str(cantidad_meses),
                "servicio_sub": str(servicio_sub),
                "servicio_proyecto": str(servicio_proyecto),
                "servicio_soporte": str(servicio_soporte),
                "lugar_factura_sub": lugar_factura_sub,
                "mes_facturacion_sub": mes_facturacion_sub,
                "modo_pago_sub": modo_pago_sub,
                "horas_implementacion": str(horas_implementacion),
                "duracion_proyecto_implementacion": duracion_proyecto_implementacion,
                "principales_caracteristicas_pi": principales_caracteristicas_pi,
                "alcances_pi": alcances_pi,
                "confi_capacitacion_cantidad_usr": confi_capacitacion_cantidad_usr,
                "duracion_implementacion_pi": duracion_implementacion_pi,
                "hora_de_trabajo_pi": str(hora_de_trabajo_pi),
                "costo_individual_hora_pi": costo_individual_hora_pi,
                "tipo_factura_pi": tipo_factura_pi,
                "modo_factura_pi": modo_factura_pi,
                "lugar_factura_pi": lugar_factura_pi,
                "emails": emails
            }
            json_path = os.path.join(PROCESSED_DIR, "propuesta.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(proposal_data, jf, indent=2, ensure_ascii=False)
            
            output_ppt = os.path.join(PROCESSED_DIR, "propuesta_generada.pptx")
            try:
                generate_ppt(proposal_data, TEMPLATE_PATH, output_ppt)
                st.success("¡Propuesta generada exitosamente!")
                # Almacena la ruta del PPT generado en session_state para mostrar el botón fuera del form
                st.session_state["ppt_file"] = output_ppt
            except Exception as e:
                st.error(f"Error generando la propuesta: {str(e)}")

# Fuera del formulario, si se ha generado un PPT, se muestra el botón de descarga
if st.session_state.get("ppt_file"):
    with open(st.session_state["ppt_file"], "rb") as f:
        st.download_button("Descargar PPT", f,
                           file_name="propuesta_generada.pptx",
                           mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        
# Caso de ingreso manual (sin archivo subido)
if uploaded_file is None:
    st.info("Por favor, ingrese los datos manualmente en el siguiente formulario:")
    with st.form("manual_form"):
        nombre_empresa = st.text_input("Nombre de la Empresa")
        descripcion_empresa = st.text_area("Descripción de la Empresa")
        requerimientos_y_desafios = st.text_area("Requerimientos y Desafíos")
        cantidad_licencias = st.number_input("Cantidad de Licencias", min_value=0)
        vigencia_contrato = st.text_input("Vigencia del Contrato")
        tipo_licencia = st.text_input("Tipo de Licencia")
        caracteristicas_principales = st.text_area("Características Principales")
        tabla_solucion = st.text_input("Tabla Solución")
        precio_sub = st.text_input("Precio Sub")
        cantidad_meses = st.number_input("Cantidad de Meses", min_value=0)
        servicio_sub = st.checkbox("Servicio Sub")
        servicio_proyecto = st.checkbox("Servicio Proyecto")
        servicio_soporte = st.checkbox("Servicio Soporte")
        lugar_factura_sub = st.text_input("Lugar Facturación Sub")
        mes_facturacion_sub = st.text_input("Mes Facturación Sub")
        modo_pago_sub = st.text_input("Modo de Pago Sub")
        horas_implementacion = st.number_input("Horas Implementación", min_value=0)
        duracion_proyecto_implementacion = st.text_input("Duración Proyecto Implementación")
        principales_caracteristicas_pi = st.text_area("Principales Características PI")
        alcances_pi = st.text_area("Alcances PI")
        confi_capacitacion_cantidad_usr = st.text_input("Capacitación a Usuarios Clave")
        duracion_implementacion_pi = st.text_input("Duración Implementación PI")
        hora_de_trabajo_pi = st.number_input("Hora de Trabajo PI", min_value=0)
        costo_individual_hora_pi = st.text_input("Costo Individual por Hora PI")
        tipo_factura_pi = st.text_input("Tipo de Factura PI")
        modo_factura_pi = st.text_input("Modo de Factura PI")
        lugar_factura_pi = st.text_input("Lugar de Facturación PI")
        emails = st.text_area("Contenido de Emails (llenar manualmente)", value="")
        
        submitted_manual = st.form_submit_button("Generar Propuesta Manualmente")
        if submitted_manual:
            proposal_data = {
                "nombre_empresa": nombre_empresa,
                "descripcion_empresa": descripcion_empresa,
                "requerimientos_y_desafios": requerimientos_y_desafios,
                "cantidad_licencias": str(cantidad_licencias),
                "vigencia_contrato": vigencia_contrato,
                "tipo_licencia": tipo_licencia,
                "caracteristicas_principales": caracteristicas_principales,
                "tabla_solucion": tabla_solucion,
                "precio_sub": precio_sub,
                "cantidad_meses": str(cantidad_meses),
                "servicio_sub": str(servicio_sub),
                "servicio_proyecto": str(servicio_proyecto),
                "servicio_soporte": str(servicio_soporte),
                "lugar_factura_sub": lugar_factura_sub,
                "mes_facturacion_sub": mes_facturacion_sub,
                "modo_pago_sub": modo_pago_sub,
                "horas_implementacion": str(horas_implementacion),
                "duracion_proyecto_implementacion": duracion_proyecto_implementacion,
                "principales_caracteristicas_pi": principales_caracteristicas_pi,
                "alcances_pi": alcances_pi,
                "confi_capacitacion_cantidad_usr": confi_capacitacion_cantidad_usr,
                "duracion_implementacion_pi": duracion_implementacion_pi,
                "hora_de_trabajo_pi": str(hora_de_trabajo_pi),
                "costo_individual_hora_pi": costo_individual_hora_pi,
                "tipo_factura_pi": tipo_factura_pi,
                "modo_factura_pi": modo_factura_pi,
                "lugar_factura_pi": lugar_factura_pi,
                "emails": emails
            }
            json_path = os.path.join(PROCESSED_DIR, "propuesta_manual.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(proposal_data, jf, indent=2, ensure_ascii=False)
            output_ppt = os.path.join(PROCESSED_DIR, "propuesta_manual.pptx")
            try:
                generate_ppt(proposal_data, TEMPLATE_PATH, output_ppt)
                st.success("¡Propuesta generada exitosamente!")
                # Almacena la ruta del archivo generado en session_state para mostrar el botón fuera del form
                st.session_state["ppt_file"] = output_ppt
            except Exception as e:
                st.error(f"Error generando la propuesta: {str(e)}")
    # Fuera del formulario manual, si se ha generado un PPT, se muestra el botón de descarga
    if st.session_state.get("ppt_file"):
        with open(st.session_state["ppt_file"], "rb") as f:
            st.download_button("Descargar PPT", f,
                               file_name="propuesta_generada.pptx",
                               mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
