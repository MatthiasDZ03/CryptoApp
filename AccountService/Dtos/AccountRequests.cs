using System.ComponentModel.DataAnnotations;
using AccountService.Models;

namespace AccountService.Dtos;

public class CreateAccountRequest
{
    [Required, StringLength(50)]
    public string FirstName { get; set; } = "";

    [Required, StringLength(50)]
    public string LastName { get; set; } = "";

    [Required, EmailAddress]
    public string Email { get; set; } = "";

    [Required, RegularExpression(@"^\+[1-9]\d{6,14}$",
        ErrorMessage = "Telefonnummer im E.164-Format, z. B. +436601234567")]
    public string PhoneNumber { get; set; } = "";

    [Required]
    public DateOnly? BirthDate { get; set; }

    [Required, RegularExpression(@"^\d{9}$",
        ErrorMessage = "Steuernummer muss genau 9 Ziffern haben")]
    public string TaxNumber { get; set; } = "";

    [Required, RegularExpression("^[A-Z]{2}$",
        ErrorMessage = "ISO-3166 Ländercode mit 2 Großbuchstaben, z. B. AT")]
    public string Citizenship { get; set; } = "";
}

public class UpdateAccountRequest
{
    [Required, StringLength(50)]
    public string FirstName { get; set; } = "";

    [Required, StringLength(50)]
    public string LastName { get; set; } = "";

    [Required, EmailAddress]
    public string Email { get; set; } = "";

    [Required, RegularExpression(@"^\+[1-9]\d{6,14}$",
        ErrorMessage = "Telefonnummer im E.164-Format, z. B. +436601234567")]
    public string PhoneNumber { get; set; } = "";

    public KycStatus KycStatus { get; set; }

    public AccountStatus Status { get; set; }
}

public class AmountRequest
{
    [Range(0.01, 1_000_000)]
    public decimal Amount { get; set; }
}

public class BuyingPowerResponse
{
    public Guid AccountId { get; set; }
    public string Symbol { get; set; } = "";
    public decimal PriceEur { get; set; }
    public decimal BalanceEur { get; set; }
    public decimal Quantity { get; set; }
}