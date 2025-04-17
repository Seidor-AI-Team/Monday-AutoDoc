# src/nlp/groq_llm.py
import json
import streamlit as st
from typing import Dict
from src.utils.config import GROQ_API_KEY
from langchain import LLMChain, PromptTemplate
from langchain_groq import ChatGroq


def refine_extraction(text: str, initial_data: Dict) -> Dict:
    """
    Refina la extracción de información para la propuesta comercial de Seidor.
    Utiliza LangChain con el modelo Groq para extraer y preparar dos secciones:
      1. Suscripciones (imagen 1).
      2. Implementación (imagen 2).
    Devuelve solo un JSON con las claves requeridas.
    """
    # Prompt actualizado sin calcular IVA, solo se indica "+ IVA" y escapando llaves literales
    template = """
Eres un asistente experto en generación de propuestas comerciales para Seidor, en español.
Tu tarea es analizar el texto transcrito de reuniones y extraer / calcular toda la información necesaria para rellenar dos secciones de la propuesta:

1. Suscripciones:
   - Lista únicamente los productos que el cliente ha solicitado (1 a 4).
   - Para cada producto, indica:
     * producto: Work Management, CRM, Dev o Service.
     * detalle: calcula (precio por usuario) × (número de usuarios) × 12 meses.
     * monto_total_anual: muestra el resultado del cálculo seguido de ' + IVA'.
   - total_suscripciones_anual: suma de cada monto_total_anual (sin calcular IVA), seguido de ' + IVA'.

2. Implementación:
   - Extrae horas_de_implementacion (número de horas) y duracion_proyecto_implementacion (en semanas).
   - En la diapositiva de implementación reporta:
     * servicio: 'Proyecto de Implementación'.
     * duracion: 'X horas / Y semanas'.
     * valor: '1.5 UF / Hora'.
     * monto_implementacion_anual: muestra 'horas_de_implementacion × 1.5 UF + IVA'.

Instrucciones generales:
- Si no encuentras un dato, deja el campo como cadena vacía ''.
- El campo 'emails' se mantiene siempre vacío.

Devuelve solo un bloque JSON con estas claves exactas:
```json
{{
  "nombre_empresa": "",
  "descripcion_empresa": "",
  "requerimientos_y_desafios": [],  # lista de puntos
  "cantidad_licencias": "",
  "vigencia_contrato": "",
  "tipo_licencia": [],
  "suscripciones": [  # array de objetos por producto
    {{
      "producto": "",
      "detalle": "",
      "monto_total_anual": "<valor> + IVA"
    }}
  ],
  "total_suscripciones_anual": "<suma> + IVA",
  "horas_implementacion": "",
  "duracion_proyecto_implementacion": "",
  "monto_implementacion_anual": "<horas> × 1.5 UF/horas + IVA",
  "emails": ""
}}```

Datos iniciales:
{initial_data}

Texto completo:
{text}
"""
    prompt = PromptTemplate(template=template, input_variables=["initial_data", "text"])

    # Configura el LLM de Groq
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        # Ejecuta la cadena con datos iniciales y texto
        generated = chain.run(
            initial_data=json.dumps(initial_data, ensure_ascii=False),
            text=text
        )
        # Extraer bloque JSON de la respuesta
        start = generated.find("{")
        end = generated.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = generated[start:end+1]
            return json.loads(json_str)
        else:
            return initial_data
    except Exception as e:
        st.error(f"Error refinando extracción con Groq LLMChain: {e}")
        return initial_data
