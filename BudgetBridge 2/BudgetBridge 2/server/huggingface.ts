const GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";
import dotenv from "dotenv";
import path from "path";

// Load .env from the project root
dotenv.config({ path: path.resolve(__dirname, "../../../../.env") });

const apiKey = process.env.GROQ_API_KEY;

if (!apiKey) {
  throw new Error("GROQ_API_KEY environment variable is not set");
}


export async function summarizeForGrade1(text: string): Promise<string> {
  try {
    const model = process.env.GROQ_MODEL || "llama-3.1-8b-instant";
    const prompt = [
      "Summarize the following lesson for Grade 1 students.",
      "Requirements (must follow strictly):",
      "- Use past tense (e.g., learned, saw, read).",
      "- Use simple words and correct grammar and spelling.",
      "- Write 4 to 6 short sentences.",
      "- Output plain text only (no lists, no headings, no quotes).",
      "- Do not invent details. Do not repeat sentences.",
      "- Ensure words are complete (no missing letters or truncations).",
      "",
      "Text to summarize:",
      "",
      text,
    ].join("\n");

    // Logging: AI_Prompt and Content (always log)
    const trunc = (s: string, n = 1000) => (s.length > n ? s.slice(0, n) + "... [truncated]" : s);
    console.log("AI_Prompt:\n" + trunc(prompt));
    console.log("Content:\n" + trunc(text));

    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
      console.warn("GROQ_API_KEY not set. Falling back to manual simplifier.");
      const fallback = text.slice(0, 600);
      console.log("Response:\n" + trunc(fallback));
      return fallback;
    }

    const response = await fetch(GROQ_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        temperature: 0.2,
        max_tokens: 220,
        messages: [
          {
            role: "system",
            content:
              `You are a careful editor that writes clear, child-friendly summaries. Always use past tense, very simple words, correct grammar and spelling, and 4–6 short sentences. Return plain text only.
              Please give me in only 150 words.
              `,
          },
          {
            role: "user",
            content: prompt,
          },
        ],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Groq API error:", errorText);
      console.log("Response:\n" + trunc(errorText));
      return text.slice(0, 600);
    }

    const data: any = await response.json();
    const content: string | undefined = data?.choices?.[0]?.message?.content;
    if (!content) {
      console.error("Groq API returned no content:", JSON.stringify(data));
      console.log("Response:\n" + trunc(JSON.stringify(data)));
      return text.slice(0, 600);
    }

    console.log("Response:\n" + trunc(content));
    return (content || "").trim();
  } catch (error) {
    console.error("Error calling Groq API:", error);
    console.log("Response:\n[Error invoking Groq API]");
    return text.slice(0, 600);
  }
}

export interface GeneratedQuestion {
  questionText: string;
  options: [string, string, string, string];
  correctAnswer: number; // 0-3
}

export async function generateQuizQuestions(
  text: string,
  count: number = 5
): Promise<GeneratedQuestion[]> {
  const model = process.env.GROQ_MODEL || "llama-3.1-8b-instant";
  const apiKey = process.env.GROQ_API_KEY;

  const instruction = [
    "Create multiple-choice questions based on the following lesson.",
    "Here there can be Math based content or English based content.",
    "based on the content, generate questions that are suitable for Grade 1 students.",
    "You should generate exactly 5 questions.",
    "Each question must have 4 answer options (labeled 0 to 3) with one correct answer.",
    "Format your response as a JSON array of objects with the following keys:",
    "Constraints:",
    "- Return ONLY valid JSON (no prose, no code fences).",
    "- The JSON must be an array of objects with keys: questionText (string), options (array of 4 strings), correctAnswer (number 0-3).",
    `- Create exactly ${count} questions if possible; fewer if the text doesn't allow it, but at least 3.`,
    "- Keep questions simple for Grade 1 level; avoid tricky wording.",
    "- Ensure one and only one correct answer; other options should be plausible.",
  ].join("\n");

  const user = [
    "Lesson text:",
    text,
    "",
    "Respond with the JSON array only.",
  ].join("\n");

  // Log prompt for debugging
  const trunc = (s: string, n = 1000) => (s.length > n ? s.slice(0, n) + "... [truncated]" : s);
  console.log("AI_Prompt:\n" + trunc(instruction + "\n\n" + user));
  console.log("Content:\n" + trunc(text));

  if (!apiKey) {
    console.warn("GROQ_API_KEY not set. Returning empty questions.");
    return [];
  }

  const response = await fetch(GROQ_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      max_tokens: 800,
      messages: [
        { role: "system", content: instruction },
        { role: "user", content: user },
      ],
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Groq API error (quiz gen):", errorText);
    console.log("Response:\n" + trunc(errorText));
    return [];
  }

  const data: any = await response.json();
  let content: string = data?.choices?.[0]?.message?.content || "";
  console.log("Response:\n" + trunc(content));

  // Strip code fences if present
  content = content.trim();
  if (content.startsWith("```")) {
    content = content.replace(/^```[a-zA-Z]*\n?/, "").replace(/```\s*$/, "").trim();
  }

  try {
    const parsed = JSON.parse(content);
    if (!Array.isArray(parsed)) return [];
    const normalized: GeneratedQuestion[] = parsed
      .map((q: any) => {
        const options = [0, 1, 2, 3].map((i) => String(q?.options?.[i] ?? "").trim()) as [
          string,
          string,
          string,
          string
        ];
        const caRaw = Number.isInteger(q?.correctAnswer) ? q.correctAnswer : 0;
        const correctAnswer = caRaw >= 0 && caRaw <= 3 ? caRaw : 0;
        return {
          questionText: String(q.questionText || "").trim(),
          options,
          correctAnswer,
        } as GeneratedQuestion;
      })
      .filter((q: GeneratedQuestion) => q.questionText && q.options.every((o) => !!o))
      .slice(0, count);
    return normalized;
  } catch (e) {
    console.error("Failed to parse quiz generation JSON:", e);
    return [];
  }
}
