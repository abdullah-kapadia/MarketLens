import React from "react";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
} from "recharts";

// Custom Candlestick Component
interface CandlestickProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  payload?: any;
  fill?: string;
}

const Candlestick: React.FC<CandlestickProps> = ({ x = 0, y = 0, width = 0, height = 0, payload }) => {
  if (!payload || !payload.open || !payload.close || !payload.high || !payload.low) {
    return null;
  }

  const { open, close, high, low } = payload;
  const isPositive = close > open;
  const fill = isPositive ? "#10b981" : "#ef4444"; // green for bullish, red for bearish
  const ratio = Math.abs(height / (payload.high - payload.low));

  return (
    <g>
      {/* Wick (high-low line) */}
      <line
        x1={x + width / 2}
        y1={y}
        x2={x + width / 2}
        y2={y + height}
        stroke={fill}
        strokeWidth={1}
      />
      {/* Body (open-close rectangle) */}
      <rect
        x={x + 1}
        y={isPositive ? y + (high - close) * ratio : y + (high - open) * ratio}
        width={Math.max(width - 2, 1)}
        height={Math.max(Math.abs((close - open) * ratio), 1)}
        fill={fill}
        stroke={fill}
      />
    </g>
  );
};

interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_9?: number;
  sma_50?: number;
  sma_200?: number;
  rsi?: number;
  upper_bb?: number;
  lower_bb?: number;
}

interface TechnicalChartProps {
  data: ChartDataPoint[];
  ticker: string;
  supportLevels?: number[];
  resistanceLevels?: number[];
}

export function TechnicalChart({ 
  data, 
  ticker, 
  supportLevels = [], 
  resistanceLevels = [] 
}: TechnicalChartProps) {
  // Calculate price domain with some padding
  const prices = data.flatMap(d => [d.low, d.high]);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const priceDomain = [
    Math.floor(minPrice - priceRange * 0.1),
    Math.ceil(maxPrice + priceRange * 0.1)
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background/95 border border-border p-3 font-mono text-[10px]">
          <div className="font-bold mb-1">{data.date}</div>
          <div className="space-y-0.5 text-[9px]">
            <div>O: ${data.open?.toFixed(2)}</div>
            <div>H: ${data.high?.toFixed(2)}</div>
            <div>L: ${data.low?.toFixed(2)}</div>
            <div>C: ${data.close?.toFixed(2)}</div>
            <div className="pt-1 border-t border-border mt-1">
              Vol: {(data.volume / 1000000).toFixed(2)}M
            </div>
            {data.rsi && <div>RSI: {data.rsi.toFixed(1)}</div>}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full space-y-2">
      {/* Main Price Chart */}
      <div className="w-full h-64 border border-border bg-background/50">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
              stroke="hsl(var(--border))"
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis
              yAxisId="price"
              domain={priceDomain}
              tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
              stroke="hsl(var(--border))"
              width={45}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Support and Resistance Lines */}
            {supportLevels.map((level, i) => (
              <ReferenceLine
                key={`support-${i}`}
                y={level}
                yAxisId="price"
                stroke="#10b981"
                strokeDasharray="5 5"
                strokeWidth={1.5}
                opacity={0.6}
              />
            ))}
            {resistanceLevels.map((level, i) => (
              <ReferenceLine
                key={`resistance-${i}`}
                y={level}
                yAxisId="price"
                stroke="#ef4444"
                strokeDasharray="5 5"
                strokeWidth={1.5}
                opacity={0.6}
              />
            ))}

            {/* Moving Averages */}
            {data[0]?.sma_9 && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma_9"
                stroke="#3b82f6"
                strokeWidth={1.5}
                dot={false}
                name="SMA(9)"
              />
            )}
            {data[0]?.sma_50 && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma_50"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
                name="SMA(50)"
              />
            )}
            {data[0]?.sma_200 && (
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="sma_200"
                stroke="#8b5cf6"
                strokeWidth={1.5}
                dot={false}
                name="SMA(200)"
              />
            )}

            {/* Bollinger Bands */}
            {data[0]?.upper_bb && data[0]?.lower_bb && (
              <>
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="upper_bb"
                  stroke="#6366f1"
                  strokeWidth={1}
                  fill="#6366f1"
                  fillOpacity={0.1}
                  dot={false}
                  name="BB Upper"
                />
                <Area
                  yAxisId="price"
                  type="monotone"
                  dataKey="lower_bb"
                  stroke="#6366f1"
                  strokeWidth={1}
                  fill="#6366f1"
                  fillOpacity={0.1}
                  dot={false}
                  name="BB Lower"
                />
              </>
            )}

            {/* Candlesticks - rendered as custom shapes */}
            <Bar
              yAxisId="price"
              dataKey="high"
              shape={<Candlestick />}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Chart */}
      <div className="w-full h-24 border border-border bg-background/50">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={data}
            margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
              stroke="hsl(var(--border))"
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis
              tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
              stroke="hsl(var(--border))"
              width={45}
              tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
            />
            <Tooltip
              formatter={(value: number) => [(value / 1000000).toFixed(2) + "M", "Volume"]}
              labelFormatter={(label) => `Date: ${label}`}
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                fontSize: "10px",
                fontFamily: "monospace",
              }}
            />
            <Bar
              dataKey="volume"
              fill="hsl(var(--muted-foreground))"
              opacity={0.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* RSI Indicator */}
      {data[0]?.rsi && (
        <div className="w-full h-20 border border-border bg-background/50">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
                stroke="hsl(var(--border))"
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 9, fill: "hsl(var(--muted-foreground))" }}
                stroke="hsl(var(--border))"
                width={30}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--background))",
                  border: "1px solid hsl(var(--border))",
                  fontSize: "10px",
                  fontFamily: "monospace",
                }}
              />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" opacity={0.5} />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" opacity={0.5} />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#a855f7"
                strokeWidth={2}
                dot={false}
                name="RSI"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-4 justify-center text-[9px] font-mono text-muted-foreground pt-2 border-t border-border">
        <div className="flex items-center gap-1">
          <div className="w-3 h-2 bg-terminal-green"></div>
          <span>Bullish</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-2 bg-swiss-red"></div>
          <span>Bearish</span>
        </div>
        {data[0]?.sma_9 && (
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span>SMA(9)</span>
          </div>
        )}
        {data[0]?.sma_50 && (
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-amber-500"></div>
            <span>SMA(50)</span>
          </div>
        )}
        {data[0]?.sma_200 && (
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-violet-500"></div>
            <span>SMA(200)</span>
          </div>
        )}
        {supportLevels.length > 0 && (
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 border-t-2 border-dashed border-terminal-green"></div>
            <span>Support</span>
          </div>
        )}
        {resistanceLevels.length > 0 && (
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 border-t-2 border-dashed border-swiss-red"></div>
            <span>Resistance</span>
          </div>
        )}
      </div>
    </div>
  );
}
