"use client";

import { useRef, useState } from "react";

type SpeechRecognitionResult = {
  0: {
    transcript: string;
  };
};

type SpeechRecognitionEventLike = Event & {
  results: {
    length: number;
    [index: number]: SpeechRecognitionResult;
  };
};

type SpeechRecognitionErrorEventLike = Event & {
  error: string;
};

interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;

  start(): void;
  stop(): void;

  onresult:
    | ((event: SpeechRecognitionEventLike) => void)
    | null;

  onerror:
    | ((event: SpeechRecognitionErrorEventLike) => void)
    | null;

  onend: (() => void) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionLike;
}

type SpeechRecognitionWindow = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

export default function VoiceButton({
  onTranscript,
}: {
  onTranscript: (text: string) => void;
}) {
  const recognitionRef =
    useRef<SpeechRecognitionLike | null>(null);

  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function startListening() {
    setError(null);

    if (listening) {
      return;
    }

    const speechWindow =
      window as SpeechRecognitionWindow;

    const SpeechRecognitionAPI =
      speechWindow.SpeechRecognition ??
      speechWindow.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setError(
        "Speech recognition is not supported by this browser."
      );
      return;
    }

    const recognition = new SpeechRecognitionAPI();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript =
        Array.from(
          { length: event.results.length },
          (_, index) =>
            event.results[index][0].transcript
        )
          .join(" ")
          .trim();

      if (transcript) {
        onTranscript(transcript);
      }
    };

    recognition.onerror = (event) => {
      setListening(false);

      setError(
        `Speech recognition error: ${event.error}`
      );
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
      setListening(true);
    } catch {
      setListening(false);
      recognitionRef.current = null;
      setError("Could not start microphone.");
    }
  }

  function stopListening() {
    recognitionRef.current?.stop();
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        onClick={
          listening
            ? stopListening
            : startListening
        }
        title={
          listening
            ? "Stop listening"
            : "Start voice input"
        }
        className={`flex h-12 w-12 items-center justify-center rounded-full border transition ${
          listening
            ? "border-red-400/40 bg-red-400/10 text-red-300"
            : "border-white/10 bg-white/[0.04] text-zinc-300 hover:bg-white/[0.08]"
        }`}
      >
        {listening ? "■" : "🎤"}
      </button>

      {listening && (
        <span className="text-xs text-zinc-500">
          Listening...
        </span>
      )}

      {error && (
        <span className="text-xs text-red-400">
          {error}
        </span>
      )}
    </div>
  );
}
