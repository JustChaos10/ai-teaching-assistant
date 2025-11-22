import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { summarizeForGrade1, generateQuizQuestions } from "./huggingface";
import {
  insertLectureSchema,
  insertQuizSchema,
  insertQuestionSchema,
  insertSubmissionSchema,
} from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  app.get("/api/lectures", async (_req, res) => {
    try {
      const lectures = await storage.getLectures();
      res.json(lectures);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/lectures/:id", async (req, res) => {
    try {
      const lecture = await storage.getLecture(req.params.id);
      if (!lecture) {
        return res.status(404).json({ error: "Lecture not found" });
      }
      res.json(lecture);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/lectures", async (req, res) => {
    try {
      const validated = insertLectureSchema.parse(req.body);
      const lecture = await storage.createLecture(validated);

      try {
        console.log(`[AI] Summarization start (POST) lectureId=${lecture.id}`);
        const summary = await summarizeForGrade1(validated.content);
        await storage.updateLectureSummary(lecture.id, summary);
        const updated = await storage.getLecture(lecture.id);
        console.log(`[AI] Summarization end (POST) lectureId=${lecture.id}, hasSummary=${!!(updated?.summary)}`);
        res.json(updated ?? lecture);
      } catch (err) {
        console.error("Error generating summary:", err);
        const updated = await storage.getLecture(lecture.id);
        console.log(`[AI] Summarization failed (POST) lectureId=${lecture.id}, returning lecture with summary=${!!(updated?.summary)}`);
        res.json(updated ?? lecture);
      }
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: error.message });
    }
  });

  app.patch("/api/lectures/:id", async (req, res) => {
    try {
      if (Object.keys(req.body).length === 0) {
        return res.status(400).json({ error: "No updates provided" });
      }
      
      const validated = insertLectureSchema.partial().parse(req.body);
      const lecture = await storage.updateLecture(req.params.id, validated);
      
      if (!lecture) {
        return res.status(404).json({ error: "Lecture not found" });
      }

      if (validated.content) {
        try {
          const summary = await summarizeForGrade1(validated.content);
          await storage.updateLectureSummary(lecture.id, summary);
          const updated = await storage.getLecture(lecture.id);
          return res.json(updated ?? lecture);
        } catch (error) {
          console.error("Error generating summary:", error);
        }
      }

      res.json(lecture);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: error.message });
    }
  });

  app.delete("/api/lectures/:id", async (req, res) => {
    try {
      const deleted = await storage.deleteLecture(req.params.id);
      if (!deleted) {
        return res.status(404).json({ error: "Lecture not found" });
      }
      res.json({ success: true });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/quizzes", async (_req, res) => {
    try {
      const quizzes = await storage.getQuizzes();
      res.json(quizzes);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/quizzes/:id", async (req, res) => {
    try {
      const quiz = await storage.getQuiz(req.params.id);
      if (!quiz) {
        return res.status(404).json({ error: "Quiz not found" });
      }
      res.json(quiz);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/quizzes/:id/questions", async (req, res) => {
    try {
      const questions = await storage.getQuestions(req.params.id);
      res.json(questions);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  // AI: generate quiz questions based on a lecture's content
  app.post("/api/quizzes/generate", async (req, res) => {
    try {
      const { lectureId, count } = req.body as { lectureId?: string; count?: number };
      if (!lectureId) {
        return res.status(400).json({ error: "Missing required field: lectureId" });
      }
      const lecture = await storage.getLecture(lectureId);
      if (!lecture) {
        return res.status(404).json({ error: "Lecture not found" });
      }
      const num = typeof count === "number" && count > 0 ? Math.min(count, 10) : 5;
      const generated = await generateQuizQuestions(lecture.content, num);
      res.json(generated);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/quizzes", async (req, res) => {
    try {
      const { quizTitle, lectureId, questions } = req.body;

      if (!quizTitle || !lectureId || !Array.isArray(questions)) {
        return res.status(400).json({
          error: "Missing required fields: quizTitle, lectureId, questions",
        });
      }

      const lecture = await storage.getLecture(lectureId);
      if (!lecture) {
        return res.status(404).json({ error: "Lecture not found" });
      }

      const quizData = insertQuizSchema.parse({
        title: quizTitle,
        lectureId,
      });
      const quiz = await storage.createQuiz(quizData);

      const questionsWithQuizId = questions.map((q: any, index: number) => ({
        ...q,
        quizId: quiz.id,
        order: index,
      }));

      for (const q of questionsWithQuizId) {
        insertQuestionSchema.parse(q);
      }

      await storage.createQuestions(questionsWithQuizId);

      res.json(quiz);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: error.message });
    }
  });

  app.patch("/api/quizzes/:id", async (req, res) => {
    try {
      if (Object.keys(req.body).length === 0) {
        return res.status(400).json({ error: "No updates provided" });
      }
      
      const validated = insertQuizSchema.partial().parse(req.body);
      const quiz = await storage.updateQuiz(req.params.id, validated);
      
      if (!quiz) {
        return res.status(404).json({ error: "Quiz not found" });
      }

      res.json(quiz);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: error.message });
    }
  });

  app.delete("/api/quizzes/:id", async (req, res) => {
    try {
      const deleted = await storage.deleteQuiz(req.params.id);
      if (!deleted) {
        return res.status(404).json({ error: "Quiz not found" });
      }
      res.json({ success: true });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/submissions", async (req, res) => {
    try {
      const { quizId, studentName, answers } = req.body;

      if (!quizId || !studentName || !Array.isArray(answers)) {
        return res.status(400).json({
          error: "Missing required fields: quizId, studentName, answers",
        });
      }

      const quiz = await storage.getQuiz(quizId);
      if (!quiz) {
        return res.status(404).json({ error: "Quiz not found" });
      }

      const questions = await storage.getQuestions(quizId);
      if (questions.length === 0) {
        return res.status(404).json({ error: "No questions found for this quiz" });
      }

      let score = 0;
      questions.forEach((question, index) => {
        if (answers[index] === question.correctAnswer) {
          score++;
        }
      });

      const submissionData = insertSubmissionSchema.parse({
        quizId,
        studentName,
        answers,
        score,
        totalQuestions: questions.length,
      });

      const submission = await storage.createSubmission(submissionData);

      res.json({ submissionId: submission.id });
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/submissions/:id", async (req, res) => {
    try {
      const submission = await storage.getSubmission(req.params.id);
      if (!submission) {
        return res.status(404).json({ error: "Submission not found" });
      }

      const questions = await storage.getQuestions(submission.quizId);

      res.json({
        ...submission,
        questions,
      });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
