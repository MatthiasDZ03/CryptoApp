namespace AccountService.Services;

public interface IPriceService
{
    // Aktueller Preis in EUR, oder null wenn der Coin unbekannt ist
    Task<decimal?> GetPriceEurAsync(string symbol);
}
