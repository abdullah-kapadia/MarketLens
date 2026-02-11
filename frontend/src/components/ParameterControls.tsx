interface ParameterControlsProps {
  timeframe: string;
  onTimeframeChange: (value: string) => void;
  sensitivity: string;
  onSensitivityChange: (value: string) => void;
  includeVolume: boolean;
  onIncludeVolumeChange: (value: boolean) => void;
  disabled?: boolean;
}

const TIMEFRAMES = ["1W", "1M", "3M", "6M", "1Y"];
const SENSITIVITIES = ["LOW", "MED", "HIGH"];

export function ParameterControls({
  timeframe,
  onTimeframeChange,
  sensitivity,
  onSensitivityChange,
  includeVolume,
  onIncludeVolumeChange,
  disabled,
}: ParameterControlsProps) {
  return (
    <div className="space-y-6">
      {/* Timeframe */}
      <div className="space-y-2">
        <label className="label-mono block">Timeframe</label>
        <div className="flex border border-border">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              type="button"
              disabled={disabled}
              onClick={() => onTimeframeChange(tf)}
              className={`flex-1 py-2 font-mono text-xs font-bold tracking-wider 
                         border-r border-border last:border-r-0
                         transition-colors duration-75
                         disabled:opacity-50 disabled:cursor-not-allowed
                         ${
                           tf === timeframe
                             ? "bg-foreground text-background"
                             : "bg-background text-foreground hover:bg-muted"
                         }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Sensitivity */}
      <div className="space-y-2">
        <label className="label-mono block">Indicator Sensitivity</label>
        <div className="flex border border-border">
          {SENSITIVITIES.map((s) => (
            <button
              key={s}
              type="button"
              disabled={disabled}
              onClick={() => onSensitivityChange(s)}
              className={`flex-1 py-2 font-mono text-xs font-bold tracking-wider 
                         border-r border-border last:border-r-0
                         transition-colors duration-75
                         disabled:opacity-50 disabled:cursor-not-allowed
                         ${
                           s === sensitivity
                             ? "bg-foreground text-background"
                             : "bg-background text-foreground hover:bg-muted"
                         }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Volume Toggle */}
      <div className="space-y-2">
        <label className="label-mono block">Include Volume Analysis</label>
        <button
          type="button"
          disabled={disabled}
          onClick={() => onIncludeVolumeChange(!includeVolume)}
          className="flex items-center gap-3 w-full py-2 font-mono text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div
            className={`w-10 h-5 border border-border relative transition-colors duration-150
                       ${includeVolume ? "bg-foreground" : "bg-background"}`}
          >
            <div
              className={`absolute top-0.5 w-3.5 h-3.5 transition-all duration-150
                         ${
                           includeVolume
                             ? "left-[calc(100%-18px)] bg-background"
                             : "left-0.5 bg-foreground"
                         }`}
            />
          </div>
          <span className="tracking-wider text-xs font-bold">
            {includeVolume ? "ENABLED" : "DISABLED"}
          </span>
        </button>
      </div>
    </div>
  );
}
