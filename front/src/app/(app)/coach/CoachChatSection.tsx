"use client";

import { CoachChat } from "@/components/CoachChat";

interface CoachChatSectionProps {
  assessmentId: string;
}

export function CoachChatSection({ assessmentId }: CoachChatSectionProps) {
  return <CoachChat assessmentId={assessmentId} />;
}

