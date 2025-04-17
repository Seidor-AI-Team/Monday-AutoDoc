# AutoPropuestasMVP

**AutoPropuestasMVP** es un MVP construido con **Streamlit**, **LangChain + Groq**, y **python-pptx**, diseñado para automatizar la creación de propuestas comerciales para el equipo de ventas de Monday.

---

## Características

- **Subida de archivos**: audio, video (se extrae audio), PDF, Word, Excel.  
- **Transcripción**: convierte audio/video a texto (Whisper).  
- **Extracción de entidades**: NER con SpaCy (`EntityRuler`) para detección preliminar.  
- **Refinamiento LLM**: LangChain + Groq para mapear y calcular datos clave.  
- **Generación de PPT**: reemplaza placeholders `{{campo}}` en plantilla con datos extraídos.  
- **Cálculos avanzados**: detalle y totales de suscripciones, horas y costos de implementación.



## Uso

1. Ejecuta la app Streamlit:
   ```bash
   streamlit run main.py
   ```
2. En la interfaz web:
   - Sube audio/video o documentos.  
   - Visualiza la **Extracción preliminar** (SpaCy).  
   - Pulsa **Refinar con LLM** para ver el JSON mapeado.  
   - Haz clic en **Generar PPT** para descargar tu propuesta.

---

## Detalle de Pipelines

### src/ingestion
- **audio_extractor.py**: extrae y transcribe audio.  
- **video_processor.py**: extrae audio de video.  
- **doc_extractor.py**: convierte PDF, DOCX y Excel a texto.

### src/nlp
- **entity_extraction.py**: NER con SpaCy y EntityRuler.  
- **groq_llm.py**: LangChain + Groq para mapear y calcular datos clave.

### src/generator
- **ppt_generator.py**: reemplaza placeholders `{{campo}}` en la plantilla PPT.

### src/utils
- **file_utils.py**: creación de carpetas y guardado de JSON.

### src/app
- **streamlit_app.py**: interfaz de usuario y orquestación de pipelines.

---

## Ejemplo de JSON extraído

```json
{
  "nombre_empresa": "Cedar",
  "descripcion_empresa": "",
  "requerimientos_y_desafios": [],
  "cantidad_licencias": "10",
  "vigencia_contrato": "",
  "tipo_licencia": [],
  "suscripciones": [
    { "producto": "Work Management", "detalle": "5 × $52 × 12", "monto_total_anual": "$3120 + IVA" },
    { "producto": "Service", "detalle": "5 × $62 × 12", "monto_total_anual": "$3720 + IVA" }
  ],
  "total_suscripciones_anual": "$6840 + IVA",
  "horas_implementacion": "40",
  "duracion_proyecto_implementacion": "8 semanas",
  "monto_implementacion_anual": "40 × 1.5 UF + IVA",
  "emails": ""
}
```

---




## Notas
- Usar versión de Python < 3.13 (Acá se usó 3.12)
- Asegúrate de tener instalado el modelo de spaCy para español:  
  `python -m spacy download es_core_news_md`


