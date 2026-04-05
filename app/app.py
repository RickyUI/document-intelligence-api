from __future__ import annotations

from pathlib import Path

import gradio as gr
import requests


API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 120


def _extract_error(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or "Error desconocido."
    return payload.get("detail") or payload.get("message") or "Error desconocido."


def _format_file_names(files: list[str]) -> str:
    if not files:
        return "No hay documentos cargados."
    return "\n".join(f"{idx + 1}. {name}" for idx, name in enumerate(files))


def _chat_placeholder(indexed: bool, uploaded: bool) -> str:
    if indexed:
        return "Pregunta sobre ingresos, guidance, riesgos, margenes o cualquier dato del documento..."
    if uploaded:
        return "Carga tus archivos para habilitar el chat."
    return "Sube uno o mas PDFs para comenzar."


def _chat_input_hint(indexed: bool, uploaded: bool) -> str:
    return f"{_chat_placeholder(indexed, uploaded)} Enter para enviar, Shift+Enter para nueva linea."


def _session_summary(files: list[str], indexed: bool) -> str:
    file_count = len(files)
    docs_label = f"{file_count} archivo" if file_count == 1 else f"{file_count} archivos"
    load_label = "Completada" if indexed else ("Pendiente" if file_count else "No iniciada")
    chat_label = "Habilitado" if indexed else "Bloqueado"
    return (
        "### Estado general\n"
        f"**Archivos:** {docs_label}  \n"
        f"**Carga al chat:** {load_label}  \n"
        f"**Chat:** {chat_label}"
    )


def upload_files(files):
    if not files:
        empty_files: list[str] = []
        return (
            "Selecciona uno o mas archivos PDF.",
            "Esperando archivos para prepararlos para el chat.",
            empty_files,
            _format_file_names(empty_files),
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=False),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary(empty_files, indexed=False),
        )

    file_handles = []
    uploaded_names = []
    try:
        multipart_files = []
        for file_obj in files:
            file_path = Path(file_obj.name)
            handle = file_path.open("rb")
            file_handles.append(handle)
            multipart_files.append(("files", (file_path.name, handle, "application/pdf")))
            uploaded_names.append(file_path.name)

        response = requests.post(
            f"{API_URL}/upload/",
            files=multipart_files,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        empty_files: list[str] = []
        return (
            f"No se pudo conectar con el backend: {exc}",
            "Revisa la conexion antes de cargar los archivos al chat.",
            empty_files,
            _format_file_names(empty_files),
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=False),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary(empty_files, indexed=False),
        )
    finally:
        for handle in file_handles:
            handle.close()

    if response.status_code != 201:
        empty_files: list[str] = []
        return (
            f"Error al subir archivos: {_extract_error(response)}",
            "No se pueden cargar al chat hasta que la subida sea exitosa.",
            empty_files,
            _format_file_names(empty_files),
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=False),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary(empty_files, indexed=False),
        )

    payload = response.json()
    saved_files = payload.get("files", uploaded_names)
    return (
        payload.get("message", "Documentos subidos correctamente."),
        "Archivos listos. Cargalos al chat para poder hacer preguntas.",
        saved_files,
        _format_file_names(saved_files),
        False,
        gr.update(
            value="",
            interactive=False,
            placeholder=_chat_input_hint(indexed=False, uploaded=True),
        ),
        gr.update(interactive=False),
        [],
        [],
        _session_summary(saved_files, indexed=False),
    )


def index_files(uploaded_files: list[str]):
    if not uploaded_files:
        return (
            "Primero sube al menos un PDF.",
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=False),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary([], indexed=False),
        )

    try:
        response = requests.post(f"{API_URL}/index/", timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        return (
            f"No se pudo indexar: {exc}",
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=True),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary(uploaded_files, indexed=False),
        )

    if response.status_code != 201:
        return (
            f"Error al indexar: {_extract_error(response)}",
            False,
            gr.update(
                value="",
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=True),
            ),
            gr.update(interactive=False),
            [],
            [],
            _session_summary(uploaded_files, indexed=False),
        )

    payload = response.json()
    return (
        payload.get("message", "Archivos cargados correctamente para el chat."),
        True,
        gr.update(
            value="",
            interactive=True,
            placeholder=_chat_input_hint(indexed=True, uploaded=True),
        ),
        gr.update(interactive=True),
        [],
        [],
        _session_summary(uploaded_files, indexed=True),
    )


def ask_question(question: str, history: list[dict], indexed: bool):
    clean_question = (question or "").strip()
    if not indexed or not clean_question:
        return history, "", history

    try:
        response = requests.post(
            f"{API_URL}/query/",
            json={"question": clean_question},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        answer = f"No se pudo consultar el backend: {exc}"
    else:
        if response.status_code == 200:
            payload = response.json()
            sources = payload.get("sources", [])
            sources_block = (
                "\n".join(f"- {source}" for source in sources)
                if sources
                else "- Sin fuentes reportadas"
            )
            answer = f"{payload.get('response', '')}\n\n**Fuentes**\n{sources_block}"
        else:
            answer = f"Error en la consulta: {_extract_error(response)}"

    new_history = history + [
        {"role": "user", "content": clean_question},
        {"role": "assistant", "content": answer},
    ]
    return new_history, "", new_history


def clear_chat(indexed: bool, uploaded_files: list[str]):
    return (
        [],
        [],
        gr.update(
            value="",
            interactive=indexed,
            placeholder=_chat_input_hint(indexed=indexed, uploaded=bool(uploaded_files)),
        ),
    )


theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky",
    neutral_hue="slate",
).set(
    body_background_fill="#f6f8fc",
    block_background_fill="#ffffff",
    block_border_color="#d8e0ef",
    input_background_fill="#f8fafc",
    button_primary_background_fill="#2563eb",
    button_primary_background_fill_hover="#1d4ed8",
    button_secondary_background_fill="#e8eefc",
    button_secondary_background_fill_hover="#dbe6ff",
    body_text_color="#0f172a",
    block_label_text_color="#334155",
    background_fill_secondary="#eef3fb",
)


with gr.Blocks(title="FinWise") as demo:
    uploaded_files = gr.State([])
    indexed = gr.State(False)
    chat_history = gr.State([])

    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown(
                """
                # FinWise
                Analiza reportes financieros, estados contables, earnings calls y otros documentos
                corporativos con busqueda semantica y respuestas fundamentadas en tus propios archivos.
                """
            )
        with gr.Column(scale=1, min_width=180):
            session_summary = gr.Markdown(_session_summary([], indexed=False))

    with gr.Row():
        with gr.Column(scale=1, min_width=320):
            gr.Markdown("## 1. Sube tus archivos")
            file_input = gr.File(
                label="Selecciona PDFs",
                file_count="multiple",
                file_types=[".pdf"],
            )
            upload_button = gr.Button("Subir archivos", variant="primary")
            upload_status = gr.Textbox(
                label="Estado de subida",
                value="Esperando archivos para iniciar.",
                interactive=False,
                lines=3,
            )

            gr.Markdown("## 2. Carga archivos")
            index_button = gr.Button("Cargar archivos", variant="secondary")
            index_status = gr.Textbox(
                label="Estado de carga",
                value="Los archivos aun no han sido cargados al chat.",
                interactive=False,
                lines=3,
            )

            gr.Markdown("## Tus archivos")
            file_list = gr.Textbox(
                label="Archivos disponibles",
                value=_format_file_names([]),
                interactive=False,
                lines=14,
            )

        with gr.Column(scale=3, min_width=720):
            gr.Markdown("## 3. Consulta")
            chatbot = gr.Chatbot(
                label="Asistente financiero",
                value=[],
                height=640,
                layout="bubble",
                placeholder="Las respuestas apareceran aqui cuando el chat este habilitado.",
            )
            question_box = gr.Textbox(
                label="Pregunta",
                value="",
                lines=1,
                max_lines=6,
                interactive=False,
                placeholder=_chat_input_hint(indexed=False, uploaded=False),
            )
            with gr.Row():
                send_button = gr.Button("Enviar", variant="primary", interactive=False)
                clear_button = gr.Button("Limpiar chat", variant="secondary")

    upload_button.click(
        upload_files,
        inputs=[file_input],
        outputs=[
            upload_status,
            index_status,
            uploaded_files,
            file_list,
            indexed,
            question_box,
            send_button,
            chatbot,
            chat_history,
            session_summary,
        ],
    )

    index_button.click(
        index_files,
        inputs=[uploaded_files],
        outputs=[
            index_status,
            indexed,
            question_box,
            send_button,
            chatbot,
            chat_history,
            session_summary,
        ],
    )

    send_button.click(
        ask_question,
        inputs=[question_box, chat_history, indexed],
        outputs=[chatbot, question_box, chat_history],
    )

    question_box.submit(
        ask_question,
        inputs=[question_box, chat_history, indexed],
        outputs=[chatbot, question_box, chat_history],
    )

    clear_button.click(
        clear_chat,
        inputs=[indexed, uploaded_files],
        outputs=[chatbot, chat_history, question_box],
    )


if __name__ == "__main__":
    demo.launch(theme=theme)
