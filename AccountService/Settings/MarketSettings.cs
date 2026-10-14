namespace AccountService.Settings;

public class MarketSettings
{
    public string Provider { get; set; } = "Simulated";
    public string CoinGeckoBaseUrl { get; set; } = "";
    public Dictionary<string, string> CoinGeckoIds { get; set; } = new();
    public Dictionary<string, decimal> SimulatedPricesEur { get; set; } = new();
}