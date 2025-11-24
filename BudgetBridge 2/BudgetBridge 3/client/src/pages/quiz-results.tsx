import { useQuery } from "@tanstack/react-query";
import { useRoute, Link } from "wouter";
import { Star, Home, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import type { Question } from "@shared/schema";

interface SubmissionWithDetails {
  id: string;
  quizId: string;
  studentName: string;
  answers: number[];
  score: number;
  totalQuestions: number;
  submittedAt: string;
  questions: Question[];
}

export default function QuizResults() {
  const [, params] = useRoute("/results/:id");
  const submissionId = params?.id;

  const { data: submission, isLoading } = useQuery<SubmissionWithDetails>({
    queryKey: ["/api/submissions", submissionId],
    enabled: !!submissionId,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-16 h-16 mx-auto animate-spin text-primary" />
          <p className="text-xl text-muted-foreground">Loading results...</p>
        </div>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardContent className="py-12 text-center space-y-4">
            <h2 className="text-2xl font-bold text-foreground">
              Results not found
            </h2>
            <Link href="/">
              <Button data-testid="button-back-home">Back to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const percentage = Math.round((submission.score / submission.totalQuestions) * 100);
  const passed = percentage >= 60;

  return (
    <div className="min-h-screen bg-background">
      <header
        className={`py-12 ${
          passed
            ? "bg-gradient-to-r from-chart-2 to-chart-1"
            : "bg-gradient-to-r from-chart-4 to-destructive"
        } text-white`}
      >
        <div className="max-w-3xl mx-auto px-6 text-center space-y-6">
          <div className="flex justify-center gap-2">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-12 h-12 ${
                  i < Math.ceil((percentage / 100) * 5)
                    ? "fill-chart-4 text-chart-4"
                    : "text-white/30"
                }`}
              />
            ))}
          </div>
          <h1 className="text-5xl font-bold">
            {passed ? "Great Job!" : "Keep Trying!"}
          </h1>
          <div className="space-y-2">
            <p className="text-9xl font-bold">{percentage}%</p>
            <p className="text-2xl">
              {submission.score} out of {submission.totalQuestions} correct
            </p>
          </div>
          <p className="text-2xl font-semibold">{submission.studentName}</p>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12">
        <div className="space-y-6">
          <h2 className="text-3xl font-bold text-foreground">Review Answers</h2>

          <Accordion type="single" collapsible className="space-y-4">
            {submission.questions.map((question, index) => {
              const userAnswer = submission.answers[index];
              const isCorrect = userAnswer === question.correctAnswer;

              return (
                <AccordionItem
                  key={question.id}
                  value={question.id}
                  data-testid={`review-question-${index}`}
                >
                  <Card
                    className={`border-2 ${
                      isCorrect
                        ? "border-chart-2/30 bg-chart-2/5"
                        : "border-destructive/30 bg-destructive/5"
                    }`}
                  >
                    <AccordionTrigger className="px-6 py-4 hover:no-underline">
                      <div className="flex items-start gap-4 text-left flex-1">
                        {isCorrect ? (
                          <CheckCircle className="w-6 h-6 text-chart-2 flex-shrink-0 mt-1" />
                        ) : (
                          <XCircle className="w-6 h-6 text-destructive flex-shrink-0 mt-1" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm text-muted-foreground mb-1">
                            Question {index + 1}
                          </p>
                          <p className="text-xl font-semibold text-foreground">
                            {question.questionText}
                          </p>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-6 pb-6">
                      <div className="space-y-3 mt-4">
                        {question.options.map((option, optIndex) => {
                          const isUserAnswer = userAnswer === optIndex;
                          const isCorrectAnswer = question.correctAnswer === optIndex;

                          return (
                            <div
                              key={optIndex}
                              className={`p-4 rounded-lg border-2 ${
                                isCorrectAnswer
                                  ? "border-chart-2 bg-chart-2/10"
                                  : isUserAnswer
                                  ? "border-destructive bg-destructive/10"
                                  : "border-border"
                              }`}
                              data-testid={`review-option-${index}-${optIndex}`}
                            >
                              <div className="flex items-center gap-3">
                                {isCorrectAnswer && (
                                  <CheckCircle className="w-5 h-5 text-chart-2" />
                                )}
                                {isUserAnswer && !isCorrectAnswer && (
                                  <XCircle className="w-5 h-5 text-destructive" />
                                )}
                                <p className="text-lg flex-1">{option}</p>
                                {isCorrectAnswer && (
                                  <span className="text-sm font-semibold text-chart-2">
                                    Correct Answer
                                  </span>
                                )}
                                {isUserAnswer && !isCorrectAnswer && (
                                  <span className="text-sm font-semibold text-destructive">
                                    Your Answer
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </AccordionContent>
                  </Card>
                </AccordionItem>
              );
            })}
          </Accordion>

          <div className="pt-8 text-center">
            <Link href="/">
              <Button size="lg" className="text-xl px-8" data-testid="button-back-home">
                <Home className="w-5 h-5 mr-2" />
                Back to Lessons
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
