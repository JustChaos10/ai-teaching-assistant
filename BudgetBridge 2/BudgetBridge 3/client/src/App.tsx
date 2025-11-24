import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import StudentDashboard from "@/pages/student-dashboard";
import TeacherDashboard from "@/pages/teacher-dashboard";
import LectureView from "@/pages/lecture-view";
import QuizTaking from "@/pages/quiz-taking";
import QuizResults from "@/pages/quiz-results";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={StudentDashboard} />
      <Route path="/teacher" component={TeacherDashboard} />
      <Route path="/lecture/:id" component={LectureView} />
      <Route path="/quiz/:id" component={QuizTaking} />
      <Route path="/results/:id" component={QuizResults} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
