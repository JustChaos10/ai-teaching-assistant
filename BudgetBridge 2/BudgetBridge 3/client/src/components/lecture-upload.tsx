import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { X, Upload, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import type { InsertLecture } from "@shared/schema";
import { GlobalWorkerOptions, getDocument } from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

interface LectureUploadProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function LectureUpload({ onClose, onSuccess }: LectureUploadProps) {
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [content, setContent] = useState("");
  const [pdfName, setPdfName] = useState<string | null>(null);
  const [parsing, setParsing] = useState(false);
  const { toast } = useToast();

  const createMutation = useMutation({
    mutationFn: async (data: InsertLecture) => {
      return await apiRequest("POST", "/api/lectures", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/lectures"] });
      toast({
        title: "Success!",
        description: "Lecture created and summary generated",
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !subject || !content) {
      toast({
        title: "Missing fields",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    createMutation.mutate({ title, subject, content });
  };

  GlobalWorkerOptions.workerSrc = pdfWorker;

  const handlePdfSelect = async (file: File | null) => {
    if (!file) return;
    if (file.type !== "application/pdf") {
      toast({
        title: "Invalid file",
        description: "Please upload a PDF file.",
        variant: "destructive",
      });
      return;
    }
    setParsing(true);
    setPdfName(file.name);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = getDocument({ data: arrayBuffer });
      const pdf = await loadingTask.promise;
      let fullText = "";
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items
          .map((item: any) => ("str" in item ? item.str : (item as any).text || ""))
          .join(" ");
        fullText += (pageNum > 1 ? "\n\n" : "") + pageText.trim();
      }
      if (!fullText) {
        toast({
          title: "No text found",
          description: "The selected PDF appears to have no extractable text.",
        });
      }
      setContent((prev) => (prev ? prev + "\n\n" + fullText : fullText));
      toast({ title: "PDF imported", description: "Content populated from PDF." });
    } catch (err: any) {
      toast({
        title: "Failed to read PDF",
        description: err?.message || "An error occurred while extracting text.",
        variant: "destructive",
      });
    } finally {
      setParsing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-2xl">Create New Lecture</CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            data-testid="button-close-lecture-upload"
          >
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Lecture Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Learning Numbers 1-10"
                data-testid="input-lecture-title"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Select value={subject} onValueChange={setSubject}>
                <SelectTrigger id="subject" data-testid="select-subject">
                  <SelectValue placeholder="Choose a subject" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="math">Math</SelectItem>
                  <SelectItem value="english">English</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="pdf">Upload PDF (optional)</Label>
              <div className="flex items-center gap-3">
                <Input
                  id="pdf"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => handlePdfSelect(e.target.files?.[0] || null)}
                  data-testid="input-lecture-pdf"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setPdfName(null);
                  }}
                  disabled={parsing}
                  data-testid="button-clear-pdf"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Clear
                </Button>
              </div>
              {pdfName && (
                <p className="text-sm text-muted-foreground">Selected: {pdfName}{parsing ? " (extracting...)" : ""}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="content">Lecture Content</Label>
              <Textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write the full lecture content here. The AI will create a simple summary for Grade 1 students."
                className="min-h-48"
                data-testid="textarea-lecture-content"
              />
              <p className="text-sm text-muted-foreground">
                The AI will automatically create a child-friendly summary
              </p>
            </div>

            <div className="flex gap-3 justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={createMutation.isPending}
                data-testid="button-cancel"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || parsing}
                data-testid="button-create-lecture-submit"
              >
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create Lecture
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

