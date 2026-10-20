# Conversión de una guía .txt a MongoDB

La conversión la hace el front, no un prompt externo:

```bash
cd guia-estudio-front
python scripts/gen_cm2t_json.py <archivo.txt> <clave>
```

La clave es camelCase y tiene que ser la misma en `SUBJECTS`, `VALID_SUBJECTS`, `SUBJECT_FILES` y en `assets/images/originales/<clave>/`. Ejemplo: `ingles2Examen1erTrimestre`. No uses el nombre visible de la materia ni guiones bajos (`conocimiento_del_medio` no es una clave de este proyecto).

El archivo `docs/assets/<clave>.json` es la fuente en el repo. El quiz no lo lee: pide `GET /questions/<clave>`.

## Documento para la colección `questions`

Una pregunta de opción múltiple:

```json
{
  "subject": "ingles2Examen1erTrimestre",
  "category": "Simple Present",
  "type": "multiple-choice",
  "question": "Add \"s\":",
  "answers": [
    { "option": "When the verb ends in S, SS, CH, X, O, Z." },
    { "option": "When subject is HE, SHE or IT.", "correct": true }
  ],
  "correctAnswer": null,
  "audioText": null,
  "image": null,
  "active": true
}
```

Una pregunta escrita. Si trae imagen, `image` es `assets/images/<clave>/<archivo>.jpg` (sin `#`):

```json
{
  "subject": "ingles2Examen1erTrimestre",
  "category": "Simple Present",
  "type": "text-input",
  "question": "She _____ in a hospital. (work)",
  "answers": null,
  "correctAnswer": "works",
  "audioText": null,
  "image": null,
  "active": true
}
```

- Quita `_correcta` del texto. Solo la opción correcta lleva `"correct": true`.
- No incluyas `_id` ni el `id` numérico del txt. Mongo asigna `_id`, y ese es el id que guarda el progreso.
- `Respuesta` del txt va en `correctAnswer` con `type` `text-input` y `answers` en null.
- `Instruccion` y `Subcategoria` no se guardan.

Inserta solo el array de la materia nueva en `questions`.

No corras `python scripts/migrate_questions.py` para agregar una materia: borra y vuelve a insertar cada clave de `SUBJECT_FILES`. Si la clave todavía no está en `VALID_SUBJECTS`, despliega el API antes de probar el quiz; si no, el endpoint responde 404.
