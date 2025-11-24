import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { X, Plus, Trash2, Loader2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import type { Lecture, InsertQuestion } from "@shared/schema";

interface QuizBuilderProps {
  lectureId: string;
  onClose: () => void;
  onSuccess: () => void;
}

interface QuestionData {
  questionText: string;
  options: [string, string, string, string];
  correctAnswer: number;
}

export function QuizBuilder({ lectureId, onClose, onSuccess }: QuizBuilderProps) {
  const [quizTitle, setQuizTitle] = useState("");
  const [questions, setQuestions] = useState<QuestionData[]>([
    { questionText: "", options: ["", "", "", ""], correctAnswer: 0 },
  ]);
  const { toast } = useToast();

  const { data: lecture } = useQuery<Lecture>({
    queryKey: ["/api/lectures", lectureId],
  });

  const createMutation = useMutation({
    mutationFn: async (data: {
      quizTitle: string;
      lectureId: string;
      questions: InsertQuestion[];
    }) => {
      return await apiRequest("POST", "/api/quizzes", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/quizzes"] });
      toast({
        title: "Success!",
        description: "Quiz created successfully",
      });
      onSuccess();
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const generateMutation = useMutation({
    mutationFn: async (count: number) => {
      const res = await apiRequest("POST", "/api/quizzes/generate", { lectureId, count });
      return await res.json();
    },
    onSuccess: (data: any) => {
      const generated = Array.isArray(data) ? data : [];
      if (generated.length === 0) {
        toast({
          title: "No questions generated",
          description: "Try again or adjust the lecture content.",
          variant: "destructive",
        });
        return;
      }
      const mapped: QuestionData[] = generated.map((q: any) => ({
        questionText: String(q.questionText || ""),
        options: [0, 1, 2, 3].map((i) => String(q?.options?.[i] ?? "")) as [
          string,
          string,
          string,
          string
        ],
        correctAnswer: Number.isInteger(q?.correctAnswer) ? q.correctAnswer : 0,
      }));
      setQuestions(mapped);
      toast({
        title: "Questions generated",
        description: "Review and edit before creating the quiz.",
      });
    },
    onError: (error: Error) => {
      toast({ title: "Generation failed", description: error.message, variant: "destructive" });
    },
  });

  const addQuestion = () => {
    if (questions.length >= 10) {
      toast({
        title: "Maximum reached",
        description: "You can only add up to 10 questions",
        variant: "destructive",
      });
      return;
    }
    setQuestions([
      ...questions,
      { questionText: "", options: ["", "", "", ""], correctAnswer: 0 },
    ]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const updateQuestion = (index: number, field: keyof QuestionData, value: any) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value };
    setQuestions(updated);
  };

  const updateOption = (qIndex: number, oIndex: number, value: string) => {
    const updated = [...questions];
    const newOptions = [...updated[qIndex].options] as [string, string, string, string];
    newOptions[oIndex] = value;
    updated[qIndex] = { ...updated[qIndex], options: newOptions };
    setQuestions(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!quizTitle) {
      toast({
        title: "Missing title",
        description: "Please enter a quiz title",
        variant: "destructive",
      });
      return;
    }

    if (questions.length === 0) {
      toast({
        title: "No questions",
        description: "Please add at least one question",
        variant: "destructive",
      });
      return;
    }

    const invalidQuestion = questions.find(
      (q) =>
        !q.questionText ||
        q.options.some((opt) => !opt) ||
        q.correctAnswer < 0 ||
        q.correctAnswer > 3
    );

    if (invalidQuestion) {
      toast({
        title: "Incomplete question",
        description: "Please fill in all question fields and options",
        variant: "destructive",
      });
      return;
    }

    const formattedQuestions: InsertQuestion[] = questions.map((q, index) => ({
      quizId: "",
      questionText: q.questionText,
      options: q.options,
      correctAnswer: q.correctAnswer,
      order: index,
    }));

    createMutation.mutate({
      quizTitle,
      lectureId,
      questions: formattedQuestions,
    });
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="text-2xl">Create Quiz</CardTitle>
            {lecture && (
              <p className="text-sm text-muted-foreground mt-1">
                For lecture: {lecture.title}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            data-testid="button-close-quiz-builder"
          >
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="quiz-title">Quiz Title</Label>
              <Input
                id="quiz-title"
                value={quizTitle}
                onChange={(e) => setQuizTitle(e.target.value)}
                placeholder="e.g., Numbers Quiz"
                data-testid="input-quiz-title"
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-lg">
                  Questions
                </Label>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => generateMutation.mutate(5)}
                    disabled={generateMutation.isPending}
                    data-testid="button-generate-questions"
                  >
                    {generateMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      "Generate with AI"
                    )}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addQuestion}
                    disabled={questions.length >= 10}
                    data-testid="button-add-question"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Question
                  </Button>
                </div>
              </div>

              {questions.map((question, qIndex) => (
                <Card key={qIndex} data-testid={`question-card-${qIndex}`}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                    <CardTitle className="text-base">
                      Question {qIndex + 1}
                    </CardTitle>
                    {questions.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeQuestion(qIndex)}
                        data-testid={`button-remove-question-${qIndex}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label>Question Text</Label>
                      <Input
                        value={question.questionText}
                        onChange={(e) =>
                          updateQuestion(qIndex, "questionText", e.target.value)
                        }
                        placeholder="Enter the question"
                        data-testid={`input-question-text-${qIndex}`}
                      />
                    </div>

                    <div className="space-y-3">
                      <Label>Answer Options</Label>
                      <RadioGroup
                        value={question.correctAnswer.toString()}
                        onValueChange={(value) =>
                          updateQuestion(qIndex, "correctAnswer", parseInt(value))
                        }
                      >
                        {question.options.map((option, oIndex) => (
                          <div key={oIndex} className="flex items-center gap-3">
                            <RadioGroupItem
                              value={oIndex.toString()}
                              id={`q${qIndex}-opt${oIndex}`}
                              data-testid={`radio-correct-answer-${qIndex}-${oIndex}`}
                            />
                            <Input
                              value={option}
                              onChange={(e) =>
                                updateOption(qIndex, oIndex, e.target.value)
                              }
                              placeholder={`Option ${oIndex + 1}`}
                              className="flex-1"
                              data-testid={`input-option-${qIndex}-${oIndex}`}
                            />
                            <Label
                              htmlFor={`q${qIndex}-opt${oIndex}`}
                              className="text-xs text-muted-foreground cursor-pointer"
                            >
                              {question.correctAnswer === oIndex && (
                                <CheckCircle className="w-4 h-4 text-chart-2" />
                              )}
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                      <p className="text-xs text-muted-foreground">
                        Select the correct answer
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="flex gap-3 justify-end pt-4 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={createMutation.isPending}
                data-testid="button-cancel-quiz"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending}
                data-testid="button-create-quiz-submit"
              >
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create Quiz"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
