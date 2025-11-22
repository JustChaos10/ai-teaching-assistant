import dotenv from "dotenv";
import { fileURLToPath } from "url";
import path from "path";
// Load env here so it's available even if index hasn't configured yet
const __filename_storage = fileURLToPath(import.meta.url);
const __dirname_storage = path.dirname(__filename_storage);
dotenv.config();
dotenv.config({ path: path.join(__dirname_storage, ".env") });
dotenv.config({ path: path.join(__dirname_storage, "..", ".env") });
import {
  type Lecture,
  type InsertLecture,
  type Quiz,
  type InsertQuiz,
  type Question,
  type InsertQuestion,
  type Submission,
  type InsertSubmission,
} from "@shared/schema";
import { randomUUID } from "crypto";
import mongoose, { Schema, model, type Model } from "mongoose";

export interface IStorage {
  getLectures(): Promise<Lecture[]>;
  getLecture(id: string): Promise<Lecture | undefined>;
  createLecture(lecture: InsertLecture): Promise<Lecture>;
  updateLecture(id: string, lecture: Partial<InsertLecture>): Promise<Lecture | undefined>;
  updateLectureSummary(id: string, summary: string): Promise<void>;
  deleteLecture(id: string): Promise<boolean>;

  getQuizzes(): Promise<Quiz[]>;
  getQuiz(id: string): Promise<Quiz | undefined>;
  createQuiz(quiz: InsertQuiz): Promise<Quiz>;
  updateQuiz(id: string, quiz: Partial<InsertQuiz>): Promise<Quiz | undefined>;
  deleteQuiz(id: string): Promise<boolean>;

  getQuestions(quizId: string): Promise<Question[]>;
  createQuestions(questions: InsertQuestion[]): Promise<Question[]>;
  deleteQuestions(quizId: string): Promise<void>;

  getSubmission(id: string): Promise<Submission | undefined>;
  createSubmission(submission: InsertSubmission): Promise<Submission>;
}

export class MemStorage implements IStorage {
  private lectures: Map<string, Lecture>;
  private quizzes: Map<string, Quiz>;
  private questions: Map<string, Question>;
  private submissions: Map<string, Submission>;

  constructor() {
    this.lectures = new Map();
    this.quizzes = new Map();
    this.questions = new Map();
    this.submissions = new Map();
  }

  async getLectures(): Promise<Lecture[]> {
    return Array.from(this.lectures.values()).sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  async getLecture(id: string): Promise<Lecture | undefined> {
    return this.lectures.get(id);
  }

  async createLecture(insertLecture: InsertLecture): Promise<Lecture> {
    const id = randomUUID();
    const lecture: Lecture = {
      ...insertLecture,
      id,
      summary: null,
      createdAt: new Date(),
    };
    this.lectures.set(id, lecture);
    return lecture;
  }

  async updateLecture(id: string, updates: Partial<InsertLecture>): Promise<Lecture | undefined> {
    const lecture = this.lectures.get(id);
    if (!lecture) {
      return undefined;
    }
    const updated = { ...lecture, ...updates };
    this.lectures.set(id, updated);
    return updated;
  }

  async updateLectureSummary(id: string, summary: string): Promise<void> {
    const lecture = this.lectures.get(id);
    if (lecture) {
      lecture.summary = summary;
      this.lectures.set(id, lecture);
    }
  }

  async deleteLecture(id: string): Promise<boolean> {
    return this.lectures.delete(id);
  }

  async getQuizzes(): Promise<Quiz[]> {
    return Array.from(this.quizzes.values()).sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  async getQuiz(id: string): Promise<Quiz | undefined> {
    return this.quizzes.get(id);
  }

  async createQuiz(insertQuiz: InsertQuiz): Promise<Quiz> {
    const id = randomUUID();
    const quiz: Quiz = {
      ...insertQuiz,
      id,
      createdAt: new Date(),
    };
    this.quizzes.set(id, quiz);
    return quiz;
  }

  async updateQuiz(id: string, updates: Partial<InsertQuiz>): Promise<Quiz | undefined> {
    const quiz = this.quizzes.get(id);
    if (!quiz) {
      return undefined;
    }
    const updated = { ...quiz, ...updates };
    this.quizzes.set(id, updated);
    return updated;
  }

  async deleteQuiz(id: string): Promise<boolean> {
    const deleted = this.quizzes.delete(id);
    if (deleted) {
      await this.deleteQuestions(id);
    }
    return deleted;
  }

  async getQuestions(quizId: string): Promise<Question[]> {
    return Array.from(this.questions.values())
      .filter((q) => q.quizId === quizId)
      .sort((a, b) => a.order - b.order);
  }

  async createQuestions(insertQuestions: InsertQuestion[]): Promise<Question[]> {
    const questions: Question[] = [];
    for (const insertQuestion of insertQuestions) {
      const id = randomUUID();
      const question: Question = {
        ...insertQuestion,
        id,
      };
      this.questions.set(id, question);
      questions.push(question);
    }
    return questions;
  }

  async deleteQuestions(quizId: string): Promise<void> {
    const questionsToDelete = Array.from(this.questions.values())
      .filter((q) => q.quizId === quizId);
    
    for (const question of questionsToDelete) {
      this.questions.delete(question.id);
    }
  }

  async getSubmission(id: string): Promise<Submission | undefined> {
    return this.submissions.get(id);
  }

  async createSubmission(insertSubmission: InsertSubmission): Promise<Submission> {
    const id = randomUUID();
    const submission: Submission = {
      ...insertSubmission,
      id,
      submittedAt: new Date(),
    };
    this.submissions.set(id, submission);
    return submission;
  }
}

class MongoStorage implements IStorage {
  private LectureModel: Model<any>;
  private QuizModel: Model<any>;
  private QuestionModel: Model<any>;
  private SubmissionModel: Model<any>;

  constructor(uri: string) {
    mongoose.set("strictQuery", true);
    if (mongoose.connection.readyState === 0) {
      console.log("[mongo] connecting...");
      mongoose
        .connect(uri)
        .then(() => {
          // connection events below will also fire
        })
        .catch((err) => {
          console.error("[mongo] connection error:", err);
        });
    }

    mongoose.connection.on("connected", () => {
      const dbName = (mongoose.connection as any).name || mongoose.connection.db?.databaseName || "unknown";
      console.log(`[mongo] connected (db: ${dbName})`);
      if (typeof resolveMongoReady === "function") {
        resolveMongoReady();
        resolveMongoReady = null;
      }
    });
    mongoose.connection.on("error", (err) => {
      console.error("[mongo] connection error:", err);
      if (typeof resolveMongoReady === "function") {
        resolveMongoReady();
        resolveMongoReady = null;
      }
    });
    mongoose.connection.on("disconnected", () => {
      console.warn("[mongo] disconnected");
      if (typeof resolveMongoReady === "function") {
        resolveMongoReady();
        resolveMongoReady = null;
      }
    });

    const LectureSchema = new Schema(
      {
        id: { type: String, required: true, index: true, unique: true },
        title: { type: String, required: true },
        subject: { type: String, required: true },
        content: { type: String, required: true },
        summary: { type: String, default: null },
        createdAt: { type: Date, default: () => new Date() },
      },
      { versionKey: false }
    );

    const QuizSchema = new Schema(
      {
        id: { type: String, required: true, index: true, unique: true },
        lectureId: { type: String, required: true, index: true },
        title: { type: String, required: true },
        createdAt: { type: Date, default: () => new Date() },
      },
      { versionKey: false }
    );

    const QuestionSchema = new Schema(
      {
        id: { type: String, required: true, index: true, unique: true },
        quizId: { type: String, required: true, index: true },
        questionText: { type: String, required: true },
        options: { type: [String], required: true },
        correctAnswer: { type: Number, required: true },
        order: { type: Number, required: true },
      },
      { versionKey: false }
    );

    const SubmissionSchema = new Schema(
      {
        id: { type: String, required: true, index: true, unique: true },
        quizId: { type: String, required: true, index: true },
        studentName: { type: String, required: true },
        answers: { type: [Number], required: true },
        score: { type: Number, required: true },
        totalQuestions: { type: Number, required: true },
        submittedAt: { type: Date, default: () => new Date() },
      },
      { versionKey: false }
    );

    this.LectureModel = model("Lecture", LectureSchema);
    this.QuizModel = model("Quiz", QuizSchema);
    this.QuestionModel = model("Question", QuestionSchema);
    this.SubmissionModel = model("Submission", SubmissionSchema);
  }

  async getLectures(): Promise<Lecture[]> {
    const docs = await this.LectureModel.find().sort({ createdAt: -1 }).lean();
    return docs as unknown as Lecture[];
  }

  async getLecture(id: string): Promise<Lecture | undefined> {
    const doc = await this.LectureModel.findOne({ id }).lean();
    return (doc as unknown as Lecture) || undefined;
  }

  async createLecture(insertLecture: InsertLecture): Promise<Lecture> {
    const id = randomUUID();
    const doc = await this.LectureModel.create({ ...insertLecture, id, summary: null, createdAt: new Date() });
    return doc.toObject() as Lecture;
  }

  async updateLecture(id: string, updates: Partial<InsertLecture>): Promise<Lecture | undefined> {
    const doc = await this.LectureModel.findOneAndUpdate({ id }, { $set: updates }, { new: true }).lean();
    return (doc as unknown as Lecture) || undefined;
  }

  async updateLectureSummary(id: string, summary: string): Promise<void> {
    await this.LectureModel.updateOne({ id }, { $set: { summary } });
  }

  async deleteLecture(id: string): Promise<boolean> {
    const res = await this.LectureModel.deleteOne({ id });
    await this.QuizModel.deleteMany({ lectureId: id });
    const quizzes = await this.QuizModel.find({ lectureId: id }, { id: 1 }).lean();
    const quizIds = quizzes.map((q: any) => q.id);
    if (quizIds.length) {
      await this.QuestionModel.deleteMany({ quizId: { $in: quizIds } });
    }
    return res.deletedCount > 0;
  }

  async getQuizzes(): Promise<Quiz[]> {
    const docs = await this.QuizModel.find().sort({ createdAt: -1 }).lean();
    return docs as unknown as Quiz[];
  }

  async getQuiz(id: string): Promise<Quiz | undefined> {
    const doc = await this.QuizModel.findOne({ id }).lean();
    return (doc as unknown as Quiz) || undefined;
    }

  async createQuiz(insertQuiz: InsertQuiz): Promise<Quiz> {
    const id = randomUUID();
    const doc = await this.QuizModel.create({ ...insertQuiz, id, createdAt: new Date() });
    return doc.toObject() as Quiz;
  }

  async updateQuiz(id: string, updates: Partial<InsertQuiz>): Promise<Quiz | undefined> {
    const doc = await this.QuizModel.findOneAndUpdate({ id }, { $set: updates }, { new: true }).lean();
    return (doc as unknown as Quiz) || undefined;
  }

  async deleteQuiz(id: string): Promise<boolean> {
    const res = await this.QuizModel.deleteOne({ id });
    await this.QuestionModel.deleteMany({ quizId: id });
    return res.deletedCount > 0;
  }

  async getQuestions(quizId: string): Promise<Question[]> {
    const docs = await this.QuestionModel.find({ quizId }).sort({ order: 1 }).lean();
    return docs as unknown as Question[];
  }

  async createQuestions(insertQuestions: InsertQuestion[]): Promise<Question[]> {
    const docs = await this.QuestionModel.insertMany(
      insertQuestions.map((q) => ({ ...q, id: randomUUID() }))
    );
    return docs.map((d) => d.toObject()) as unknown as Question[];
  }

  async deleteQuestions(quizId: string): Promise<void> {
    await this.QuestionModel.deleteMany({ quizId });
  }

  async getSubmission(id: string): Promise<Submission | undefined> {
    const doc = await this.SubmissionModel.findOne({ id }).lean();
    return (doc as unknown as Submission) || undefined;
  }

  async createSubmission(insertSubmission: InsertSubmission): Promise<Submission> {
    const id = randomUUID();
    const doc = await this.SubmissionModel.create({ ...insertSubmission, id, submittedAt: new Date() });
    return doc.toObject() as unknown as Submission;
  }
}

export const storage: IStorage = process.env.MONGODB_URI
  ? new MongoStorage(process.env.MONGODB_URI)
  : new MemStorage();

// Determine backend from actual instance to avoid env mismatches
export const usingMongo = storage instanceof MongoStorage;
console.log(`[storage] backend: ${usingMongo ? "MongoDB (Mongoose)" : "In-Memory"}`);

type ResolveVoid = (value?: void | PromiseLike<void>) => void;
let resolveMongoReady: ResolveVoid | null = null;
export const mongoReady: Promise<void> = new Promise((resolve: ResolveVoid) => {
  resolveMongoReady = resolve;
});

// Helper to resolve only once
const resolveOnce = () => {
  if (typeof resolveMongoReady === "function") {
    resolveMongoReady();
    resolveMongoReady = null;
  }
};

if (!usingMongo) {
  // In-memory: resolve immediately
  resolveOnce();
}

// Fallback: avoid waiting forever if neither connected nor error events fire
setTimeout(() => {
  if (typeof resolveMongoReady === "function") {
    console.warn("[mongo] connection not confirmed within timeout; continuing startup");
    resolveOnce();
  }
}, 7000);
