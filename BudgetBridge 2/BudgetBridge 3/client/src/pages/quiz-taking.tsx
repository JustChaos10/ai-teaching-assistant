import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRoute, useLocation } from "wouter";
import { ArrowLeft, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import type { Quiz, Question } from "@shared/schema";

export default function QuizTaking() {
  const [, params] = useRoute("/quiz/:id");
  const [, setLocation] = useLocation();
  const quizId = params?.id;
  const [studentName, setStudentName] = useState("");
  const [started, setStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const { toast } = useToast();

  const { data: quiz, isLoading: quizLoading } = useQuery<Quiz>({
    queryKey: ["/api/quizzes", quizId],
    enabled: !!quizId,
  });

  const { data: questions, isLoading: questionsLoading } = useQuery<Question[]>({
    queryKey: ["/api/quizzes", quizId, "questions"],
    enabled: !!quizId,
  });

  const submitMutation = useMutation({
    mutationFn: async (data: {
      quizId: string;
      studentName: string;
      answers: number[];
    }) => {
      const response = await apiRequest("POST", "/api/submissions", data);
      return await response.json();
    },
    onSuccess: (data: any) => {
      setLocation(`/results/${data.submissionId}`);
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleStart = () => {
    if (!studentName.trim()) {
      toast({
        title: "Please enter your name",
        description: "We need your name to save your quiz results",
        variant: "destructive",
      });
      return;
    }
    setStarted(true);
  };

  const handleAnswer = (answerIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (answers[currentQuestion] === undefined) {
      toast({
        title: "Please select an answer",
        description: "Choose one option before continuing",
        variant: "destructive",
      });
      return;
    }
    if (questions && currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handleSubmit = () => {
    if (answers[currentQuestion] === undefined) {
      toast({
        title: "Please select an answer",
        description: "Choose one option before submitting",
        variant: "destructive",
      });
      return;
    }

    if (quizId) {
      submitMutation.mutate({
        quizId,
        studentName,
        answers,
      });
    }
  };

  if (quizLoading || questionsLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-16 h-16 mx-auto animate-spin text-primary" />
          <p className="text-xl text-muted-foreground">Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (!quiz || !questions || questions.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardContent className="py-12 text-center space-y-4">
            <h2 className="text-2xl font-bold text-foreground">Quiz not found</h2>
            <Button onClick={() => setLocation("/")} data-testid="button-back-home">
              Back to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const sortedQuestions = [...questions].sort((a, b) => a.order - b.order);
  const progress = ((currentQuestion + 1) / sortedQuestions.length) * 100;

  if (!started) {
    return (
      <div className="min-h-screen bg-background">
        <header className="bg-gradient-to-r from-primary to-chart-3 text-primary-foreground py-6">
          <div className="max-w-2xl mx-auto px-6">
            <Button
              variant="ghost"
              className="mb-4 text-primary-foreground hover:bg-white/10"
              onClick={() => setLocation("/")}
              data-testid="button-back"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <h1 className="text-4xl font-bold">{quiz.title}</h1>
          </div>
        </header>

        <main className="max-w-2xl mx-auto px-6 py-12">
          <Card className="p-8">
            <CardContent className="p-0 space-y-6">
              <div className="text-center space-y-4">
                <div className="w-20 h-20 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
                  <CheckCircle className="w-10 h-10 text-primary" />
                </div>
                <h2 className="text-3xl font-bold text-foreground">
                  Let's Get Started!
                </h2>
                <p className="text-xl text-muted-foreground">
                  This quiz has {sortedQuestions.length} questions
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="student-name" className="text-lg">
                  What's your name?
                </Label>
                <Input
                  id="student-name"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  placeholder="Enter your name"
                  className="text-lg h-14"
                  data-testid="input-student-name"
                />
              </div>

              <Button
                onClick={handleStart}
                size="lg"
                className="w-full text-xl py-6"
                data-testid="button-start-quiz"
              >
                Start Quiz
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  const question = sortedQuestions[currentQuestion];
  const isLastQuestion = currentQuestion === sortedQuestions.length - 1;

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-gradient-to-r from-primary to-chart-3 text-primary-foreground py-4">
        <div className="max-w-3xl mx-auto px-6">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-2xl font-bold">{quiz.title}</h1>
            <span className="text-lg font-semibold">
              {currentQuestion + 1} / {sortedQuestions.length}
            </span>
          </div>
          <Progress value={progress} className="h-3 bg-white/20" />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12">
        <Card className="p-8 mb-6">
          <CardContent className="p-0 space-y-8">
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Question {currentQuestion + 1}
              </p>
              <h2 className="text-3xl font-bold text-foreground leading-relaxed">
                {question.questionText}
              </h2>
            </div>

            <RadioGroup
              value={answers[currentQuestion]?.toString()}
              onValueChange={(value) => handleAnswer(parseInt(value))}
              className="space-y-4"
            >
              {question.options.map((option, index) => (
                <Card
                  key={index}
                  className={`cursor-pointer transition-all hover-elevate ${
                    answers[currentQuestion] === index
                      ? "border-2 border-primary bg-primary/5"
                      : "border-2"
                  }`}
                  onClick={() => handleAnswer(index)}
                  data-testid={`option-${index}`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4">
                      <RadioGroupItem
                        value={index.toString()}
                        id={`option-${index}`}
                        className="w-6 h-6"
                      />
                      <Label
                        htmlFor={`option-${index}`}
                        className="text-xl cursor-pointer flex-1"
                      >
                        {option}
                      </Label>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </RadioGroup>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          {isLastQuestion ? (
            <Button
              onClick={handleSubmit}
              size="lg"
              className="text-xl px-8"
              disabled={submitMutation.isPending}
              data-testid="button-submit-quiz"
            >
              {submitMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                "Submit Quiz"
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              size="lg"
              className="text-xl px-8"
              data-testid="button-next-question"
            >
              Next Question
            </Button>
          )}
        </div>
      </main>
    </div>
  );
}
