const GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";

export async function summarizeForGrade1(text: string): Promise<string> {
  try {
    const model = process.env.GROQ_MODEL || "llama-3.1-8b-instant";

    // Truncate input text if it's too long (GROQ has token limits)
    // Most models can handle ~6000-8000 tokens input, roughly 24000-32000 chars
    const maxInputChars = 20000;
    const truncatedText = text.length > maxInputChars ? text.slice(0, maxInputChars) + "\n\n[Content truncated for processing]" : text;

    const prompt = [
      "Summarize the following lesson for Grade 1 students.",
      "Requirements (must follow strictly):",
      "- Use past tense (e.g., learned, saw, read).",
      "- Use simple words and correct grammar and spelling.",
      "- Create a comprehensive summary covering all key points and sections.",
      "- Organize the summary in clear paragraphs.",
      "- Output plain text only (no bullet points, no headings, no quotes).",
      "- Do not invent details. Do not repeat sentences.",
      "- Ensure words are complete (no missing letters or truncations).",
      "- Make the summary detailed enough to cover the entire lesson content.",
      "",
      "Text to summarize:",
      "",
      truncatedText,
    ].join("\n");

    // Logging: AI_Prompt and Content (always log)
    const trunc = (s: string, n = 1000) => (s.length > n ? s.slice(0, n) + "... [truncated]" : s);
    console.log("AI_Prompt:\n" + trunc(prompt));
    console.log("Content:\n" + trunc(text));

    const apiKey = process.env.GROQ_API_KEY;
    console.log(`[DEBUG] GROQ_API_KEY present: ${!!apiKey}, length: ${apiKey?.length || 0}`);

    if (!apiKey) {
      console.warn("GROQ_API_KEY not set. Returning first 2000 characters as summary.");
      const fallback = text.slice(0, 2000);
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
        max_tokens: 2000,
        messages: [
          {
            role: "system",
            content:
              `You are a careful editor that writes clear, child-friendly summaries. Always use past tense, very simple words, correct grammar and spelling. Create a comprehensive summary that covers all the key points from the lesson. Return plain text only.`,
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
      return text.slice(0, 2000);
    }

    const data: any = await response.json();
    const content: string | undefined = data?.choices?.[0]?.message?.content;
    if (!content) {
      console.error("Groq API returned no content:", JSON.stringify(data));
      console.log("Response:\n" + trunc(JSON.stringify(data)));
      return text.slice(0, 2000);
    }

    console.log("Response:\n" + trunc(content));
    return (content || "").trim();
  } catch (error) {
    console.error("Error calling Groq API:", error);
    console.log("Response:\n[Error invoking Groq API]");
    return text.slice(0, 2000);
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
  const model = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";
  const apiKey = process.env.GROQ_API_KEY;

  const instruction = [
    "Create fun, interactive multiple-choice questions for Grade 1 students based on the following lesson.",
    "Make the questions highly visual and engaging using emojis and symbols where appropriate.",
    "For example:\n",
    "- For counting: 'How many 🍎 are there? 🍎🍎🍎' with options like '1', '2', '3', '4'\n",
    "- For colors: 'What color is the 🟡? (sun emoji)' with options like '🟡 Yellow', '🔵 Blue', '🔴 Red', '🟢 Green'\n",
    "- For shapes: 'Which shape has 3 sides? 🔺 ⬜ ⚪' with shape options\n\n",
    "Requirements:\n",
    `- Generate exactly ${count} questions if possible, but at least 3.`,
    "- Each question must have 4 answer options (labeled 0 to 3) with one correct answer.",
    "- Use emojis and symbols to make questions visual and engaging for young children.",
    "- Keep text simple and minimal - use emojis to replace words where possible.",
    "- For math questions, include visual representations (e.g., '2 + 2 = ?' could show '🍎🍎 + 🍎🍎 = ?')",
    "- Format your response as a JSON array of objects with these keys:",
    "  - questionText: The question with emojis",
    "  - options: Array of 4 answer choices (include emojis here too if relevant)",
    "  - correctAnswer: Number (0-3) indicating the correct option",
    "\nReturn ONLY valid JSON (no prose, no code fences)."
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
      temperature: 0.5,
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
