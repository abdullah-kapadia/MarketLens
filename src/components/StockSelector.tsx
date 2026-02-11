import { useState, useCallback, useEffect } from "react";
import { listStocks } from "@/lib/api";
import { FALLBACK_STOCKS } from "@/lib/fallback-data";
import type { Stock } from "@/lib/api-types";

interface StockSelectorProps {
  selected: string;
  onSelect: (ticker: string) => void;
  disabled?: boolean;
}

export function StockSelector({ selected, onSelect, disabled }: StockSelectorProps) {
  const [open, setOpen] = useState(false);
  const [stocks, setStocks] = useState<Stock[]>(FALLBACK_STOCKS.stocks);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await listStocks();
        setStocks(response.stocks);
      } catch (error) {
        console.warn("Failed to fetch stocks from API, using fallback data:", error);
        setStocks(FALLBACK_STOCKS.stocks);
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  const selectedStock = stocks.find((s) => s.ticker === selected);

  const handleSelect = useCallback(
    (ticker: string) => {
      onSelect(ticker);
      setOpen(false);
    },
    [onSelect]
  );

  return (
    <div className="space-y-2">
      <label className="label-mono block">Ticker</label>
      <div className="relative">
        <button
          type="button"
          disabled={disabled || loading}
          onClick={() => setOpen(!open)}
          className="w-full border border-border bg-background px-4 py-3 text-left font-mono text-sm 
                     shadow-[4px_4px_0px_hsl(var(--ink)/0.15)] 
                     hover:shadow-[2px_2px_0px_hsl(var(--ink)/0.15)] 
                     active:shadow-none active:translate-x-[2px] active:translate-y-[2px]
                     transition-all duration-75
                     disabled:opacity-50 disabled:cursor-not-allowed
                     brutalist-focus"
        >
          <div className="flex items-center justify-between">
            <span className="font-bold tracking-wider">
              {loading ? "LOADING..." : selectedStock ? selectedStock.ticker : "SELECT TICKER"}
            </span>
            <span className="text-muted-foreground text-xs">
              {selectedStock ? `$${selectedStock.current_price.toFixed(2)}` : "—"}
            </span>
          </div>
          {selectedStock && (
            <div className="mt-1 text-xs text-muted-foreground">{selectedStock.name}</div>
          )}
        </button>

        {open && (
          <div className="absolute z-50 mt-1 w-full border border-border bg-background shadow-[4px_4px_0px_hsl(var(--ink)/0.2)]">
            {stocks.map((stock) => {
              const changeSign = stock.change_percent >= 0 ? "+" : "";
              const changeStr = `${changeSign}${stock.change_percent.toFixed(2)}%`;
              
              return (
                <button
                  key={stock.ticker}
                  type="button"
                  onClick={() => handleSelect(stock.ticker)}
                  className={`w-full px-4 py-2.5 text-left font-mono text-sm border-b border-border last:border-b-0
                             hover:bg-muted transition-colors duration-75
                             ${stock.ticker === selected ? "bg-muted font-bold" : ""}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold tracking-wider">{stock.ticker}</span>
                    <span className={stock.change_percent >= 0 ? "text-terminal-green" : "text-swiss-red"}>
                      {changeStr}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">{stock.name}</div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
