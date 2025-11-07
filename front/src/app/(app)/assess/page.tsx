import { redirect } from "next/navigation";

export default function AssessLegacyRedirect() {
  redirect("/app/chat");
}

