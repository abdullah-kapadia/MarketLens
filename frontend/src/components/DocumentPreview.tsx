import type { ReportDetail } from "@/lib/api-types";
import { FALLBACK_ANALYSIS } from "@/lib/fallback-data";
import { TechnicalChart } from "./TechnicalChart";

interface DocumentPreviewProps {
  ticker: string;
  isReady: boolean;
  report?: ReportDetail | null;
}

export function DocumentPreview({ ticker, isReady, report }: DocumentPreviewProps) {
  console.log('[DocumentPreview] Rendering - isReady:', isReady, 'report:', !!report);

  if (!isReady) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="font-mono text-xs text-muted-foreground tracking-[0.3em] uppercase">
            No report generated
          </div>
          <div className="w-16 h-px bg-border mx-auto" />
          <div className="font-mono text-[10px] text-muted-foreground/60 tracking-wider">
            SELECT TICKER → SET PARAMETERS → INITIALIZE
          </div>
        </div>
      </div>
    );
  }

  // Use report data if available, otherwise use fallback
  const analysis = report?.analysis || { ...FALLBACK_ANALYSIS, chart_config: { ...FALLBACK_ANALYSIS.chart_config, ticker } };
  const signalColor = analysis.signal === "BULLISH" ? "text-terminal-green" : 
                      analysis.signal === "BEARISH" ? "text-swiss-red" : 
                      "text-muted-foreground";
  
  return (
    <div className="flex justify-center py-8 px-4">
      <div className="paper-sheet border border-border bg-background w-full max-w-2xl">
        {/* Document Header */}
        <div className="border-b border-border px-10 py-8">
          <div className="flex items-start justify-between">
            <div>
              <div className="label-mono text-[10px] mb-1">Technical Analysis Report</div>
              <h2 className="font-serif text-3xl font-bold tracking-tight">{ticker}</h2>
              <div className={`font-mono text-xs font-bold tracking-wider mt-2 ${signalColor}`}>
                {analysis.signal} • {analysis.confidence} CONFIDENCE
              </div>
            </div>
            <div className="text-right font-mono text-[10px] text-muted-foreground space-y-0.5">
              <div>DATE: {new Date(report?.generated_at || Date.now()).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "2-digit" }).toUpperCase()}</div>
              <div>CLASS: EQUITY</div>
              <div>STATUS: <span className="text-terminal-green">FINAL</span></div>
              {report && (
                <div className="mt-2">
                  <div>TIME: {report.execution_time_ms}ms</div>
                  <div>CALLS: {report.tool_calls_count}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Thesis */}
        <div className="border-b border-border px-10 py-6 bg-muted/20">
          <div className="label-mono mb-2">Investment Thesis</div>
          <p className="font-serif text-base font-semibold leading-relaxed text-foreground">
            {analysis.thesis}
          </p>
        </div>

        {/* Executive Summary */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Executive Summary</div>
          <p className="font-serif text-sm leading-relaxed text-foreground/80" style={{ textAlign: "justify" }}>
            {analysis.summary}
          </p>
        </div>

        {/* Technical Analysis Chart */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Price Action & Indicators</div>
          {analysis.chart_config.data && analysis.chart_config.data.length > 0 ? (
            <TechnicalChart 
              data={analysis.chart_config.data}
              ticker={ticker}
              supportLevels={analysis.key_levels.support}
              resistanceLevels={analysis.key_levels.resistance}
            />
          ) : (
            <div className="crosshatch border border-border h-48 flex items-center justify-center">
              <div className="bg-background/80 px-4 py-2 border border-border">
                <span className="font-mono text-xs text-muted-foreground tracking-wider">
                  CHART: {ticker} — OHLCV + OVERLAY
                </span>
              </div>
            </div>
          )}
          <div className="flex justify-between mt-2 font-mono text-[10px] text-muted-foreground">
            <span>PERIOD: {analysis.chart_config.period}</span>
            <span>INTERVAL: 1D</span>
            <span>OVERLAYS: {analysis.chart_config.overlays.join(", ")}</span>
          </div>
        </div>

        {/* Detailed Analysis */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Detailed Analysis</div>
          <div className="space-y-3 font-serif text-sm">
            <div>
              <span className="font-bold text-foreground">Trend: </span>
              <span className="text-foreground/80">{analysis.detailed_analysis.trend}</span>
            </div>
            <div>
              <span className="font-bold text-foreground">Momentum: </span>
              <span className="text-foreground/80">{analysis.detailed_analysis.momentum}</span>
            </div>
            <div>
              <span className="font-bold text-foreground">Key Levels: </span>
              <span className="text-foreground/80">{analysis.detailed_analysis.key_levels}</span>
            </div>
            <div>
              <span className="font-bold text-foreground">Volume Context: </span>
              <span className="text-foreground/80">{analysis.detailed_analysis.volume_context}</span>
            </div>
            <div>
              <span className="font-bold text-foreground">Market Context: </span>
              <span className="text-foreground/80">{analysis.detailed_analysis.market_context}</span>
            </div>
          </div>
        </div>

        {/* Key Levels Table */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Key Price Levels</div>
          <div className="border border-border">
            <div className="flex items-center font-mono text-xs border-b border-border">
              <div className="w-1/3 px-3 py-2 font-bold tracking-wider border-r border-border bg-muted/30">
                SUPPORT
              </div>
              <div className="w-2/3 px-3 py-2">
                {analysis.key_levels.support.map(s => `$${s.toFixed(2)}`).join(", ")}
              </div>
            </div>
            <div className="flex items-center font-mono text-xs border-b border-border">
              <div className="w-1/3 px-3 py-2 font-bold tracking-wider border-r border-border bg-muted/30">
                RESISTANCE
              </div>
              <div className="w-2/3 px-3 py-2">
                {analysis.key_levels.resistance.map(r => `$${r.toFixed(2)}`).join(", ")}
              </div>
            </div>
            <div className="flex items-center font-mono text-xs border-b border-border">
              <div className="w-1/3 px-3 py-2 font-bold tracking-wider border-r border-border bg-muted/30">
                STOP LOSS
              </div>
              <div className="w-2/3 px-3 py-2 text-swiss-red">
                ${analysis.key_levels.stop_loss.toFixed(2)}
              </div>
            </div>
            <div className="flex items-center font-mono text-xs">
              <div className="w-1/3 px-3 py-2 font-bold tracking-wider border-r border-border bg-muted/30">
                TARGET
              </div>
              <div className="w-2/3 px-3 py-2 text-terminal-green">
                ${analysis.key_levels.target.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        {/* Evidence Chain */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Evidence Chain</div>
          <ul className="space-y-1.5 font-serif text-sm text-foreground/80">
            {analysis.evidence_chain.map((evidence, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-terminal-green font-mono shrink-0">✓</span>
                <span>{evidence}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Risk Factors */}
        <div className="border-b border-border px-10 py-6">
          <div className="label-mono mb-3">Risk Factors</div>
          <ul className="space-y-1.5 font-serif text-sm text-foreground/80">
            {analysis.risk_factors.map((risk, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-swiss-red font-mono shrink-0">⚠</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Final Commentary */}
        <div className="px-10 py-6">
          <div className="label-mono mb-3">Final Commentary</div>
          <p className="font-serif text-sm leading-relaxed text-foreground/80" style={{ textAlign: "justify" }}>
            {analysis.final_commentary || analysis.summary}
          </p>
          <div className="mt-6 pt-4 border-t border-border flex justify-between items-end">
            <div className="font-mono text-[10px] text-muted-foreground">
              <div>GENERATED BY: AUTOMATED ANALYST v2.1.0</div>
              <div>DISCLAIMER: FOR INFORMATIONAL PURPOSES ONLY</div>
              {/* {!report && <div className="text-swiss-red mt-1">USING FALLBACK DATA</div>} */}
            </div>
            <div className="font-serif text-xs italic text-muted-foreground">
              — The Automated Analyst
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
