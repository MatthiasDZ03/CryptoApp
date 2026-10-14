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

    // READ (alle): GET /api/v1/accounts
    [HttpGet]
    public async Task<ActionResult<List<Account>>> GetAll()
    {
        return await _db.Accounts.ToListAsync();
    }

    // READ (eines): GET /api/v1/accounts/{id}
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

    // HIER kommen in 6.2 bis 6.4 weitere Methoden dazu
}