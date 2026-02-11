import { useEffect, useRef, useState } from "react";

interface LogEntry {
  status: "done" | "active" | "pending";
  text: string;
}

const REPORT_STEPS: string[] = [
  "CONNECTING TO MARKET DATA FEED",
  "FETCHING OHLCV DATA",
  "VALIDATING PRICE INTEGRITY",
  "CALCULATING RSI (14-PERIOD)",
  "CALCULATING MACD (12,26,9)",
  "COMPUTING BOLLINGER BANDS",
  "ANALYZING SUPPORT/RESISTANCE",
  "RUNNING VOLUME PROFILE",
  "GENERATING TREND ANALYSIS",
  "COMPILING RISK METRICS",
  "WRITING EXECUTIVE SUMMARY",
  "FORMATTING REPORT LAYOUT",
  "RENDERING CHARTS",
  "FINALIZING DOCUMENT",
];

interface TerminalLogProps {
  isRunning: boolean;
  onComplete: () => void;
  ticker: string;
}

export function TerminalLog({ isRunning, onComplete, ticker }: TerminalLogProps) {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [currentStep, setCurrentStep] = useState(-1);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isRunning) {
      setEntries([]);
      setCurrentStep(-1);
      return;
    }

    setEntries([]);
    setCurrentStep(0);

    const timers: ReturnType<typeof setTimeout>[] = [];

    REPORT_STEPS.forEach((step, i) => {
      // Show step as active
      const showTimer = setTimeout(() => {
        setEntries((prev) => [
          ...prev.map((e) => ({ ...e, status: "done" as const })),
          { status: "active" as const, text: step },
        ]);
        setCurrentStep(i);
      }, i * 600 + 200);

      timers.push(showTimer);

      // Mark as done
      if (i < REPORT_STEPS.length - 1) {
        const doneTimer = setTimeout(() => {
          setEntries((prev) =>
            prev.map((e, idx) => (idx === i ? { ...e, status: "done" as const } : e))
          );
        }, (i + 1) * 600 + 100);
        timers.push(doneTimer);
      }
    });

    // Complete
    const completeTimer = setTimeout(() => {
      setEntries((prev) => prev.map((e) => ({ ...e, status: "done" as const })));
      onComplete();
    }, REPORT_STEPS.length * 600 + 400);
    timers.push(completeTimer);

    return () => timers.forEach(clearTimeout);
  }, [isRunning, onComplete]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [entries]);

  const timestamp = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
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
            <span className="text-background/40 shrink-0">{timestamp()}</span>
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
      </div>
    </div>
  );
}
