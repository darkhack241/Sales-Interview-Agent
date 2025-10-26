import reflex as rx
from app.state import InterviewState, Evaluation


def question_result_card(
    question: dict, answer: str, evaluation: Evaluation
) -> rx.Component:
    score_data = evaluation["scores"]
    return rx.el.div(
        rx.el.h3(
            f"Q{question['id']}: {question['text']}",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    "Your Answer", class_name="text-md font-semibold text-gray-600 mb-2"
                ),
                rx.el.p(answer, class_name="text-gray-700 italic"),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.h4(
                    "AI Feedback", class_name="text-md font-semibold text-gray-600 mb-2"
                ),
                rx.el.p(evaluation["feedback"], class_name="text-gray-700"),
            ),
            class_name="p-4 bg-gray-50 rounded-lg border border-gray-200",
        ),
        rx.el.div(
            rx.recharts.radar_chart(
                rx.recharts.polar_grid(),
                rx.recharts.polar_angle_axis(
                    data_key="subject", tick={"fill": "#4b5563"}
                ),
                rx.recharts.radar(
                    name="Score",
                    data_key="score",
                    stroke="#f97316",
                    fill="#f97316",
                    fill_opacity=0.6,
                ),
                data=[
                    {"subject": "Relevance", "score": score_data["relevance"]},
                    {"subject": "Impact", "score": score_data["impact"]},
                    {"subject": "Strategy", "score": score_data["strategy"]},
                    {"subject": "Clarity", "score": score_data["clarity"]},
                    {"subject": "Communication", "score": score_data["communication"]},
                ],
                cx="50%",
                cy="50%",
                outer_radius="80%",
                width=300,
                height=250,
            ),
            class_name="flex justify-center mt-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 w-full",
    )


def results_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            InterviewState.interview_finished,
            rx.el.div(
                rx.el.header(
                    rx.el.h1(
                        "Interview Report",
                        class_name="text-4xl font-bold text-gray-800",
                    ),
                    rx.el.p(
                        "Here is a detailed breakdown of your performance.",
                        class_name="text-lg text-gray-600 mt-2",
                    ),
                    rx.el.button(
                        "Download Report",
                        rx.icon("download", class_name="mr-2"),
                        on_click=rx.download(
                            data=InterviewState.get_report_data,
                            filename="interview_report.json",
                        ),
                        class_name="mt-4 px-4 py-2 bg-orange-500 text-white font-semibold rounded-lg shadow-sm hover:bg-orange-600 flex items-center",
                    ),
                    class_name="text-center py-12 bg-gray-50 border-b border-gray-200",
                ),
                rx.el.main(
                    rx.el.div(
                        rx.el.h2(
                            "Overall Performance",
                            class_name="text-2xl font-bold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                InterviewState.overall_summary.get("summary", ""),
                                class_name="text-gray-700 max-w-3xl",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Overall Score", class_name="text-lg font-semibold"
                                ),
                                rx.el.p(
                                    InterviewState.overall_summary.get(
                                        "total_average", 0.0
                                    ).to_string(),
                                    class_name="text-4xl font-bold text-orange-500",
                                ),
                                class_name="text-center",
                            ),
                            class_name="grid md:grid-cols-[2fr_1fr] gap-8 items-center bg-white p-8 rounded-xl border border-gray-200",
                        ),
                        class_name="mb-12",
                    ),
                    rx.el.div(
                        rx.el.h2(
                            "Per-Question Analysis",
                            class_name="text-2xl font-bold text-gray-800 mb-6",
                        ),
                        rx.foreach(
                            InterviewState.questions,
                            lambda q: rx.cond(
                                InterviewState.evaluations.contains(q["id"]),
                                question_result_card(
                                    q,
                                    InterviewState.answers[q["id"]],
                                    InterviewState.evaluations[q["id"]],
                                ),
                                rx.el.div(),
                            ),
                        ),
                        class_name="space-y-8",
                    ),
                    class_name="max-w-4xl mx-auto p-8",
                ),
            ),
            rx.el.div(
                rx.spinner(size="3"),
                rx.el.p("Generating your report...", class_name="text-gray-500 mt-4"),
                class_name="flex flex-col items-center justify-center h-screen",
            ),
        ),
        class_name="font-['Inter'] bg-white min-h-screen",
    )