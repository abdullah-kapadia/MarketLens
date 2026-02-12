import { useState, useCallback } from "react";
import { StockSelector } from "@/components/StockSelector";
import { TerminalLog } from "@/components/TerminalLog";
import { DocumentPreview } from "@/components/DocumentPreview";
import { analyzeStock, listReports, getReportDetail } from "@/lib/api";
import type { ReportDetail, AgentStep } from "@/lib/api-types";

const Index = () => {
  const [selectedTicker, setSelectedTicker] = useState("AAPL");
  const [isProcessing, setIsProcessing] = useState(false);
  const [reportReady, setReportReady] = useState(false);
  const [currentReport, setCurrentReport] = useState<ReportDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sseEvents, setSseEvents] = useState<AgentStep[]>([]);

  const handleInitialize = useCallback(() => {
    setReportReady(false);
    setIsProcessing(true);
    setError(null);
    setCurrentReport(null);
    setSseEvents([]);

    const onMessage = (step: AgentStep) => {
      console.log('[Index] Processing step:', step.type, step);
      setSseEvents((prev) => {
        const updated = [...prev, step];
        console.log('[Index] Updated sseEvents length:', updated.length);
        return updated;
      });

      if (step.type === "complete") {
        console.log('[Index] Complete event received!', step);
        const reportId = step.report_id;
        if (reportId) {
          console.log('[Index] Fetching report details for:', reportId);
          getReportDetail(reportId)
            .then((reportDetail) => {
              console.log('[Index] Report fetched successfully:', reportDetail);
              setCurrentReport(reportDetail);
              setReportReady(true);
            })
            .catch((err) => {
              console.error("[Index] Error fetching report detail:", err);
              setError("Analysis complete, but failed to fetch report details.");
              setReportReady(true); // Still show ready, but with error
            });
        } else {
          console.error("[Index] Complete event received without report_id.");
          setError("Analysis completed, but no report ID was provided.");
          setReportReady(true);
        }
      } else if (step.type === "error") {
        setError(`Analysis failed: ${step.content || 'Unknown error'}`);
        setReportReady(false); // Analysis failed, so report is not ready
      }
    };

    const onError = (err: any) => {
      console.error("SSE Error:", err);
      setError("SSE connection error. Analysis might have failed.");
      setIsProcessing(false);
      setReportReady(false); // Analysis failed, so report is not ready
    };

    const onComplete = () => {
      setIsProcessing(false);
    };

    analyzeStock(selectedTicker, onMessage, onError, onComplete);

  }, [selectedTicker]);

  const handleComplete = useCallback(() => {
    setIsProcessing(false);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Top Bar */}
      <div className="border-b border-border">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-4">
            <span className="font-mono text-[10px] font-bold tracking-[0.3em] text-muted-foreground">
              THE
            </span>
            <h1 className="font-serif text-lg font-bold tracking-tight">Automated Analyst</h1>
          </div>
          <div className="flex items-center gap-6 font-mono text-[10px] text-muted-foreground tracking-wider">
            <span>SYS: ONLINE</span>
            <span className="w-1.5 h-1.5 bg-terminal-green" />
            <span>{new Date().toLocaleDateString("en-US").toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex min-h-[calc(100vh-49px)]">
        {/* Left Column — Controls */}
        <div className="w-1/4 min-w-[280px] max-w-[360px] border-r border-border flex flex-col">
          {/* Header */}
          <div className="border-b border-border px-5 py-4">
            <h2 className="font-mono text-xs font-bold tracking-[0.2em]">AUTOMATED ANALYST</h2>
            <div className="font-mono text-[10px] text-muted-foreground mt-1 tracking-wider">
              REPORT GENERATION PIPELINE v2.1
            </div>
          </div>

          {/* Controls */}
          <div className="flex-1 px-5 py-6 space-y-8">
            <StockSelector
              selected={selectedTicker}
              onSelect={setSelectedTicker}
              disabled={isProcessing}
            />

            <div className="w-full h-px bg-border" />

            {/* Terminal Log */}
            <TerminalLog
              isRunning={isProcessing}
              onComplete={handleComplete}
              ticker={selectedTicker}
              sseEvents={sseEvents}
            />
          </div>

          {/* Trigger Button */}
          <div className="p-5 border-t border-border mt-auto">
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleInitialize}
              className="w-full py-4 bg-foreground text-background font-mono text-xs font-bold 
                         tracking-[0.2em] uppercase border border-border
                         hover:bg-swiss-red hover:text-primary-foreground
                         active:translate-y-[1px]
                         transition-colors duration-150
                         disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-foreground"
            >
              {isProcessing ? "PROCESSING..." : "INITIALIZE REPORT SEQUENCE"}
            </button>
          </div>
        </div>

        {/* Right Column — Preview Canvas */}
        <div className="flex-1 bg-muted/30 overflow-auto">
          {/* Canvas Header */}
          <div className="border-b border-border px-6 py-2 flex items-center justify-between bg-background">
            <div className="flex items-center gap-4">
              <span className="label-mono">Output Preview</span>
              {reportReady && (
                <span className="font-mono text-[10px] text-terminal-green tracking-wider font-bold">
                  ● REPORT READY
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 font-mono text-[10px] text-muted-foreground">
              <span>TICKER: {selectedTicker}</span>
            </div>
          </div>

          {/* Document Preview Area */}
          <DocumentPreview 
            ticker={selectedTicker} 
            isReady={reportReady} 
            report={currentReport}
          />
        </div>
      </div>
    </div>
  );
};

export default Index;
