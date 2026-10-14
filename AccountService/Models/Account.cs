namespace AccountService.Models;

public enum KycStatus
{
    Pending,
    Verified,
    Rejected
}

public enum AccountStatus
{
    Active,
    Suspended,
    Closed
}

public class Account
{
    public Guid Id { get; set; }
    public string FirstName { get; set; } = "";
    public string LastName { get; set; } = "";
    public string Email { get; set; } = "";
    public string PhoneNumber { get; set; } = "";
    public DateOnly BirthDate { get; set; }
    public string TaxNumber { get; set; } = "";
    public string Citizenship { get; set; } = "";
    public KycStatus KycStatus { get; set; } = KycStatus.Pending;
    public AccountStatus Status { get; set; } = AccountStatus.Active;
    public decimal Balance { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}