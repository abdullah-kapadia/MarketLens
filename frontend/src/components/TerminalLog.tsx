import { useEffect, useRef, useState } from "react";
import { AgentStep } from "@/lib/api-types";

interface LogEntry {
  status: "done" | "active" | "pending";
  text: string;
  timestamp?: string;
}

interface TerminalLogProps {
  isRunning: boolean;
  onComplete: () => void; // This will now be primarily for signaling completion from parent
  ticker: string;
  sseEvents: AgentStep[];
}

// Helper function to format tool arguments
function formatToolArgs(args: Record<string, any> | null): string {
  if (!args) return "";
  const entries = Object.entries(args);
  if (entries.length === 0) return "";
  return entries
    .map(([key, value]) => {
      if (typeof value === "string") return `${key}="${value}"`;
      if (typeof value === "object") return `${key}={...}`;
      return `${key}=${value}`;
    })
    .join(", ");
}

// Helper function to format observation results
function formatObservation(result: any): string {
  if (!result) return "null";
  if (typeof result === "string") {
    return result.length > 200 ? result.substring(0, 200) + "..." : result;
  }
  if (typeof result === "object") {
    const str = JSON.stringify(result, null, 0);
    return str.length > 200 ? str.substring(0, 200) + "...}" : str;
  }
  return String(result);
}

export function TerminalLog({ isRunning, onComplete, ticker, sseEvents }: TerminalLogProps) {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('[TerminalLog] useEffect triggered - isRunning:', isRunning, 'sseEvents.length:', sseEvents.length);

    // Clear entries when analysis starts or stops
    if (!isRunning) {
      setEntries([]);
      return;
    }

    // Process SSE events into log entries
    const newEntries: LogEntry[] = [];
    sseEvents.forEach((step, i) => {
      let text = "";
      let status: LogEntry["status"] = "done";

      if (step.type === "reasoning") {
        const reasoning = step.content || "";
        const truncated = reasoning.length > 150 ? reasoning.substring(0, 150) + "..." : reasoning;
        text = `[#${step.iteration}] REASONING: ${truncated}`;
      } else if (step.type === "tool_call") {
        const argsStr = step.tool_input ? formatToolArgs(step.tool_input) : "";
        text = `[#${step.iteration}] TOOL CALL: ${step.tool_name}(${argsStr})`;
      } else if (step.type === "observation") {
        const resultStr = formatObservation(step.result);
        text = `[#${step.iteration}] OBSERVATION: ${resultStr}`;
      } else if (step.type === "error") {
        text = `[#${step.iteration}] ERROR: ${step.content}${step.code ? ` (Code: ${step.code})` : ""}`;
        status = "active"; // Mark error as active/critical
      } else if (step.type === "complete") {
        const execTime = step.execution_time_ms ? (step.execution_time_ms / 1000).toFixed(2) : "N/A";
        const toolCalls = step.tool_calls_count || 0;
        text = `ANALYSIS COMPLETE in ${execTime}s (${toolCalls} tool calls) | REPORT ID: ${step.report_id}`;
      } else {
        text = `UNKNOWN EVENT: ${JSON.stringify(step)}`;
      }

      // Mark the last received step as active if analysis is still running
      if (isRunning && i === sseEvents.length - 1 && step.type !== "complete" && step.type !== "error") {
        status = "active";
      }

      newEntries.push({ status, text, timestamp: step.timestamp });
    });

    console.log('[TerminalLog] Setting entries, count:', newEntries.length);
    setEntries(newEntries);

    // Call onComplete only when the SSE stream signals completion
    if (sseEvents.some(step => step.type === "complete")) {
      onComplete();
    }

  }, [sseEvents, isRunning, onComplete]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries]);

  const formatTimestamp = (dateString?: string) => {
    const date = dateString ? new Date(dateString) : new Date();
    return `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}:${date.getSeconds().toString().padStart(2, "0")}`;
  };

  return (
    <div className="border border-border bg-foreground text-background font-mono text-xs">
      {/* Terminal header */}
      <div className="flex items-center justify-between border-b border-rule px-3 py-1.5 bg-foreground">
        <span className="font-bold tracking-widest text-[10px]">PROCESS_LOG</span>
        <span className="text-background/50 text-[10px]">
          {isRunning ? `PID:${Math.floor(Math.random() * 9000 + 1000)}` : "IDLE"}
        </span>
      </div>

      {/* Terminal body */}
      <div ref={scrollRef} className="p-3 h-48 overflow-y-auto space-y-0.5">
        {!isRunning && entries.length === 0 && (
          <div className="text-background/30">
            <p>AUTOMATED ANALYST v2.1.0</p>
            <p>READY. SELECT TICKER AND INITIALIZE.</p>
            <p className="mt-2">
              {">"} <span className="terminal-cursor">█</span>
            </p>
          </div>
        )}

        {entries.map((entry, i) => (
          <div key={i} className="terminal-line-enter flex items-start gap-2">
            <span className="text-background/40 shrink-0">{formatTimestamp(entry.timestamp)}</span>
            <span className="shrink-0">
              {entry.status === "done" ? (
                <span className="text-terminal-green">[✓]</span>
              ) : (
                <span className="text-terminal-amber">[»]</span>
              )}
            </span>
            <span className={entry.status === "active" ? "text-background" : "text-background/60"}>
              {entry.text}
              {entry.status === "active" && <span className="terminal-cursor ml-1">█</span>}
            </span>
          </div>
        ))}

        {entries.length > 0 && !isRunning && (
          <div className="terminal-line-enter mt-2 pt-2 border-t border-background/20">
            <span className="text-terminal-green font-bold">
              [COMPLETE] REPORT FOR {ticker} GENERATED SUCCESSFULLY
            </span>
          </div>
        )}
         {entries.length > 0 && sseEvents.some(step => step.type === "error") && (
          <div className="terminal-line-enter mt-2 pt-2 border-t border-background/20">
            <span className="text-swiss-red font-bold">
              [ERROR] ANALYSIS FOR {ticker} FAILED
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
