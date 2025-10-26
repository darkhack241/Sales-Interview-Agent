import reflex as rx
import google.generativeai as genai
from typing import TypedDict, Optional
import os
from elevenlabs.client import ElevenLabs
from elevenlabs.core import ApiError
import logging
import json


class Question(TypedDict):
    id: int
    text: str
    audio_file: Optional[str]


class EvaluationScores(TypedDict):
    relevance: int
    impact: int
    strategy: int
    clarity: int
    communication: int


class Evaluation(TypedDict):
    scores: EvaluationScores
    feedback: str
    overall: float


class InterviewState(rx.State):
    """Manages the state of the AI interview session."""

    questions: list[Question] = [
        {
            "id": 1,
            "text": "Tell me about your most successful sales campaign — what made it effective?",
            "audio_file": None,
        },
        {
            "id": 2,
            "text": "Describe a time you had to handle a difficult client. What was the situation and how did you manage it?",
            "audio_file": None,
        },
        {
            "id": 3,
            "text": "How do you identify and qualify potential leads? What tools or strategies do you use?",
            "audio_file": None,
        },
        {
            "id": 4,
            "text": "Walk me through your process for closing a complex, high-value deal from start to finish.",
            "audio_file": None,
        },
        {
            "id": 5,
            "text": "How do you stay updated on industry trends and competitor activities, and how do you use that information?",
            "audio_file": None,
        },
        {
            "id": 6,
            "text": "Describe a situation where you failed to meet a sales target. What did you learn from that experience?",
            "audio_file": None,
        },
        {
            "id": 7,
            "text": "Imagine you need to break into a new, untapped market. What would be your 90-day plan?",
            "audio_file": None,
        },
    ]
    answers: dict[int, str] = {}
    evaluations: dict[int, Evaluation] = {}
    overall_summary: dict = {}
    is_evaluating: bool = False
    current_question_index: int = -1
    interview_started: bool = False
    interview_finished: bool = False
    is_recording: bool = False
    transcript: str = ""
    is_ai_speaking: bool = False

    @rx.var
    def total_questions(self) -> int:
        return len(self.questions)

    @rx.var
    def progress_percent(self) -> float:
        if not self.interview_started or self.current_question_index < 0:
            return 0
        return (self.current_question_index + 1) / self.total_questions * 100

    @rx.var
    def current_question(self) -> Question | None:
        if (
            self.interview_started
            and 0 <= self.current_question_index < self.total_questions
        ):
            return self.questions[self.current_question_index]
        return None

    @rx.var
    def current_answer(self) -> str:
        if self.current_question:
            return self.answers.get(self.current_question["id"], "")
        return ""

    @rx.var
    def is_first_question(self) -> bool:
        return self.current_question_index == 0

    @rx.var
    def is_last_question(self) -> bool:
        return self.current_question_index == self.total_questions - 1

    @rx.event
    def start_interview(self):
        self.interview_started = True
        self.current_question_index = 0
        return InterviewState.generate_all_question_audio

    @rx.event
    async def generate_all_question_audio(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            logging.warning(
                "ELEVENLABS_API_KEY not set. Skipping audio generation. The interview will proceed without audio."
            )
            return
        client = ElevenLabs(api_key=api_key)
        for i, q in enumerate(self.questions):
            if q["audio_file"] is None:
                try:
                    audio_generator = client.text_to_speech.convert(
                        text=q["text"],
                        voice_id="JBFqnCBsd6RMkjVDRZzb",
                        model_id="eleven_multilingual_v2",
                        output_format="mp3_44100_128",
                    )
                    filename = f"question_{q['id']}.mp3"
                    upload_dir = rx.get_upload_dir()
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    outfile = upload_dir / filename
                    with outfile.open("wb") as file_object:
                        for chunk in audio_generator:
                            file_object.write(chunk)
                    self.questions[i]["audio_file"] = filename
                except ApiError as e:
                    if e.status_code == 401:
                        logging.warning(
                            f"ElevenLabs API key is missing text-to-speech permission for question {q['id']}. The interview will continue without audio for this question."
                        )
                    else:
                        logging.exception(
                            f"An ElevenLabs API error occurred for question {q['id']}: {e}"
                        )
                except Exception as e:
                    logging.exception(
                        f"An unexpected error occurred generating audio for question {q['id']}: {e}"
                    )

    @rx.event
    def next_question(self):
        if self.current_question_index < self.total_questions - 1:
            self.current_question_index += 1
            self.transcript = ""
            self.is_ai_speaking = True

    @rx.event
    def prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.transcript = self.current_answer

    @rx.event
    def set_answer(self, text: str):
        if self.current_question:
            question_id = self.current_question["id"]
            self.answers[question_id] = text

    @rx.event
    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if not self.is_recording and self.transcript:
            self.set_answer(self.transcript)
            return InterviewState.evaluate_answer

    @rx.event
    def set_transcript(self, transcript: str):
        self.transcript = transcript
        self.set_answer(transcript)

    @rx.event
    def set_ai_speaking(self, is_speaking: bool):
        self.is_ai_speaking = is_speaking

    @rx.event
    def setup_audio_listeners(self):
        return rx.call_script(
            f"setupAudioEventListeners('{InterviewState.set_ai_speaking.get_full_name()}', '{InterviewState.set_ai_speaking.get_full_name()}')"
        )

    @rx.event(background=True)
    async def evaluate_answer(self):
        async with self:
            if not self.current_question or not self.current_answer:
                return
            self.is_evaluating = True
            question_id = self.current_question["id"]
            question_text = self.current_question["text"]
            answer_text = self.current_answer
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                "gemini-2.5-flash",
                generation_config={"response_mime_type": "application/json"},
            )
            prompt = f"""You are an expert Sales & BD interview evaluator.\n\nQuestion: {question_text}\nCandidate's Answer: {answer_text}\n\nEvaluate the answer based on the following rubric, providing a score from 0 to 5 for each category:\n- Relevance: How relevant and on-topic was the answer?\n- Impact/Results: Did the candidate mention measurable outcomes or clear achievements?\n- Strategy/Approach: Did they describe a clear plan or thought process?\n- Clarity & Structure: Was the response well-organized and logical?\n- Communication & Confidence: How clear and confident was their delivery?\n\nReturn a JSON object with this exact structure:\n{{\n  "scores": {{ "relevance": <score>, "impact": <score>, "strategy": <score>, "clarity": <score>, "communication": <score> }},\n  "feedback": "<short, constructive feedback text>",\n  "overall": <average_score>\n}} \n"""
            response = await model.generate_content_async(prompt)
            evaluation_data = json.loads(response.text)
            async with self:
                self.evaluations[question_id] = evaluation_data
                self.is_evaluating = False
        except Exception as e:
            logging.exception(f"Error during evaluation: {e}")
            async with self:
                self.is_evaluating = False

    @rx.event(background=True)
    async def finalize_interview(self):
        async with self:
            self.is_evaluating = True
        all_answers = "".join(
            (
                f"Q{q['id']}: {q['text']}\nA: {self.answers.get(q['id'], 'No answer.')}\n\n"
                for q in self.questions
            )
        )
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                "gemini-2.5-flash",
                generation_config={"response_mime_type": "application/json"},
            )
            prompt = f"""You are an expert Sales & BD hiring manager. Based on the full interview transcript below, provide a final summary of the candidate's performance. \n\nTranscript:\n{all_answers}\n\nReturn a JSON object with this exact structure:\n{{\n  "summary": "<A brief 3-4 sentence summary of the candidate's overall strengths and areas for improvement.>",\n  "total_average": <A float representing the average of all question scores from the transcript analysis>\n}}\n"""
            response = await model.generate_content_async(prompt)
            summary_data = json.loads(response.text)
            async with self:
                self.overall_summary = summary_data
                self.is_evaluating = False
                self.interview_finished = True
        except Exception as e:
            logging.exception(f"Error during final summary: {e}")
            async with self:
                self.is_evaluating = False

    @rx.var
    def get_current_evaluation(self) -> Evaluation | None:
        if self.current_question:
            return self.evaluations.get(self.current_question["id"])
        return None

    @rx.var
    def get_report_data(self) -> str:
        report = {
            "questions": self.questions,
            "answers": self.answers,
            "evaluations": self.evaluations,
            "summary": self.overall_summary,
        }
        return json.dumps(report, indent=2)