import reflex as rx
from app.state import InterviewState
from app.components.voice_recorder import voice_recorder, ai_avatar, candidate_avatar


def icon_text_item(icon_name: str, text: str) -> rx.Component:
    """A helper to create an icon and text item."""
    return rx.el.div(
        rx.icon(icon_name, class_name="w-5 h-5 text-orange-500"),
        rx.el.span(text, class_name="text-gray-600"),
        class_name="flex items-center gap-3",
    )


def welcome_screen() -> rx.Component:
    """The initial screen before the interview starts."""
    return rx.el.div(
        rx.icon("clipboard-pen-line", class_name="w-16 h-16 text-orange-500 mb-6"),
        rx.el.h1(
            "Sales & BD Interview", class_name="text-4xl font-bold text-gray-800 mb-4"
        ),
        rx.el.p(
            "Welcome! This is a structured interview for the Sales & Business Development role.",
            class_name="text-lg text-gray-600 mb-8 max-w-2xl text-center",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Instructions",
                    class_name="text-xl font-semibold text-gray-700 mb-4",
                ),
                rx.el.div(
                    icon_text_item("mic", "You will answer questions with your voice."),
                    icon_text_item(
                        "message-square-text",
                        "Your responses will be transcribed in real-time.",
                    ),
                    icon_text_item("timer", "Take your time; there is no rush."),
                    icon_text_item("volume-2", "Questions will be read aloud to you."),
                    class_name="flex flex-col gap-4 mb-8",
                ),
                class_name="bg-white p-8 rounded-xl border border-gray-200",
            ),
            class_name="w-full max-w-lg mb-8",
        ),
        rx.el.button(
            "Start Interview",
            rx.icon("arrow-right", class_name="ml-2"),
            on_click=InterviewState.start_interview,
            class_name="px-8 py-4 bg-orange-500 text-white font-semibold rounded-lg shadow-md hover:bg-orange-600 transition-all duration-200 flex items-center",
        ),
        class_name="flex flex-col items-center justify-center text-center p-8 w-full",
    )


def interview_view() -> rx.Component:
    """The main view for the interview questions and answers."""
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.h2(
                    "Sales & BD Interview", class_name="text-xl font-bold text-gray-800"
                ),
                rx.el.p(
                    f"Question {InterviewState.current_question_index + 1} of {InterviewState.total_questions}",
                    class_name="text-sm font-medium text-gray-500",
                ),
                class_name="flex justify-between items-center w-full",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="bg-orange-500 h-2 rounded-full transition-all duration-500",
                    style={"width": f"{InterviewState.progress_percent}%"},
                ),
                class_name="w-full bg-gray-200 rounded-full h-2 mt-4",
            ),
            class_name="w-full max-w-5xl p-6",
        ),
        rx.el.main(
            rx.cond(
                InterviewState.current_question,
                rx.el.div(
                    rx.el.div(
                        ai_avatar(),
                        rx.el.div(
                            rx.cond(
                                InterviewState.current_question["audio_file"],
                                rx.el.audio(
                                    src=rx.get_upload_url(
                                        InterviewState.current_question["audio_file"]
                                    ),
                                    auto_play=True,
                                    id="question-audio",
                                    on_mount=InterviewState.setup_audio_listeners,
                                    class_name="hidden",
                                ),
                                rx.spinner(size="2"),
                            ),
                            class_name="flex flex-col items-center justify-center h-48",
                        ),
                        candidate_avatar(),
                        class_name="grid grid-cols-[1fr,auto,1fr] items-center gap-8 w-full",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.cond(
                                InterviewState.transcript != "",
                                rx.el.p(
                                    InterviewState.transcript,
                                    class_name="text-gray-800",
                                ),
                                rx.el.p(
                                    "Your live transcript will appear here...",
                                    class_name="text-gray-400 italic",
                                ),
                            ),
                            class_name="w-full max-w-2xl h-40 p-4 bg-white border border-gray-200 rounded-lg overflow-y-auto text-center",
                        ),
                        class_name="w-full flex flex-col items-center mt-8",
                    ),
                    class_name="w-full flex flex-col items-center justify-center flex-grow",
                ),
                rx.el.div(
                    rx.spinner(size="3"),
                    rx.el.p("Loading next question...", class_name="text-gray-500"),
                    class_name="flex flex-col items-center justify-center h-full gap-4",
                ),
            ),
            class_name="flex-grow w-full max-w-5xl p-6 flex flex-col items-center justify-center",
        ),
        rx.el.footer(
            rx.el.div(
                rx.el.button(
                    rx.icon("arrow-left", class_name="mr-2"),
                    "Previous",
                    on_click=InterviewState.prev_question,
                    disabled=InterviewState.is_first_question,
                    class_name="px-6 py-3 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg shadow-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center",
                ),
                rx.el.div(
                    voice_recorder(),
                    class_name="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2",
                ),
                rx.el.button(
                    rx.cond(
                        InterviewState.is_last_question,
                        "Finish & View Results",
                        "Next Question",
                    ),
                    rx.icon("arrow-right", class_name="ml-2"),
                    on_click=[
                        rx.cond(
                            InterviewState.is_last_question,
                            InterviewState.finalize_interview,
                            InterviewState.next_question,
                        ),
                        rx.cond(
                            InterviewState.is_last_question,
                            rx.redirect("/results"),
                            rx.noop(),
                        ),
                    ],
                    disabled=InterviewState.is_evaluating,
                    class_name="px-6 py-3 bg-orange-500 text-white font-semibold rounded-lg shadow-md hover:bg-orange-600 disabled:bg-orange-300 disabled:cursor-not-allowed transition-all duration-200 flex items-center",
                ),
                class_name="flex justify-between items-center w-full relative",
            ),
            class_name="w-full max-w-5xl p-6 border-t border-gray-200",
        ),
        class_name="flex flex-col items-center justify-between w-full h-full min-h-screen",
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.cond(InterviewState.interview_started, interview_view(), welcome_screen()),
        class_name="font-['Inter'] bg-gray-50 w-full min-h-screen flex items-center justify-center",
    )


from app.results import results_page

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.script(src="https://unpkg.com/recharts/umd/Recharts.min.js"),
    ],
)
app.add_page(index)
app.add_page(results_page, route="/results")