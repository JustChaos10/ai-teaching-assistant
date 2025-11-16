import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "wouter";
import { Plus, BookOpen, ClipboardList, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import type { Lecture, Quiz } from "@shared/schema";
import { LectureUpload } from "@/components/lecture-upload";
import { QuizBuilder } from "@/components/quiz-builder";

export default function TeacherDashboard() {
  const [showLectureUpload, setShowLectureUpload] = useState(false);
  const [showQuizBuilder, setShowQuizBuilder] = useState(false);
  const [selectedLecture, setSelectedLecture] = useState<string | null>(null);
  const { toast } = useToast();

  const { data: lectures, isLoading: lecturesLoading } = useQuery<Lecture[]>({
    queryKey: ["/api/lectures"],
  });

  const { data: quizzes, isLoading: quizzesLoading } = useQuery<Quiz[]>({
    queryKey: ["/api/quizzes"],
  });

  const deleteLectureMutation = useMutation({
    mutationFn: async (lectureId: string) => {
      return await apiRequest("DELETE", `/api/lectures/${lectureId}`, undefined);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/lectures"] });
      toast({
        title: "Success",
        description: "Lecture deleted successfully",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const deleteQuizMutation = useMutation({
    mutationFn: async (quizId: string) => {
      return await apiRequest("DELETE", `/api/quizzes/${quizId}`, undefined);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/quizzes"] });
      toast({
        title: "Success",
        description: "Quiz deleted successfully",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleDeleteLecture = (e: React.MouseEvent, lectureId: string) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this lecture?")) {
      deleteLectureMutation.mutate(lectureId);
    }
  };

  const handleDeleteQuiz = (e: React.MouseEvent, quizId: string) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this quiz?")) {
      deleteQuizMutation.mutate(quizId);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-primary" />
            <h1 className="text-2xl font-semibold text-foreground">Teacher Dashboard</h1>
          </div>
          <Link href="/" data-testid="link-student-view">
            <Button variant="outline" data-testid="button-student-view">
              Student View
            </Button>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Tabs defaultValue="lectures" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="lectures" data-testid="tab-lectures">
              Lectures
            </TabsTrigger>
            <TabsTrigger value="quizzes" data-testid="tab-quizzes">
              Quizzes
            </TabsTrigger>
          </TabsList>

          <TabsContent value="lectures" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-foreground">Manage Lectures</h2>
              <Button
                onClick={() => setShowLectureUpload(true)}
                data-testid="button-create-lecture"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Lecture
              </Button>
            </div>

            {lecturesLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="animate-pulse">
                    <CardHeader className="space-y-2">
                      <div className="h-6 bg-muted rounded" />
                      <div className="h-4 bg-muted rounded w-20" />
                    </CardHeader>
                    <CardContent>
                      <div className="h-4 bg-muted rounded" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : lectures && lectures.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {lectures.map((lecture) => (
                  <Card
                    key={lecture.id}
                    className="hover-elevate cursor-pointer"
                    onClick={() => {
                      setSelectedLecture(lecture.id);
                      setShowQuizBuilder(true);
                    }}
                    data-testid={`card-lecture-${lecture.id}`}
                  >
                    <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-3">
                      <div className="space-y-1 flex-1">
                        <CardTitle className="text-lg">{lecture.title}</CardTitle>
                        <p className="text-sm text-muted-foreground capitalize">
                          {lecture.subject}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => handleDeleteLecture(e, lecture.id)}
                        data-testid={`button-delete-lecture-${lecture.id}`}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {lecture.summary || lecture.content}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="py-12">
                <CardContent className="text-center space-y-4">
                  <BookOpen className="w-16 h-16 mx-auto text-muted-foreground" />
                  <p className="text-muted-foreground">
                    No lectures yet. Create your first lecture to get started!
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="quizzes" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-foreground">Manage Quizzes</h2>
            </div>

            {quizzesLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <Card key={i} className="animate-pulse">
                    <CardHeader className="space-y-2">
                      <div className="h-6 bg-muted rounded" />
                    </CardHeader>
                    <CardContent>
                      <div className="h-4 bg-muted rounded" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : quizzes && quizzes.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {quizzes.map((quiz) => {
                  const lecture = lectures?.find((l) => l.id === quiz.lectureId);
                  return (
                    <Card key={quiz.id} data-testid={`card-quiz-${quiz.id}`}>
                      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-3">
                        <div className="space-y-1 flex-1">
                          <CardTitle className="text-lg">{quiz.title}</CardTitle>
                          {lecture && (
                            <p className="text-sm text-muted-foreground">
                              {lecture.title}
                            </p>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => handleDeleteQuiz(e, quiz.id)}
                          data-testid={`button-delete-quiz-${quiz.id}`}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xs text-muted-foreground">
                          Created {new Date(quiz.createdAt).toLocaleDateString()}
                        </p>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <Card className="py-12">
                <CardContent className="text-center space-y-4">
                  <ClipboardList className="w-16 h-16 mx-auto text-muted-foreground" />
                  <p className="text-muted-foreground">
                    No quizzes yet. Select a lecture to create a quiz!
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </main>

      {showLectureUpload && (
        <LectureUpload
          onClose={() => setShowLectureUpload(false)}
          onSuccess={() => setShowLectureUpload(false)}
        />
      )}

      {showQuizBuilder && selectedLecture && (
        <QuizBuilder
          lectureId={selectedLecture}
          onClose={() => {
            setShowQuizBuilder(false);
            setSelectedLecture(null);
          }}
          onSuccess={() => {
            setShowQuizBuilder(false);
            setSelectedLecture(null);
          }}
        />
      )}
    </div>
  );
}
