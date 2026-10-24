using AccountService.Data;
using AccountService.Dtos;
using AccountService.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace AccountService.Controllers;

[ApiController]
[Route("api/v1/accounts")]
public class AccountsController : ControllerBase
{
    private const int MinimumAge = 18;

    private readonly AccountDbContext _db;

    public AccountsController(AccountDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<ActionResult<List<Account>>> GetAll()
    {
        return await _db.Accounts.ToListAsync();
    }

    
    [HttpGet("{id:guid}")]
    public async Task<ActionResult<Account>> GetById(Guid id)
    {
        var account = await _db.Accounts.FindAsync(id);
        if (account == null)
        {
            return NotFound();
        }
        return account;
    }

    [HttpPost]
    public async Task<ActionResult<Account>> Create(CreateAccountRequest request)
    {
        if (CalculateAge(request.BirthDate!.Value) < MinimumAge)
        {
            ModelState.AddModelError(nameof(request.BirthDate),
                $"Kunde muss mindestens {MinimumAge} Jahre alt sein.");
            return ValidationProblem(ModelState);
        }

        var email = request.Email.Trim().ToLowerInvariant();
        if (await _db.Accounts.AnyAsync(a => a.Email == email))
        {
            return Problem(detail: "E-Mail wird bereits verwendet.",
                statusCode: StatusCodes.Status409Conflict);
        }

        var account = new Account
        {
            
            Id = Guid.NewGuid(),
            FirstName = request.FirstName,
            LastName = request.LastName,
            Email = email,
            PhoneNumber = request.PhoneNumber,
            BirthDate = request.BirthDate.Value,
            TaxNumber = request.TaxNumber,
            Citizenship = request.Citizenship
        };

        _db.Accounts.Add(account);
        await _db.SaveChangesAsync();

        return CreatedAtAction(nameof(GetById), new { id = account.Id }, account);
    }

    private static int CalculateAge(DateOnly birthDate)
    {
        var today = DateOnly.FromDateTime(DateTime.Today);
        var age = today.Year - birthDate.Year; 
        if (birthDate > today.AddYears(-age))
        {
            age--;
        }
        return age;
    }

    // UPDATE: PUT /api/v1/accounts/{id}
    [HttpPut("{id:guid}")]
    public async Task<ActionResult<Account>> Update(Guid id, UpdateAccountRequest request)
    {
        var account = await _db.Accounts.FindAsync(id);
        if (account == null)
        {
            return NotFound();
        }

        var email = request.Email.Trim().ToLowerInvariant();
        if (await _db.Accounts.AnyAsync(a => a.Email == email && a.Id != id))
        {
            return Problem(detail: "E-Mail wird bereits verwendet.",
                statusCode: StatusCodes.Status409Conflict);
        }

        account.FirstName = request.FirstName;
        account.LastName = request.LastName;
        account.Email = email;
        account.PhoneNumber = request.PhoneNumber;
        account.KycStatus = request.KycStatus;
        account.Status = request.Status;

        await _db.SaveChangesAsync();
        return account;
    }

    // DELETE: DELETE /api/v1/accounts/{id}
    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var account = await _db.Accounts.FindAsync(id);
        if (account == null)
        {
            return NotFound();
        }

        if (account.Balance != 0)
        {
            return Problem(detail: "Konto kann nur mit Guthaben 0 gelöscht werden.",
                statusCode: StatusCodes.Status409Conflict);
        }

        _db.Accounts.Remove(account);
        await _db.SaveChangesAsync();
        return NoContent();
    }

    // HIER kommen in Schritt 7 Deposit und Withdraw dazu
}