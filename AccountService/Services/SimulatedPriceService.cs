using AccountService.Settings;
using Microsoft.Extensions.Options;

namespace AccountService.Services;

public class SimulatedPriceService : IPriceService
{
    private readonly MarketSettings _settings;

    public SimulatedPriceService(IOptions<MarketSettings> options)
    {
        _settings = options.Value;
    }

    public Task<decimal?> GetPriceEurAsync(string symbol)
    {
        if (!_settings.SimulatedPricesEur.TryGetValue(symbol.ToUpperInvariant(), out var basePrice))
        {
            return Task.FromResult<decimal?>(null);
        }

        // +/- 2 % Zufallsschwankungen, damit es wie ein echter Market aussieht
        var factor = 1 + (decimal)(Random.Shared.NextDouble() * 0.04 - 0.02);
        return Task.FromResult<decimal?>(Math.Round(basePrice * factor, 2));    
    }
}