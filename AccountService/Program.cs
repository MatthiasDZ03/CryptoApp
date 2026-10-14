using System.Text.Json.Serialization;
using AccountService.Settings;
using AccountService.Services;

using AccountService.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ---------- API-Kern (Mo) ----------
builder.Services.AddControllers()
    .AddJsonOptions(options =>
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));
builder.Services.AddSwaggerGen();
builder.Services.AddDbContext<AccountDbContext>(options =>
    options.UseInMemoryDatabase("AccountDb"));

// -------- Infrastruktur (Matthias) ----------
builder.Services.Configure<MarketSettings>(builder.Configuration.GetSection("Market"));
builder.Services.Configure<ApiKeySettings>(builder.Configuration.GetSection("ApiKey"));


var app = builder.Build();


if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();