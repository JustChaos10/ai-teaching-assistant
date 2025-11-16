import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import { BookOpen, Star, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Lecture } from "@shared/schema";

export default function StudentDashboard() {
  const { data: lectures, isLoading } = useQuery<Lecture[]>({
    queryKey: ["/api/lectures"],
  });

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-gradient-to-r from-primary to-chart-3 text-primary-foreground py-8">
        <div className="max-w-4xl mx-auto px-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <BookOpen className="w-12 h-12" />
              <h1 className="text-4xl font-bold">Learning Adventure</h1>
            </div>
            <Link href="/teacher" data-testid="link-teacher-view">
              <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20" data-testid="button-teacher-view">
                <Users className="w-4 h-4 mr-2" />
                Teacher
              </Button>
            </Link>
          </div>
          <p className="text-xl text-primary-foreground/90">
            Learn English and Math with fun lessons!
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            Choose a Lesson
          </h2>
          <p className="text-lg text-muted-foreground">
            Click on any lesson to start learning
          </p>
        </div>

        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="animate-pulse p-8">
                <div className="h-6 bg-muted rounded mb-4" />
                <div className="h-4 bg-muted rounded w-24" />
              </Card>
            ))}
          </div>
        ) : lectures && lectures.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2">
            {lectures.map((lecture) => (
              <Link key={lecture.id} href={`/lecture/${lecture.id}`}>
                <Card
                  className="hover-elevate active-elevate-2 cursor-pointer transition-all p-8 border-2"
                  data-testid={`card-lecture-${lecture.id}`}
                >
                  <CardContent className="p-0 space-y-4">
                    <div className="flex items-start justify-between">
                      <h3 className="text-2xl font-bold text-foreground">
                        {lecture.title}
                      </h3>
                      <div
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          lecture.subject === "math"
                            ? "bg-chart-3/20 text-chart-3"
                            : "bg-chart-5/20 text-chart-5"
                        }`}
                      >
                        {lecture.subject.charAt(0).toUpperCase() +
                          lecture.subject.slice(1)}
                      </div>
                    </div>
                    <p className="text-base text-muted-foreground line-clamp-2">
                      {lecture.summary || "Click to read this lesson!"}
                    </p>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Star className="w-4 h-4 fill-chart-4 text-chart-4" />
                      <span>New Lesson</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card className="py-16">
            <CardContent className="text-center space-y-6">
              <BookOpen className="w-24 h-24 mx-auto text-muted-foreground" />
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-foreground">
                  No Lessons Yet
                </h3>
                <p className="text-lg text-muted-foreground">
                  Your teacher will add lessons soon. Check back later!
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
