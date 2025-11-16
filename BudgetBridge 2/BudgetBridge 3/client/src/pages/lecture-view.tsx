import { useQuery } from "@tanstack/react-query";
import { useRoute, Link } from "wouter";
import { ArrowLeft, BookOpen, ClipboardCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Lecture, Quiz } from "@shared/schema";

export default function LectureView() {
  const [, params] = useRoute("/lecture/:id");
  const lectureId = params?.id;

  const { data: lecture, isLoading: lectureLoading } = useQuery<Lecture>({
    queryKey: ["/api/lectures", lectureId],
    enabled: !!lectureId,
  });

  const { data: quizzes } = useQuery<Quiz[]>({
    queryKey: ["/api/quizzes"],
  });

  const quiz = quizzes?.find((q) => q.lectureId === lectureId);

  if (lectureLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-16 h-16 mx-auto animate-spin text-primary" />
          <p className="text-xl text-muted-foreground">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (!lecture) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardContent className="py-12 text-center space-y-4">
            <BookOpen className="w-16 h-16 mx-auto text-muted-foreground" />
            <h2 className="text-2xl font-bold text-foreground">
              Lesson not found
            </h2>
            <Link href="/">
              <Button data-testid="button-back-home">Back to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-gradient-to-r from-primary to-chart-3 text-primary-foreground py-6">
        <div className="max-w-3xl mx-auto px-6">
          <Link href="/">
            <Button
              variant="ghost"
              className="mb-4 text-primary-foreground hover:bg-white/10"
              data-testid="button-back"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Lessons
            </Button>
          </Link>
          <h1 className="text-4xl font-bold mb-2">{lecture.title}</h1>
          <div
            className={`inline-block px-4 py-2 rounded-full text-lg font-semibold bg-white/20`}
          >
            {lecture.subject.charAt(0).toUpperCase() + lecture.subject.slice(1)}
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12">
        <Card className="p-8 mb-8">
          <CardContent className="p-0">
            <h2 className="text-3xl font-bold text-foreground mb-6 flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-primary" />
              What You'll Learn
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-2xl leading-relaxed text-foreground whitespace-pre-wrap">
                {lecture.summary || lecture.content}
              </p>
            </div>
          </CardContent>
        </Card>

        {quiz ? (
          <Card className="bg-gradient-to-r from-chart-2/10 to-chart-3/10 border-2 border-chart-2/30 p-8">
            <CardContent className="p-0 space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-chart-2 flex items-center justify-center">
                  <ClipboardCheck className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-foreground">
                    Ready for the Quiz?
                  </h3>
                  <p className="text-lg text-muted-foreground">
                    Test what you learned!
                  </p>
                </div>
              </div>
              <Link href={`/quiz/${quiz.id}`}>
                <Button
                  size="lg"
                  className="w-full text-xl py-6"
                  data-testid="button-start-quiz"
                >
                  Start Quiz
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <Card className="p-8 border-2 border-dashed">
            <CardContent className="p-0 text-center space-y-4">
              <ClipboardCheck className="w-12 h-12 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  No Quiz Yet
                </h3>
                <p className="text-base text-muted-foreground">
                  Your teacher hasn't added a quiz for this lesson yet.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
