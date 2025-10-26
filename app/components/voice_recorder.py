import reflex as rx
from app.state import InterviewState


def recorder_status() -> rx.Component:
    """Displays the recording status indicator."""
    return rx.el.div(
        rx.el.div(
            rx.cond(
                InterviewState.is_recording,
                rx.el.div(class_name="w-2 h-2 bg-red-500 rounded-full animate-pulse"),
                rx.el.div(class_name="w-2 h-2 bg-gray-400 rounded-full"),
            )
        ),
        rx.el.p(
            rx.cond(InterviewState.is_recording, "Recording", "Ready"),
            class_name="text-xs font-medium text-gray-500",
        ),
        class_name="flex items-center gap-2",
    )


def voice_recorder() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon(
                rx.cond(InterviewState.is_recording, "mic-off", "mic"),
                class_name="w-8 h-8",
            ),
            on_click=InterviewState.toggle_recording,
            class_name=rx.cond(
                InterviewState.is_recording,
                "p-5 rounded-full bg-red-100 text-red-600 hover:bg-red-200 transition-colors shadow-lg animate-pulse",
                "p-5 rounded-full bg-green-100 text-green-600 hover:bg-green-200 transition-colors shadow-md",
            ),
        ),
        recorder_status(),
        rx.el.script(src="/js/speech.js"),
        class_name="flex flex-col items-center gap-3",
    )


def ai_avatar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("bot", class_name="w-10 h-10 text-orange-500"),
            class_name="p-4 bg-orange-100 rounded-full border-4 border-white shadow-md",
        ),
        rx.el.p(
            "AI Interviewer", class_name="text-sm font-semibold text-gray-700 mt-2"
        ),
        rx.cond(
            InterviewState.is_ai_speaking,
            rx.el.div(
                rx.el.div(
                    class_name="w-2 h-2 bg-orange-500 rounded-full animate-pulse"
                ),
                rx.el.p("Speaking...", class_name="text-xs text-orange-600"),
                class_name="flex items-center gap-1.5 mt-1",
            ),
            rx.el.div(class_name="h-6 mt-1"),
        ),
        class_name="flex flex-col items-center justify-self-start",
    )


def candidate_avatar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("user", class_name="w-10 h-10 text-blue-500"),
            class_name="p-4 bg-blue-100 rounded-full border-4 border-white shadow-md",
        ),
        rx.el.p("You", class_name="text-sm font-semibold text-gray-700 mt-2"),
        rx.cond(
            InterviewState.is_recording,
            rx.el.div(
                rx.icon("mic", class_name="w-4 h-4 text-red-500 animate-pulse"),
                rx.el.p("Listening...", class_name="text-xs text-red-600"),
                class_name="flex items-center gap-1.5 mt-1",
            ),
            rx.el.div(class_name="h-6 mt-1"),
        ),
        class_name="flex flex-col items-center justify-self-end",
    )