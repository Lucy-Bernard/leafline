"use client";

import { DiagnosisResult } from "@/lib/types/diagnosis.types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2 } from "lucide-react";
import { MarkdownMessage } from "@/components/ui/markdown-message";

interface DiagnosisResultDisplayProps {
  result: DiagnosisResult;
  onClose: () => void;
}

export function DiagnosisResultDisplay({
  result,
  onClose,
}: DiagnosisResultDisplayProps) {
  return (
    <Card className="w-full" data-testid="diagnosis-result-display">
      <CardHeader>
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          <CardTitle>Diagnosis Complete</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div>
            <h4 className="font-semibold text-sm text-muted-foreground mb-1">
              DIAGNOSIS
            </h4>
            <div data-testid="diagnosis-finding">
              <MarkdownMessage content={result.finding} className="font-semibold text-lg" />
            </div>
          </div>
          <Separator />
          <div>
            <h4 className="font-semibold text-sm text-muted-foreground mb-1">
              RECOMMENDATION
            </h4>
            <div data-testid="diagnosis-recommendation">
              <MarkdownMessage content={result.recommendation} />
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-4">
          <Button onClick={onClose} data-testid="close-diagnosis-result">
            Close
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
